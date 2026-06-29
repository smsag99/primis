


import os
import gemini_patch  # noqa: F401  -- Gemini compatibility shim; import before building agents
from primisai.nexus.core import Agent, Supervisor
from py_tools import run_python_tool          # <-- the only swapped import

llm_config = {
    "api_key": os.environ.get("GOOGLE_API_KEY", ""),
    "model": "gemini-2.5-flash",
    "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
}

SPEC = """\
Write a Python function with this exact signature:

    def is_leap_year(year):

It must return True if `year` is a leap year and False otherwise, using the full
Gregorian rule: a year is a leap year if it is divisible by 4, EXCEPT century
years (divisible by 100), which are leap years only if also divisible by 400.

After writing it, call run_python_tests(solution_code=<your full code>) to verify
against the golden test. If it does not PASS, read which years were wrong, fix the
function, and verify again. Repeat until you get PASS, then reply with the final code.
"""


def main():
    if not llm_config["api_key"]:
        raise SystemExit("Set GOOGLE_API_KEY (or switch main.py to the Ollama block).")

    supervisor = Supervisor(
        "DevManager",
        llm_config,
        system_message="You manage a coding task. Delegate to PyDev and report the verified result.",
    )

    pydev = Agent(
        "PyDev",
        llm_config,
        tools=[run_python_tool],            # <-- the only swapped tool
        use_tools=True,
        system_message=(
            "You are a Python engineer. You write a function and verify it with the "
            "run_python_tests tool. You NEVER edit the test; you only change your code. "
            "Keep iterating until the tool reports PASS."
        ),
    )

    supervisor.register_agent(pydev)
    supervisor.display_agent_graph()

    result = supervisor.chat(SPEC)
    print("\n=== FINAL RESULT ===\n")
    print(result)


if __name__ == "__main__":
    main()
