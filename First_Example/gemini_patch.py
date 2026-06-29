"""
Compatibility shim for running PrimisAI Nexus against Google Gemini's
OpenAI-compatible endpoint.

Nexus hardcodes `"strict": True` on its supervisor delegation tools
(supervisor.py). OpenAI accepts that field; Gemini's OpenAI-compat layer
rejects any unknown field in `tools[...]` with a 400. This patch wraps
AI.generate_response and strips `strict` from every outgoing tool schema,
without touching anything in site-packages.

Import this module BEFORE building any Supervisor/Agent:  import gemini_patch
"""
from primisai.nexus.core.ai import AI

_orig_generate_response = AI.generate_response

def _strip_strict(tools):
    if not tools:
        return tools
    cleaned = []
    for t in tools:
        t = dict(t)
        t.pop("strict", None)                 # top-level (supervisor tools)
        if isinstance(t.get("function"), dict):
            fn = dict(t["function"])
            fn.pop("strict", None)            # nested, just in case
            t["function"] = fn
        cleaned.append(t)
    return cleaned

def _patched_generate_response(self, messages, tools=None, use_tools=False):
    return _orig_generate_response(self, messages, _strip_strict(tools), use_tools)

AI.generate_response = _patched_generate_response
