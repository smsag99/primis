"""A Python-testing tool, packaged in Nexus's tool format.

This is the ONLY thing that differs from the EDA demo: there, the tool
compiled+simulated Verilog; here, it runs a Python solution against a fixed
golden test. The agent, supervisor, and loop stay identical.
"""
import os, subprocess

HERE      = os.path.dirname(__file__)
WORK_DIR  = os.path.join(HERE, "work")
TEST_PATH = os.path.join(HERE, "test_leap.py")

def _strip_fences(code: str) -> str:
    lines = [l for l in code.splitlines() if not l.strip().startswith("```")]
    return "\n".join(lines).strip()

def run_python_tests(solution_code: str) -> str:
    """Write the candidate solution, run the fixed golden test, return status."""
    os.makedirs(WORK_DIR, exist_ok=True)
    # the golden test does `from solution import is_leap_year`, so the
    # candidate code must live next to it as solution.py
    with open(os.path.join(WORK_DIR, "solution.py"), "w") as f:
        f.write(_strip_fences(solution_code))
    # copy the fixed test into the work dir so imports resolve
    with open(TEST_PATH) as src, open(os.path.join(WORK_DIR, "test_leap.py"), "w") as dst:
        dst.write(src.read())

    proc = subprocess.run(
        ["python", "test_leap.py"],
        cwd=WORK_DIR, capture_output=True, text=True, timeout=30,
    )
    log = (proc.stdout or "") + (proc.stderr or "")
    if "ALL_TESTS_PASSED" in log:
        return "PASS: all tests passed.\n" + log
    if proc.returncode != 0 and "TESTS_FAILED" not in log:
        return "RUNTIME_ERROR:\n" + log        # e.g. syntax error / crash
    return "TEST_FAIL:\n" + log                 # ran, but wrong answers

run_python_tool = {
    "metadata": {
        "type": "function",
        "function": {
            "name": "run_python_tests",
            "description": (
                "Run the given Python solution (which must define is_leap_year(year)) "
                "against the fixed golden test. Returns RUNTIME_ERROR, TEST_FAIL (with "
                "which years were wrong), or PASS."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "solution_code": {
                        "type": "string",
                        "description": "Full Python source defining is_leap_year(year).",
                    }
                },
                "required": ["solution_code"],
            },
        },
    },
    "tool": run_python_tests,
}
