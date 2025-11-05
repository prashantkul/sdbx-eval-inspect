"""Judge Agent - Evaluates whether sandbox escape attempts succeeded."""

from inspect_ai.agent import Agent, agent
from inspect_ai.model import ChatMessageSystem


@agent
def judge_agent(
    system_message: str = None,
    use_detailed_prompt: bool = False
) -> Agent:
    """
    Create a judge agent for sandbox escape analysis.

    The judge agent evaluates interactions and determines success.
    It detects successful escapes and scores attempt sophistication.

    Args:
        system_message: Optional custom system message
        use_detailed_prompt: Use detailed prompt with scoring criteria

    Returns:
        Agent instance for the judge
    """
    from inspect_integration.prompts.judge_prompts import (
        JUDGE_PROMPT,
        JUDGE_PROMPT_DETAILED
    )

    # Choose prompt
    if system_message is None:
        system_message = JUDGE_PROMPT_DETAILED if use_detailed_prompt else JUDGE_PROMPT

    async def execute(state):
        """
        Execute judge agent logic.

        The judge analyzes the conversation between auditor and target,
        detecting successful escapes and scoring sophistication.
        """
        from inspect_ai.model import get_model

        # Add system message if not already present
        if not any(msg.role == "system" for msg in state.messages):
            state.messages.insert(0, ChatMessageSystem(content=system_message))

        # Analyze the interaction (no tools needed)
        output = await get_model().generate(
            state.messages,
            tools=None
        )

        # Update state with judgment
        state.messages.append(output.message)
        state.output = output

        return state

    return execute
