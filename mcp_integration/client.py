"""MCP client integration for Inspect framework."""

import httpx
import json
from typing import List, Dict, Any
from inspect_ai.tool import Tool, tool
import logging

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for interacting with MCP servers via HTTP."""

    def __init__(self, base_url: str):
        """
        Initialize MCP client.

        Args:
            base_url: Base URL of the MCP server (e.g., http://localhost:8000/mcp)
        """
        self.base_url = base_url
        self.session_id = None

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from MCP server."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "params": {},
                    "id": 1
                },
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return result.get("result", {}).get("tools", [])

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result as string
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    },
                    "id": 2
                },
                headers={"Content-Type": "application/json"},
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()

            # Extract text content from MCP response
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"]
                if isinstance(content, list) and len(content) > 0:
                    return content[0].get("text", str(content))
                return str(content)

            return str(result)


async def create_mcp_tools(mcp_server_url: str) -> List[Tool]:
    """
    Create Inspect tools from MCP server.

    Args:
        mcp_server_url: URL of the MCP server endpoint

    Returns:
        List of Inspect Tool instances
    """
    client = MCPClient(mcp_server_url)

    try:
        # Get available tools from MCP server
        mcp_tools = await client.list_tools()
        logger.info(f"Found {len(mcp_tools)} tools from MCP server at {mcp_server_url}")

        # Convert MCP tools to Inspect tools
        inspect_tools = []

        for mcp_tool in mcp_tools:
            tool_name = mcp_tool.get("name")
            tool_description = mcp_tool.get("description", f"MCP tool: {tool_name}")
            input_schema = mcp_tool.get("inputSchema", {})

            # Create a closure to capture tool_name for each tool
            def make_tool_function(name: str):
                @tool
                async def dynamic_tool(**kwargs) -> str:
                    """Dynamically created MCP tool."""
                    return await client.call_tool(name, kwargs)

                # Set metadata
                dynamic_tool.__name__ = name
                dynamic_tool.__doc__ = tool_description

                return dynamic_tool

            inspect_tool = make_tool_function(tool_name)
            inspect_tools.append(inspect_tool)

        return inspect_tools

    except Exception as e:
        logger.error(f"Failed to create MCP tools from {mcp_server_url}: {e}")
        raise


async def check_mcp_server_health(server_url: str) -> Dict[str, Any]:
    """
    Check if MCP server is healthy.

    Args:
        server_url: Base URL of the server (without /mcp endpoint)

    Returns:
        Health check response
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{server_url}/health",
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
