import os
import gemini_patch  # noqa: F401  -- strips `strict` from tools for Gemini compat; must import before building agents
from primisai.nexus.core import Agent, Supervisor
from eda_tools import iverilog_tool

llm_config = {
    "api_key": os.environ.get("GOOGLE_API_KEY", ""),
    "model": "gemini-2.5-flash",
    "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
}

# (B) Local, fully offline (privacy-preserving angle from the JD) -- needs `ollama serve`
# llm_config = {
#     "api_key": "ollama",                      # any non-empty string
#     "model": "qwen2.5-coder:7b",
#     "base_url": "http://localhost:11434/v1",
# }

# (C) OpenAI
# llm_config = {
#     "api_key": os.environ.get("OPENAI_API_KEY", ""),
#     "model": "gpt-4o",
#     "base_url": "https://api.openai.com/v1",
# }

SPEC = """\
Implement a Verilog module named `alu` with this exact interface:

    module alu(input [7:0] a, b, input [1:0] op, output reg [7:0] y);

Behavior (combinational):
    op = 2'b00 : y = a + b      (ADD)
    op = 2'b01 : y = a - b      (SUB)
    op = 2'b10 : y = a | b      (OR)
    op = 2'b11 : y = a & b      (AND)

After writing the module, call run_iverilog(design_code=<your full module>) to
verify it against the golden testbench. If it does not PASS, read the failing
vectors, fix the RTL, and verify again. Repeat until you get PASS. When it
passes, reply with the final Verilog and a one-line summary.
"""


def main():
    if not llm_config["api_key"]:
        raise SystemExit(
            "No API key set. Export GOOGLE_API_KEY (or switch to the Ollama block "
            "for fully offline runs)."
        )

    supervisor = Supervisor(
        "DesignManager",
        llm_config,
        system_message=(
            "You manage a hardware design workflow. Delegate RTL design and "
            "verification to RTLEngineer and report the final verified result."
        ),
    )

    rtl_engineer = Agent(
        "RTLEngineer",
        llm_config,
        tools=[iverilog_tool],
        use_tools=True,
        system_message=(
            "You are a Verilog design engineer. You write synthesizable RTL and "
            "verify it using the run_iverilog tool. You NEVER edit the testbench; "
            "you only change the design. Keep iterating until the tool reports PASS."
        ),
    )

    supervisor.register_agent(rtl_engineer)
    supervisor.display_agent_graph()

    # The supervisor delegates to RTLEngineer, whose internal loop calls the
    # iverilog tool, reads failures, and fixes the design automatically.
    result = supervisor.chat(SPEC)
    print("\n=== FINAL RESULT ===\n")
    print(result)


if __name__ == "__main__":
    main()
