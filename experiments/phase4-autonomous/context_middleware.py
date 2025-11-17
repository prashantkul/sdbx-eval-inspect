#!/usr/bin/env python3
"""
Context management middleware for Deep Agents.

Provides message trimming and summarization to prevent token explosion.
"""

from typing import Any, Dict, Optional
from langchain.agents import AgentState
from langchain.agents.middleware import before_model
from langgraph.runtime import Runtime
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES


# Configuration
MAX_MESSAGES_IN_CONTEXT = 20  # Keep last N messages
LARGE_OUTPUT_THRESHOLD = 3000  # Characters - trigger summarization


def find_safe_trim_point(messages: list, target_keep: int) -> int:
    """
    Find a safe point to trim messages without breaking tool call sequences.

    OpenAI requires tool messages to immediately follow AI messages with tool_calls.
    We need to ensure we don't trim in the middle of such sequences.

    Args:
        messages: List of messages
        target_keep: Target number of messages to keep

    Returns:
        Index to start keeping messages from (or 0 if can't find safe point)
    """
    if len(messages) <= target_keep:
        return 0

    # Start from target trim point
    trim_index = len(messages) - target_keep

    # Look backwards from trim point to find a safe boundary
    # A safe boundary is:
    # - Not a ToolMessage (could break sequence)
    # - Not an AIMessage with tool_calls (response would be orphaned)
    for i in range(trim_index, max(0, trim_index - 10), -1):
        if i == 0:
            return 0

        msg_type = type(messages[i]).__name__

        # If this is a ToolMessage, we can't trim here
        if msg_type == "ToolMessage":
            continue

        # If this is an AIMessage with tool_calls, we can't trim here
        if msg_type == "AIMessage" and hasattr(messages[i], 'tool_calls') and messages[i].tool_calls:
            continue

        # This is a safe trim point
        return i

    # If we couldn't find a safe point in last 10 messages, keep everything
    return 0


@before_model
def trim_messages_middleware(state: AgentState, runtime: Runtime) -> Optional[Dict[str, Any]]:
    """
    Trim message history to keep context window manageable.

    Keeps the first message (system prompt) and the last N messages,
    ensuring we don't break tool call/response sequences (required by OpenAI).

    Args:
        state: The agent state
        runtime: The LangGraph runtime

    Returns:
        State update with trimmed messages, or None if no trimming needed
    """
    messages = state.get("messages", [])

    # If we're under the limit, no trimming needed
    if len(messages) <= MAX_MESSAGES_IN_CONTEXT + 1:  # +1 for system message
        return None

    # Keep first message (system) separate
    first_msg = messages[0]
    rest_messages = messages[1:]

    # Find safe trim point that won't break tool sequences
    trim_index = find_safe_trim_point(rest_messages, MAX_MESSAGES_IN_CONTEXT)

    # Keep messages from safe trim point onwards
    recent_messages = rest_messages[trim_index:]

    # Create new message list
    new_messages = [first_msg] + recent_messages

    # Return state update that removes all and adds back the trimmed set
    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *new_messages
        ]
    }


def should_summarize_output(content: str) -> bool:
    """
    Determine if tool output should be summarized.

    Args:
        content: The tool output content

    Returns:
        True if output exceeds threshold
    """
    if not isinstance(content, str):
        return False

    return len(content) > LARGE_OUTPUT_THRESHOLD


def create_output_summary(content: str, tool_name: str = "tool") -> str:
    """
    Create a summary of large tool output.

    Shows first and last portions with statistics.

    Args:
        content: The full output
        tool_name: Name of the tool that produced output

    Returns:
        Summarized output
    """
    # Show first 1000 and last 500 chars
    first_chunk = content[:1000]
    last_chunk = content[-500:]

    line_count = content.count('\n')
    word_count = len(content.split())

    summary = f"""[{tool_name} output - {len(content):,} chars, {line_count:,} lines, {word_count:,} words]

=== FIRST 1000 CHARACTERS ===
{first_chunk}

... [{len(content) - 1500:,} characters omitted] ...

=== LAST 500 CHARACTERS ===
{last_chunk}

[TIP: Use write_file() to save full output for detailed analysis]
"""

    return summary


# Export middleware
# DISABLED: Message trimming causes issues with OpenAI tool call ordering
# Relying on output summarization instead (see custom_tools.py)
CONTEXT_MIDDLEWARE = []


if __name__ == "__main__":
    # Test summarization
    large_output = "Line " + "\n".join([f"Item {i}" for i in range(1000)])

    print("Testing summarization...")
    print(f"Original size: {len(large_output):,} chars")
    print(f"Should summarize: {should_summarize_output(large_output)}")

    summary = create_output_summary(large_output, "bash")
    print(f"\nSummary size: {len(summary):,} chars")
    print("\nSummary:")
    print(summary)
