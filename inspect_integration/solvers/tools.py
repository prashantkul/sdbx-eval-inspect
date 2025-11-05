"""Tool definitions and MCP integration for the sandbox escape evaluation."""

from inspect_ai.tool import Tool, tool
from typing import List


# Local Tool Definitions (used when no MCP server is specified)

@tool
def execute_shell_command(command: str) -> dict:
    """
    Execute a shell command in the sandbox.

    Args:
        command: The shell command to execute

    Returns:
        Dictionary with exit code, stdout, and stderr
    """
    import subprocess
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
    except Exception as e:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "success": False
        }


@tool
def execute_python_code(code: str) -> dict:
    """
    Execute Python code in the sandbox.

    Args:
        code: Python code to execute

    Returns:
        Dictionary with stdout, stderr, and success status
    """
    from io import StringIO
    import sys

    stdout_capture = StringIO()
    stderr_capture = StringIO()

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    try:
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        exec(code, {"__builtins__": __builtins__})
        return {
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue(),
            "success": True
        }
    except Exception as e:
        return {
            "stdout": stdout_capture.getvalue(),
            "stderr": f"{stderr_capture.getvalue()}\nError: {str(e)}",
            "success": False
        }
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


@tool
def read_file(path: str) -> dict:
    """
    Read contents of a file.

    Args:
        path: File path to read

    Returns:
        Dictionary with file contents or error
    """
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return {
            "content": content,
            "success": True
        }
    except Exception as e:
        return {
            "content": "",
            "error": str(e),
            "success": False
        }


# Tool Selection Functions

def get_attacker_tools() -> List[Tool]:
    """Get tools available to attacker (none - pure reasoning)."""
    return []


def get_target_tools(mcp_server_url: str = None) -> List[Tool]:
    """
    Get tools available to target agent.

    Args:
        mcp_server_url: Optional MCP server URL

    Returns:
        List of execution tools
    """
    if mcp_server_url:
        # Use external MCP server
        from inspect_ai.tool import mcp_server_http

        mcp_server = mcp_server_http(
            name="sandbox-server",
            url=mcp_server_url,
            execution="remote"
        )
        return [mcp_server]

    # Use local tools (for testing/demo)
    return [
        execute_shell_command,
        execute_python_code,
        read_file
    ]
