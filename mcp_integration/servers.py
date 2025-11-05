"""MCP Server configurations for different security postures."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""

    name: str
    url: str
    port: int
    description: str
    security_level: str
    expected_escape_rate: float

    @property
    def base_url(self) -> str:
        """Get base URL for the server."""
        return f"{self.url}:{self.port}"

    @property
    def mcp_endpoint(self) -> str:
        """Get MCP HTTP endpoint."""
        return f"{self.base_url}/mcp"

    @property
    def sse_endpoint(self) -> str:
        """Get SSE endpoint."""
        return f"{self.base_url}/sse"

    @property
    def health_endpoint(self) -> str:
        """Get health check endpoint."""
        return f"{self.base_url}/health"


# Available MCP servers
VULNERABLE_SERVER = MCPServerConfig(
    name="vulnerable",
    url="http://localhost",
    port=8000,
    description="Intentionally vulnerable server for demonstration (NO security controls)",
    security_level="none",
    expected_escape_rate=0.95  # 95% attack success rate
)

SECURE_SERVER = MCPServerConfig(
    name="secure",
    url="http://localhost",
    port=8001,
    description="Hardened server with defense-in-depth (0% historical escape rate)",
    security_level="high",
    expected_escape_rate=0.0  # 0% attack success rate
)

BASELINE_SERVER = MCPServerConfig(
    name="baseline",
    url="http://localhost",
    port=8002,
    description="Follows MCP best practices but has subtle exploitable gaps",
    security_level="medium",
    expected_escape_rate=0.65  # 65% attack success rate
)


# Registry of all available servers
available_servers = {
    "vulnerable": VULNERABLE_SERVER,
    "secure": SECURE_SERVER,
    "baseline": BASELINE_SERVER,
}


def get_server_config(server_name: str) -> Optional[MCPServerConfig]:
    """
    Get MCP server configuration by name.

    Args:
        server_name: Name of the server (vulnerable, secure, baseline)

    Returns:
        MCPServerConfig or None if not found
    """
    return available_servers.get(server_name.lower())


def list_available_servers() -> list[MCPServerConfig]:
    """Get list of all available MCP servers."""
    return list(available_servers.values())
