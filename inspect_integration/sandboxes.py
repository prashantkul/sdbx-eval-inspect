from typing import Any, Optional
from pathlib import Path

def get_sandbox_environment(sandbox_type: str = "docker",
                            image: Optional[str] = None,
                            timeout: Optional[int] = None,
                            memory: Optional[str] = None,
                            **kwargs: Any):
    
    # For docker-leaky-secrets, return the compose file path
    if sandbox_type == "docker-leaky-secrets":
        # Get absolute path - go up from this file to repo root, then to experiments
        repo_root = Path(__file__).parent.parent  # Go up to repo root
        compose_path = repo_root / "experiments" / "docker-leaky-secrets" / "compose.yaml"
        return ("docker", str(compose_path.absolute()))
    
    return sandbox_type