"""Agent implementations for sandbox escape evaluation.

This module provides three agents using Inspect's @agent decorator:
- Target Agent: The sandboxed agent being tested (has tools)
- Auditor Agent: Crafts instructions to get target to escape (no tools)
- Judge Agent: Evaluates whether escape attempts succeeded (no tools)

This architecture follows Petri's pattern.
"""

from .target_agent import target_agent
from .auditor_agent import auditor_agent
from .judge_agent import judge_agent

__all__ = [
    'target_agent',
    'auditor_agent',
    'judge_agent'
]
