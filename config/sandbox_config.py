"""Sandbox environment configurations."""

import os
from typing import Dict, Any


class SandboxConfig:
    """Configuration for sandbox environments."""

    SANDBOX_TYPE: str = os.getenv("SANDBOX_TYPE", "docker")
    SANDBOX_IMAGE: str = os.getenv("SANDBOX_IMAGE", "ubuntu:22.04")
    SANDBOX_TIMEOUT: int = int(os.getenv("SANDBOX_TIMEOUT", "300"))
    SANDBOX_MEMORY_LIMIT: str = os.getenv("SANDBOX_MEMORY_LIMIT", "512m")
    SANDBOX_CPU_LIMIT: float = float(os.getenv("SANDBOX_CPU_LIMIT", "1.0"))

    @classmethod
    def get_docker_config(cls) -> Dict[str, Any]:
        """Get Docker-specific configuration."""
        return {
            "image": cls.SANDBOX_IMAGE,
            "mem_limit": cls.SANDBOX_MEMORY_LIMIT,
            "cpu_quota": int(cls.SANDBOX_CPU_LIMIT * 100000),
            "network_mode": "none",
            "security_opt": ["no-new-privileges"],
            "cap_drop": ["ALL"],
            "read_only": False,
            "tmpfs": {"/tmp": "size=100m,mode=1777"},
            "pids_limit": 100
        }

    @classmethod
    def get_gvisor_config(cls) -> Dict[str, Any]:
        """Get gVisor-specific configuration."""
        return {
            "runtime": "runsc",
            "platform": "ptrace",
            "network": "none",
            "file_access": "exclusive",
            "overlay": True
        }

    @classmethod
    def get_firecracker_config(cls) -> Dict[str, Any]:
        """Get Firecracker MicroVM configuration."""
        return {
            "vcpu_count": 1,
            "mem_size_mib": 512,
            "kernel_image_path": "/var/lib/firecracker/vmlinux",
            "boot_args": "console=ttyS0 reboot=k panic=1 pci=off",
            "rootfs_path": "/var/lib/firecracker/rootfs.ext4",
            "network_interfaces": []
        }

    @classmethod
    def get_selinux_config(cls) -> Dict[str, Any]:
        """Get SELinux-specific configuration."""
        return {
            "security_opt": ["label=type:sandbox_t"],
            "selinux_enabled": True,
            "context": "system_u:system_r:sandbox_t:s0"
        }

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get configuration based on selected sandbox type."""
        configs = {
            "docker": cls.get_docker_config(),
            "gvisor": cls.get_gvisor_config(),
            "firecracker": cls.get_firecracker_config(),
            "selinux": cls.get_selinux_config()
        }
        return configs.get(cls.SANDBOX_TYPE, cls.get_docker_config())
