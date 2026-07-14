import os
import gemini_patch  # noqa: F401  -- strips `strict` from tools for Gemini compat; must import before building agents
from primisai.nexus.core import Agent, Supervisor
from eda_tools import iverilog_tool

llm_config = {
    "api_key": os.environ.get("GOOGLE_API_KEY", ""),
    "model": "gemini-2.5-flash",
    "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
}


SPEC = """\
Implement a Verilog module named `alu` with this exact interface:

    module alu(input [7:0] a, b, input [1:0] op, output reg [7:0] y);


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

    result = supervisor.chat(SPEC)
    print("\n=== FINAL RESULT ===\n")
    print(result)


if __name__ == "__main__":
    main()
