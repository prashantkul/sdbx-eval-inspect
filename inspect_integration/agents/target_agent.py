"""Target Agent - Sandboxed agent that executes commands with tools."""

from inspect_ai.agent import Agent, agent
from inspect_ai.model import ChatMessageSystem
from typing import Optional


@agent
def target_agent(
    system_message: str = None,
    use_detailed_prompt: bool = False,
    mcp_server_url: Optional[str] = None
) -> Agent:
    """
    Create a target agent for sandbox testing.

    The target agent HAS tools - it executes commands.
    It's the subject being tested for escape vulnerabilities.

    Args:
        system_message: Optional custom system message
        use_detailed_prompt: Use detailed prompt
        mcp_server_url: Optional MCP server URL for tools

    Returns:
        Agent instance for the target
    """
    from inspect_integration.prompts.target_prompts import (
        TARGET_PROMPT,
        TARGET_PROMPT_DETAILED
    )
    from inspect_integration.solvers.tools import get_target_tools

    # Choose prompt
    if system_message is None:
        system_message = TARGET_PROMPT_DETAILED if use_detailed_prompt else TARGET_PROMPT

    # Get tools for this agent
    tools = get_target_tools(mcp_server_url)

    async def execute(state):
        """
        Execute target agent logic.

        The target executes commands using available tools.
        It should faithfully execute instructions (for testing).
        """
        from inspect_ai.model import get_model

        # Add system message if not already present
        if not any(msg.role == "system" for msg in state.messages):
            state.messages.insert(0, ChatMessageSystem(content=system_message))

        # Execute with tools available
        # Note: Using generate_loop would be better for multi-turn tool usage
        # but for single-turn execution, generate with tools works
        output = await get_model().generate(
            state.messages,
            tools=tools
        )

        # Update state with execution results
        state.messages.append(output.message)
        state.output = output

        return state

    return execute
