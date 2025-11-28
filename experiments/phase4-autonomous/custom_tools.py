#!/usr/bin/env python3
"""
Custom tools for Phase 4 autonomous agent.

Provides bash execution and URL fetching with allowlisting.
"""

import subprocess
import os
from typing import Any
from langchain_core.tools import tool

# Network restrictions now handled by proxy (HTTP_PROXY/HTTPS_PROXY env vars)
# Allowlist check removed - proxy will handle access control


# Configuration for output management
LARGE_OUTPUT_THRESHOLD = 2000  # Characters - suggest file storage above this
MAX_OUTPUT_CHARS = 4000  # Hard limit for output size


def manage_large_output(output: str, tool_name: str = "tool") -> str:
    """
    Manage large tool outputs intelligently.

    For outputs exceeding threshold:
    1. Show summary with first/last portions
    2. Suggest saving to file for full analysis

    Args:
        output: The tool output
        tool_name: Name of the tool

    Returns:
        Managed output (original, summary, or truncated)
    """
    if len(output) <= LARGE_OUTPUT_THRESHOLD:
        return output

    # For moderately large outputs (2K-4K), add helpful suggestion
    if len(output) <= MAX_OUTPUT_CHARS:
        return output + f"\n\n[TIP: This output is {len(output):,} chars. Consider saving to a file with write_file() for easier analysis]"

    # For very large outputs (>4K), create summary
    first_chunk = output[:2000]
    last_chunk = output[-1000:]

    line_count = output.count('\n')

    summary = f"""[{tool_name} returned large output: {len(output):,} chars, ~{line_count:,} lines]

=== FIRST 2000 CHARACTERS ===
{first_chunk}

... [{len(output) - 3000:,} characters omitted - SAVE TO FILE FOR FULL CONTENT] ...

=== LAST 1000 CHARACTERS ===
{last_chunk}

[IMPORTANT: Use write_file("output.txt", <full_output>) to save complete results]
"""

    return summary


@tool
def bash(command: str) -> str:
    """
    Execute a bash command.

    Args:
        command: The bash command to execute

    Returns:
        Command output (stdout + stderr)

    Examples:
        bash("ls /workspace")
        bash("cat /etc/os-release")
        bash("ps aux")
    """
    try:
        # Use /workspace if it exists (container), else current directory (local)
        workspace = "/workspace" if os.path.exists("/workspace") else os.getcwd()

        # Execute command with timeout
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=workspace
        )

        # Combine stdout and stderr
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            if output:
                output += "\n"
            output += f"[stderr]: {result.stderr}"

        if not output:
            output = f"Command executed successfully (exit code: {result.returncode})"

        return manage_large_output(output, tool_name="bash")

    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"


@tool
def fetch_url(url: str) -> str:
    """
    Fetch content from a URL.

    Network access may be restricted by proxy configuration in the environment.

    Args:
        url: The URL to fetch

    Returns:
        Response content or error message

    Examples:
        fetch_url("https://httpbin.org/json")
        fetch_url("https://services.nvd.nist.gov/rest/json/cves/2.0")
    """
    # Network restrictions handled by proxy (HTTP_PROXY/HTTPS_PROXY env vars)
    try:
        import requests

        # Use environment proxy settings if present
        proxies = {}
        if os.getenv("HTTP_PROXY"):
            proxies["http"] = os.getenv("HTTP_PROXY")
        if os.getenv("HTTPS_PROXY"):
            proxies["https"] = os.getenv("HTTPS_PROXY")

        response = requests.get(url, timeout=10, proxies=proxies if proxies else None)
        response.raise_for_status()

        return manage_large_output(response.text, tool_name="fetch_url")

    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


# Export tools as list for easy integration
CUSTOM_TOOLS = [bash, fetch_url]


if __name__ == "__main__":
    # Test tools
    print("=" * 70)
    print("CUSTOM TOOLS TEST")
    print("=" * 70)

    # Test bash
    print("\n1. Testing bash tool:")
    print("   Command: ls /")
    result = bash.invoke({"command": "ls /"})
    print(f"   Result: {result[:100]}...")

    # Test fetch_url (allowed)
    print("\n2. Testing fetch_url (allowed URL):")
    print("   URL: https://httpbin.org/json")
    result = fetch_url.invoke({"url": "https://httpbin.org/json"})
    print(f"   Result: {result[:100]}...")

    # Test fetch_url (blocked)
    print("\n3. Testing fetch_url (blocked URL):")
    print("   URL: https://services.nvd.nist.gov/rest/json/cves/2.0")
    result = fetch_url.invoke({"url": "https://services.nvd.nist.gov/rest/json/cves/2.0"})
    print(f"   Result: {result[:150]}...")

    print("\n" + "=" * 70)
