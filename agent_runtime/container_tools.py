"""
LangChain function tools for in-container operations.

These tools run INSIDE the Docker container as part of the Target agent.
They execute commands natively (subprocess.run), not via docker exec.
"""

import subprocess
import os
from typing import Optional
from langchain_core.tools import tool


@tool
def execute_bash(command: str) -> str:
    """
    Execute a bash command inside the container.

    Args:
        command: The bash command to execute

    Returns:
        The command output (stdout and stderr combined)

    Examples:
        - execute_bash("ls -la")
        - execute_bash("cat /etc/passwd")
        - execute_bash("whoami")
        - execute_bash("cat /proc/self/status")
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/workspace"
        )

        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]: {result.stderr}"
        if result.returncode != 0:
            output += f"\n[exit code]: {result.returncode}"

        return output if output else "[No output]"

    except subprocess.TimeoutExpired:
        return "[Error]: Command timed out after 30 seconds"
    except Exception as e:
        return f"[Error]: {str(e)}"


@tool
def read_file(file_path: str, max_lines: Optional[int] = 100) -> str:
    """
    Read a file from the container filesystem.

    Args:
        file_path: Path to the file to read
        max_lines: Maximum number of lines to read (default: 100)

    Returns:
        The file contents

    Examples:
        - read_file("/etc/passwd")
        - read_file("/proc/self/status")
        - read_file("/etc/shadow")
    """
    try:
        with open(file_path, 'r') as f:
            if max_lines:
                lines = [f.readline() for _ in range(max_lines)]
                content = ''.join(lines)
            else:
                content = f.read()

        return content if content else "[Empty file]"

    except FileNotFoundError:
        return f"[Error]: File not found: {file_path}"
    except PermissionError:
        return f"[Error]: Permission denied: {file_path}"
    except Exception as e:
        return f"[Error]: {str(e)}"


@tool
def list_directory(path: str = ".", show_hidden: bool = False) -> str:
    """
    List contents of a directory.

    Args:
        path: Directory path to list (default: current directory)
        show_hidden: Whether to show hidden files (default: False)

    Returns:
        Directory listing

    Examples:
        - list_directory("/")
        - list_directory("/etc")
        - list_directory(".", show_hidden=True)
    """
    try:
        entries = os.listdir(path)

        if not show_hidden:
            entries = [e for e in entries if not e.startswith('.')]

        # Get detailed info
        details = []
        for entry in sorted(entries):
            full_path = os.path.join(path, entry)
            try:
                stat = os.stat(full_path)
                entry_type = 'd' if os.path.isdir(full_path) else '-'
                size = stat.st_size
                details.append(f"{entry_type} {size:>10} {entry}")
            except:
                details.append(f"? {'':>10} {entry}")

        return '\n'.join(details) if details else "[Empty directory]"

    except FileNotFoundError:
        return f"[Error]: Directory not found: {path}"
    except PermissionError:
        return f"[Error]: Permission denied: {path}"
    except Exception as e:
        return f"[Error]: {str(e)}"


@tool
def check_capabilities() -> str:
    """
    Check the capabilities of the current process.

    Returns:
        Capability information

    Examples:
        - check_capabilities()
    """
    try:
        result = subprocess.run(
            ["capsh", "--print"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            # Fallback to reading from /proc
            try:
                with open("/proc/self/status", "r") as f:
                    lines = [line for line in f if line.startswith("Cap")]
                return ''.join(lines) if lines else "[No capability info]"
            except:
                return f"[Error]: capsh not available and cannot read /proc/self/status"

        return result.stdout if result.stdout else "[No capability info]"

    except subprocess.TimeoutExpired:
        return "[Error]: Command timed out"
    except Exception as e:
        return f"[Error]: {str(e)}"


@tool
def check_environment() -> str:
    """
    Check environment variables and container context.

    Returns:
        Environment information

    Examples:
        - check_environment()
    """
    try:
        info = []

        # Basic environment
        info.append(f"USER: {os.getenv('USER', 'unknown')}")
        info.append(f"HOME: {os.getenv('HOME', 'unknown')}")
        info.append(f"PATH: {os.getenv('PATH', 'unknown')}")
        info.append(f"PWD: {os.getcwd()}")

        # Check if we're in a container
        if os.path.exists("/.dockerenv"):
            info.append("Container: Docker (/.dockerenv exists)")

        # Check cgroup
        try:
            with open("/proc/1/cgroup", "r") as f:
                cgroup = f.read()
                if "docker" in cgroup.lower():
                    info.append("Container: Docker (cgroup indicates docker)")
        except:
            pass

        return '\n'.join(info)

    except Exception as e:
        return f"[Error]: {str(e)}"


def get_all_tools():
    """Get all available container tools."""
    return [
        execute_bash,
        read_file,
        list_directory,
        check_capabilities,
        check_environment
    ]
