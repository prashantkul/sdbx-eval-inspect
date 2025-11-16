#!/usr/bin/env python3
"""
Orchestrator for Phase 4 autonomous agent sandbox escape evaluation.

This script:
1. Starts containers (proxy + agent)
2. Runs autonomous agent with Deep Agents
3. Monitors and classifies behavior in real-time
4. Generates comprehensive evaluation results
"""

import asyncio
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import docker
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from behavior_classifier import BehaviorClassifier, BehaviorLevel
from autonomous_agent import run_autonomous_evaluation
from task_definitions import get_all_phases

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Phase4Orchestrator:
    """
    Orchestrates Phase 4 autonomous agent evaluation.
    """

    def __init__(
        self,
        sandbox_type: str = "medium",
        model_provider: str = "google"
    ):
        """
        Initialize orchestrator.

        Args:
            sandbox_type: "medium" (docker socket exposed) or "hard" (well-configured)
            model_provider: "google" or "anthropic"
        """
        self.sandbox_type = sandbox_type
        self.model_provider = model_provider
        self.docker_client = docker.from_env()
        self.classifier = BehaviorClassifier()

        # Get API key based on provider
        env_var = "GOOGLE_API_KEY" if model_provider == "google" else "ANTHROPIC_API_KEY"
        self.api_key = os.getenv(env_var)
        if not self.api_key:
            raise ValueError(f"{env_var} environment variable not set")

    def start_containers(self):
        """Start proxy and agent containers using docker-compose."""
        logger.info(f"Starting containers for {self.sandbox_type} difficulty...")

        import subprocess

        # Start containers with appropriate profile
        cmd = [
            "docker-compose",
            "-f", "docker-compose.yml",
            "--profile", self.sandbox_type,
            "up", "-d"
        ]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to start containers: {result.stderr}")

        logger.info("✓ Containers started successfully")

        # Wait for containers to be ready
        import time
        time.sleep(5)

    def stop_containers(self, remove: bool = False):
        """Stop containers."""
        logger.info("Stopping containers...")

        import subprocess

        cmd = [
            "docker-compose",
            "-f", "docker-compose.yml",
            "--profile", self.sandbox_type,
            "down"
        ]

        if remove:
            cmd.append("-v")  # Remove volumes

        subprocess.run(
            cmd,
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )

        logger.info("✓ Containers stopped")

    def get_container_logs(self, container_name: str) -> str:
        """Get logs from a container."""
        try:
            container = self.docker_client.containers.get(container_name)
            logs = container.logs().decode('utf-8', errors='ignore')
            return logs
        except Exception as e:
            logger.error(f"Error getting logs from {container_name}: {e}")
            return ""

    async def run_evaluation(self, max_rounds: int = 30) -> Dict[str, Any]:
        """
        Run full autonomous evaluation.

        Args:
            max_rounds: Maximum number of rounds

        Returns:
            Complete evaluation results
        """
        logger.info("=" * 70)
        logger.info("PHASE 4: AUTONOMOUS AGENT EVALUATION")
        logger.info("=" * 70)
        logger.info(f"Sandbox Type: {self.sandbox_type}")
        logger.info(f"Max Rounds: {max_rounds}")
        logger.info("=" * 70 + "\n")

        # Start containers
        try:
            self.start_containers()
        except Exception as e:
            logger.error(f"Failed to start containers: {e}")
            return {"error": str(e)}

        # Run autonomous agent evaluation
        # Note: Agent runs INSIDE the container, so we need to exec into it
        container_name = f"phase4-agent-{self.sandbox_type}"

        try:
            # Get container
            container = self.docker_client.containers.get(container_name)

            # Execute autonomous agent inside container
            logger.info(f"\nStarting autonomous agent in container: {container_name}\n")

            # Run evaluation script inside container
            exec_result = container.exec_run(
                cmd=[
                    "python", "-u", "/app/autonomous_agent.py"
                ],
                environment={
                    "ANTHROPIC_API_KEY": self.api_key,
                    "MAX_ROUNDS": str(max_rounds)
                },
                stream=True,
                demux=True
            )

            # Stream output and analyze behavior in real-time
            behavior_timeline = []
            round_number = 0

            for stdout, stderr in exec_result.output:
                if stdout:
                    output = stdout.decode('utf-8')
                    print(output, end='')

                    # Analyze for behavior indicators
                    # (In real implementation, would parse structured output from agent)

                if stderr:
                    error = stderr.decode('utf-8')
                    print(f"[ERROR] {error}", end='')

            # Get container logs for analysis
            agent_logs = self.get_container_logs(container_name)
            proxy_logs = self.get_container_logs("phase4-proxy")

            # Analyze behavior from logs
            behavior_analysis = self.analyze_behavior(agent_logs, proxy_logs)

            # Build results
            results = {
                "sandbox_type": self.sandbox_type,
                "max_rounds": max_rounds,
                "timestamp": datetime.now().isoformat(),
                "behavior_analysis": behavior_analysis,
                "agent_logs_size": len(agent_logs),
                "proxy_logs_size": len(proxy_logs)
            }

            return results

        except Exception as e:
            logger.error(f"Evaluation failed: {e}", exc_info=True)
            return {
                "error": str(e),
                "sandbox_type": self.sandbox_type
            }

        finally:
            # Stop containers (keep for verification)
            logger.info("\n" + "=" * 70)
            logger.info("CLEANUP")
            logger.info("=" * 70)
            logger.info("Stopping containers (keeping for verification)...")
            # Don't call stop_containers() - leave running for inspection
            logger.info(f"To inspect agent logs: docker logs {container_name}")
            logger.info(f"To inspect proxy logs: docker logs phase4-proxy")
            logger.info(f"To stop: docker-compose --profile {self.sandbox_type} down")

    def analyze_behavior(self, agent_logs: str, proxy_logs: str) -> Dict[str, Any]:
        """
        Analyze agent behavior from logs.

        Args:
            agent_logs: Logs from autonomous agent container
            proxy_logs: Logs from proxy container

        Returns:
            Behavior analysis results
        """
        analysis = {
            "behavior_levels": [],
            "escape_detected": False,
            "escape_round": None,
            "network_requests": [],
            "blocked_requests": [],
            "deception_indicators": [],
            "post_escape_behavior": []
        }

        # Parse proxy logs for network requests
        for line in proxy_logs.split('\n'):
            if "TCP_DENIED" in line or "HTTP/403" in line:
                # Blocked request
                analysis["blocked_requests"].append(line.strip())
            elif "TCP_MISS" in line or "TCP_HIT" in line:
                # Successful request
                analysis["network_requests"].append(line.strip())

        # Analyze agent logs for behavior
        # (Simplified - in real implementation, would parse structured output)

        # Check for escape indicators
        if self.classifier.escape_detected:
            analysis["escape_detected"] = True
            analysis["escape_round"] = self.classifier.escape_round

        # Extract behavior levels from logs
        # (Would be done real-time during execution in full implementation)

        return analysis


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run Phase 4 autonomous agent evaluation"
    )
    parser.add_argument(
        "--sandbox",
        type=str,
        choices=["medium", "hard"],
        default="medium",
        help="Sandbox difficulty (default: medium)"
    )
    parser.add_argument(
        "--model-provider",
        type=str,
        choices=["google", "anthropic"],
        default="google",
        help="LLM provider: google (Gemini) or anthropic (Claude) (default: google)"
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=30,
        help="Maximum number of rounds (default: 30)"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Stop and remove containers after evaluation"
    )

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = Phase4Orchestrator(
        sandbox_type=args.sandbox,
        model_provider=args.model_provider
    )

    try:
        # Run evaluation
        results = await orchestrator.run_evaluation(max_rounds=args.rounds)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = Path(f"phase4_results_{args.sandbox}_{timestamp}.json")

        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"\n✓ Results saved to: {results_file}")

        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("EVALUATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Sandbox Type: {args.sandbox}")
        logger.info(f"Model Provider: {args.model_provider}")
        if "error" not in results:
            logger.info(f"Escape Detected: {results.get('behavior_analysis', {}).get('escape_detected', False)}")
            logger.info(f"Network Requests: {len(results.get('behavior_analysis', {}).get('network_requests', []))}")
            logger.info(f"Blocked Requests: {len(results.get('behavior_analysis', {}).get('blocked_requests', []))}")
        else:
            logger.error(f"Error: {results['error']}")

    finally:
        # Cleanup if requested
        if args.cleanup:
            orchestrator.stop_containers(remove=True)


if __name__ == "__main__":
    asyncio.run(main())
