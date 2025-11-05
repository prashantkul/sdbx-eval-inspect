"""UK AISI Inspect Framework Integration for Sandbox Escape Evaluation.

This module provides Inspect-native agents for sandbox escape evaluation.
"""

from .tasks_native import sandbox_escape_native, sandbox_escape_from_dataset
from .scorers import (
    escape_success_scorer,
    sophistication_scorer,
    stealth_scorer,
    safety_violations_scorer,
    combined_scorer,
    technique_accuracy_scorer
)
from .solvers import coordinated_agent_solver
from .sandboxes import get_sandbox_environment
from .agents import target_agent, auditor_agent, judge_agent

__all__ = [
    # Tasks
    'sandbox_escape_native',
    'sandbox_escape_from_dataset',
    # Agents
    'target_agent',
    'auditor_agent',
    'judge_agent',
    # Scorers
    'escape_success_scorer',
    'sophistication_scorer',
    'stealth_scorer',
    'safety_violations_scorer',
    'combined_scorer',
    'technique_accuracy_scorer',
    # Solver
    'coordinated_agent_solver',
    # Sandbox
    'get_sandbox_environment'
]
