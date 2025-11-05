"""Auditor Agent - Agent that attempts to get the target to perform actions."""

from inspect_ai.agent import Agent, agent
from inspect_ai.model import ChatMessageSystem


@agent
def auditor_agent(
    system_message: str = None,
    use_detailed_prompt: bool = False
) -> Agent:
    """
    Create an auditor agent for sandbox escape testing.

    The auditor agent has NO tools - it's pure reasoning.
    It crafts instructions to get the target to escape the sandbox.
    Similar to Petri's auditor agent.

    Args:
        system_message: Optional custom system message
        use_detailed_prompt: Use detailed prompt with techniques library

    Returns:
        Agent instance for the auditor
    """
    from inspect_integration.prompts.auditor_prompts import (
        AUDITOR_PROMPT,
        AUDITOR_PROMPT_DETAILED
    )

    # Choose prompt
    if system_message is None:
        system_message = AUDITOR_PROMPT_DETAILED if use_detailed_prompt else AUDITOR_PROMPT

    async def execute(state):
        """
        Execute auditor agent logic.

        The auditor crafts instructions without using tools.
        It reasons about bypass techniques and creates prompts for the target.
        """
        from inspect_ai.model import get_model

        # Add system message if not already present
        if not any(msg.role == "system" for msg in state.messages):
            state.messages.insert(0, ChatMessageSystem(content=system_message))

        # Generate instruction for the target (no tools)
        output = await get_model().generate(
            state.messages,
            tools=None  # Auditor has no tools - pure reasoning
        )

        # Update state with the instruction
        state.messages.append(output.message)
        state.output = output

        return state

    return execute
