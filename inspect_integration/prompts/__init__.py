"""Agent prompts for sandbox escape evaluation."""

from .auditor_prompts import AUDITOR_PROMPT, AUDITOR_PROMPT_DETAILED, get_auditor_prompt
from .target_prompts import TARGET_PROMPT, TARGET_PROMPT_DETAILED
from .judge_prompts import JUDGE_PROMPT, JUDGE_PROMPT_DETAILED

__all__ = [
    'AUDITOR_PROMPT',
    'AUDITOR_PROMPT_DETAILED',
    'get_auditor_prompt',
    'TARGET_PROMPT',
    'TARGET_PROMPT_DETAILED',
    'JUDGE_PROMPT',
    'JUDGE_PROMPT_DETAILED'
]
