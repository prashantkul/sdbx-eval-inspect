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


@before_model
def trim_messages_middleware(state: AgentState, runtime: Runtime) -> Optional[Dict[str, Any]]:
    """
    Trim message history to keep context window manageable.

    Keeps the first message (system prompt) and the last N messages.

    Args:
        state: The agent state
        runtime: The LangGraph runtime

    Returns:
        State update with trimmed messages, or None if no trimming needed
    """
    messages = state.get("messages", [])

    # If we're under the limit, no trimming needed
    if len(messages) <= MAX_MESSAGES_IN_CONTEXT:
        return None

    # Keep first message (system) and last N messages
    first_msg = messages[0]
    recent_messages = messages[-MAX_MESSAGES_IN_CONTEXT:]

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
CONTEXT_MIDDLEWARE = [trim_messages_middleware]


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
