#!/usr/bin/env python3
"""
Context management middleware for Deep Agents.

Uses LangChain's built-in SummarizationMiddleware for automatic context management.
"""

from langchain.agents.middleware import SummarizationMiddleware
from langchain_openai import ChatOpenAI
import os


# Configuration
MAX_TOKENS_BEFORE_SUMMARY = 20000  # Trigger summarization at 20K tokens
MESSAGES_TO_KEEP = 15  # Keep last 15 messages after summarization


def create_context_middleware():
    """
    Create LangChain's SummarizationMiddleware for automatic context management.

    This middleware:
    - Monitors message history token count
    - Automatically summarizes old messages when threshold is reached
    - Keeps recent messages intact for context
    - Uses gpt-4o-mini for cost-effective summarization

    Returns:
        SummarizationMiddleware instance
    """
    return SummarizationMiddleware(
        model=ChatOpenAI(
            model="gpt-4o-mini",  # Cheaper model for summarization
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.3  # Lower temp for factual summaries
        ),
        max_tokens_before_summary=MAX_TOKENS_BEFORE_SUMMARY,
        messages_to_keep=MESSAGES_TO_KEEP
    )


# Export function to create middleware (not instance) to avoid duplicates
def get_context_middleware():
    """
    Get a fresh middleware list with SummarizationMiddleware.

    Creates a new instance each time to avoid duplicate middleware errors.
    LangChain checks that all middleware have unique names - creating at module
    level would cause "duplicate middleware" errors.

    Returns:
        List with fresh SummarizationMiddleware instance
    """
    return [create_context_middleware()]

# For backward compatibility - but this creates instance at import time
# which can cause duplicate errors. Use get_context_middleware() instead.
# DISABLED: Not using middleware anymore (Deep Agents handles context management)
# CONTEXT_MIDDLEWARE = get_context_middleware()


if __name__ == "__main__":
    # Test that middleware can be created
    print("Testing SummarizationMiddleware creation...")
    middleware = create_context_middleware()
    print(f"✓ Created SummarizationMiddleware")
    print(f"  Max tokens before summary: {MAX_TOKENS_BEFORE_SUMMARY:,}")
    print(f"  Messages to keep: {MESSAGES_TO_KEEP}")
    print(f"  Model: gpt-4o-mini")
