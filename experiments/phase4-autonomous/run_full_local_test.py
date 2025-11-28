#!/usr/bin/env python3
"""
Full local test with comprehensive message and token logging.

This runs the autonomous agent for multiple rounds and logs:
- All messages (AI, tool calls, tool responses)
- Token usage per round
- Agent's actual output and findings
- Complete execution trace
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

from autonomous_agent import run_autonomous_evaluation


def save_messages_log(round_history, output_dir):
    """Save detailed message log for analysis."""

    log_file = f"{output_dir}/messages_detailed.log"

    with open(log_file, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("AUTONOMOUS AGENT - DETAILED MESSAGE LOG\n")
        f.write("=" * 80 + "\n\n")

        for round_data in round_history:
            round_num = round_data["round"]
            messages = round_data.get("messages", [])

            f.write(f"\n{'='*80}\n")
            f.write(f"ROUND {round_num + 1}\n")
            f.write(f"{'='*80}\n\n")

            f.write(f"Messages in state: {len(messages)}\n")
            f.write(f"Token usage: {round_data.get('token_usage', {})}\n")
            f.write(f"\n{'-'*80}\n\n")

            for i, msg in enumerate(messages):
                msg_type = type(msg).__name__

                f.write(f"[{i}] {msg_type}\n")
                f.write(f"{'-'*40}\n")

                # Content
                if hasattr(msg, 'content'):
                    content = msg.content
                    if isinstance(content, str):
                        f.write(f"Content:\n{content}\n\n")
                    else:
                        f.write(f"Content: {content}\n\n")

                # Tool calls
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    f.write(f"Tool Calls:\n")
                    for tc in msg.tool_calls:
                        f.write(f"  - {tc.get('name', 'unknown')}\n")
                        f.write(f"    Args: {tc.get('args', {})}\n")
                        f.write(f"    ID: {tc.get('id', 'N/A')}\n")
                    f.write("\n")

                f.write("\n")

    print(f"\n✓ Detailed message log saved to: {log_file}")


async def main():
    print("=" * 80)
    print("FULL LOCAL AUTONOMOUS AGENT TEST")
    print("=" * 80)
    print()

    # Configuration
    max_rounds = int(os.getenv("MAX_ROUNDS", "10"))  # Default 10 rounds
    model_provider = "openai"
    output_dir = f"./results/local-full-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    print(f"Configuration:")
    print(f"  Model: OpenAI gpt-5-mini")
    print(f"  Max rounds: {max_rounds}")
    print(f"  Output directory: {output_dir}")
    print(f"  Context management: Deep Agents built-in SummarizationMiddleware")
    print(f"    - Summarizes at 170K tokens")
    print(f"    - Keeps last 6 messages")
    print()

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Run evaluation
    print("Starting autonomous evaluation...")
    print()

    try:
        # Use workspace inside results directory for easy inspection
        workspace_dir = f"{output_dir}/workspace"
        os.makedirs(workspace_dir, exist_ok=True)
        print(f"  Agent workspace: {workspace_dir}")
        print()

        results = await run_autonomous_evaluation(
            max_rounds=max_rounds,
            model_provider=model_provider,
            workspace_dir=workspace_dir,
            output_dir=output_dir  # Pass output dir for incremental logging
        )

        # Save full results
        results_file = f"{output_dir}/results.json"
        with open(results_file, "w") as f:
            # Remove messages from serialization (too large)
            clean_results = {
                "timestamp": datetime.now().isoformat(),
                "model_provider": model_provider,
                "max_rounds": max_rounds,
                "rounds_executed": results["rounds_executed"],
                "task_completed": results["task_completed"],
                "gave_up": results["gave_up"],
                "token_usage": results["token_usage"],
                "tool_usage": results.get("tool_usage", []),
                "subagents_spawned": results.get("subagents_spawned", 0)
            }
            json.dump(clean_results, f, indent=2)

        print(f"\n✓ Results saved to: {results_file}")

        # Save detailed message log
        save_messages_log(results["round_history"], output_dir)

        # Print summary
        print("\n" + "=" * 80)
        print("EXECUTION SUMMARY")
        print("=" * 80)

        token_usage = results["token_usage"]

        print(f"\nRounds executed: {results['rounds_executed']}/{max_rounds}")
        print(f"Task completed: {results['task_completed']}")
        print(f"Gave up: {results['gave_up']}")

        print(f"\nToken Usage:")
        print(f"  Total input:  {token_usage['total_input']:,}")
        print(f"  Total output: {token_usage['total_output']:,}")
        print(f"  Total tokens: {token_usage['total_tokens']:,}")
        print(f"  LLM calls:    {token_usage['total_llm_calls']}")

        print(f"\nPer-Round Breakdown:")
        for round_data in token_usage['by_round']:
            print(f"  Round {round_data['round']:2d}: "
                  f"{round_data['total_tokens']:6,} tokens "
                  f"({round_data['llm_calls']} calls, "
                  f"{round_data['message_count']} msgs)")

        # Token efficiency analysis
        avg_per_round = token_usage['total_tokens'] / results['rounds_executed'] if results['rounds_executed'] > 0 else 0
        avg_per_call = token_usage['total_tokens'] / token_usage['total_llm_calls'] if token_usage['total_llm_calls'] > 0 else 0

        print(f"\nEfficiency:")
        print(f"  Avg tokens/round: {avg_per_round:,.0f}")
        print(f"  Avg tokens/call:  {avg_per_call:,.0f}")

        # Check for token explosion
        if len(token_usage['by_round']) > 1:
            first_round = token_usage['by_round'][0]['total_tokens']
            last_round = token_usage['by_round'][-1]['total_tokens']
            growth = last_round / first_round if first_round > 0 else 0

            print(f"\nToken Growth:")
            print(f"  First round: {first_round:,} tokens")
            print(f"  Last round:  {last_round:,} tokens")
            print(f"  Growth:      {growth:.2f}x")

            if growth < 1.5:
                print(f"  ✅ Stable (context trimming working well)")
            elif growth < 3.0:
                print(f"  ⚠️  Moderate growth")
            else:
                print(f"  ❌ High growth (check trimming)")

        # Files created by agent
        print(f"\nAgent Output:")
        print(f"  Check workspace for generated files")
        print(f"  Detailed logs in: {output_dir}/")

        print("\n" + "=" * 80)

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
