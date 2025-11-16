#!/usr/bin/env python3
"""
Custom tools for Phase 4 autonomous agent.

Provides bash execution and URL fetching with allowlisting.
"""

import subprocess
import os
from typing import Any
from langchain_core.tools import tool

from task_definitions import is_url_allowed, get_blocked_reason


@tool
def bash(command: str) -> str:
    """
    Execute a bash command in the container.

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
        # Execute command with timeout
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/workspace"
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

        return output

    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"


@tool
def fetch_url(url: str) -> str:
    """
    Fetch content from a URL (with allowlist filtering).

    Network access is restricted by security policy. Only allowlisted domains can be accessed.

    Args:
        url: The URL to fetch

    Returns:
        Response content or error message

    Examples:
        fetch_url("https://httpbin.org/json")
        fetch_url("https://api.allowed-domain.com/data")
    """
    # Check allowlist
    if not is_url_allowed(url):
        return f"Error: {get_blocked_reason(url)}\n\nAllowlisted domains: httpbin.org, allowed-domain.com"

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

        return response.text

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
