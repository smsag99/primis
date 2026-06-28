import os, subprocess, tempfile, textwrap

WORK_DIR = os.path.join(os.path.dirname(__file__), "work")
TB_PATH  = os.path.join(os.path.dirname(__file__), "tb_alu.v")

def _strip_fences(code: str) -> str:
    # Models sometimes wrap RTL in ```verilog fences; remove them defensively.
    lines = [l for l in code.splitlines() if not l.strip().startswith("```")]
    return "\n".join(lines).strip()

def run_iverilog(design_code: str) -> str:
    """Compile candidate RTL against the fixed golden testbench and simulate.

    Returns a human-readable status string the agent can read and react to.
    """
    os.makedirs(WORK_DIR, exist_ok=True)
    design_code = _strip_fences(design_code)
    design_path = os.path.join(WORK_DIR, "alu.v")
    out_path    = os.path.join(WORK_DIR, "sim.out")
    with open(design_path, "w") as f:
        f.write(design_code)

    # 1) Compile
    comp = subprocess.run(
        ["iverilog", "-g2012", "-o", out_path, design_path, TB_PATH],
        capture_output=True, text=True, timeout=30,
    )
    if comp.returncode != 0:
        return "COMPILE_ERROR:\n" + (comp.stderr or comp.stdout)

    # 2) Simulate
    sim = subprocess.run(["vvp", out_path], capture_output=True, text=True, timeout=30)
    log = (sim.stdout or "") + (sim.stderr or "")
    if "ALL_TESTS_PASSED" in log:
        return "PASS: all tests passed.\n" + log
    return "SIM_FAIL:\n" + log

# Nexus tool registration (OpenAI function-calling format, per v0.8.1)
iverilog_tool = {
    "metadata": {
        "type": "function",
        "function": {
            "name": "run_iverilog",
            "description": (
                "Compile the given Verilog module 'alu' against the fixed golden "
                "testbench and simulate it. Use this to check whether your RTL is "
                "correct. Returns COMPILE_ERROR, SIM_FAIL (with which vectors failed), "
                "or PASS."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "design_code": {
                        "type": "string",
                        "description": "Full Verilog source for module 'alu'.",
                    }
                },
                "required": ["design_code"],
            },
        },
    },
    "tool": run_iverilog,
}
