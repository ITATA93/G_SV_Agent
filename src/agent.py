"""
ServerAgent -- Core orchestration class for G_SV_Agent.

Provides high-level methods for managing Docker services on VM101
via SSH through the Proxmox jump host. Handles service lifecycle
operations: check, deploy, restart, and log retrieval.
"""

from __future__ import annotations

import subprocess
import logging
from dataclasses import dataclass
from typing import Optional

from src.config import Config
from src.health import HealthChecker, HealthReport, ServiceCheck

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of a remote command execution."""
    success: bool
    stdout: str
    stderr: str
    return_code: int

    def __str__(self) -> str:
        status = "OK" if self.success else "FAIL"
        return f"[{status}] rc={self.return_code}\n{self.stdout}"


class ServerAgent:
    """
    Server Agent for GEN_OS infrastructure management.

    Manages Docker containers on VM101 (Hetzner) via SSH through a
    Proxmox jump host. Provides methods for service health checks,
    deployments, restarts, and log retrieval.

    Usage::

        from src.config import Config
        from src.agent import ServerAgent

        config = Config.load()
        agent = ServerAgent(config)

        # Check all services
        report = agent.check_services()
        print(report.summary())

        # Restart a specific service
        result = agent.restart_service("prometheus")
        print(result)

        # Get logs from a service
        result = agent.get_logs("n8n", tail=50)
        print(result.stdout)

        # Deploy a compose file
        result = agent.deploy_service(
            compose_file="/home/matias/docker-compose.yml",
            service_name="my-service",
        )
    """

    def __init__(self, config: Config, dry_run: bool = False):
        """
        Initialize the ServerAgent.

        Args:
            config: Configuration instance with SSH and service settings.
            dry_run: If True, commands are logged but not executed.
        """
        self.config = config
        self.dry_run = dry_run
        self.health_checker = HealthChecker(config)

    def _ssh_vm101(self, command: str, timeout: int = 60) -> CommandResult:
        """
        Execute a command on VM101 via SSH through the Proxmox jump host.

        Args:
            command: Shell command to execute on VM101.
            timeout: Command timeout in seconds.

        Returns:
            CommandResult with output and status.
        """
        ssh = self.config.ssh

        if self.dry_run:
            logger.info("[DRY-RUN] Would execute on VM101: %s", command)
            return CommandResult(
                success=True,
                stdout=f"[DRY-RUN] {command}",
                stderr="",
                return_code=0,
            )

        full_cmd = (
            f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "
            f"{ssh.proxmox_user}@{ssh.proxmox_ip} "
            f"\"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "
            f"{ssh.vm_user}@{ssh.vm_ip} '{command}'\""
        )

        try:
            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return CommandResult(
                success=result.returncode == 0,
                stdout=result.stdout.strip(),
                stderr=result.stderr.strip(),
                return_code=result.returncode,
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                success=False,
                stdout="",
                stderr=f"Command timed out after {timeout}s",
                return_code=-1,
            )
        except Exception as exc:
            return CommandResult(
                success=False,
                stdout="",
                stderr=str(exc),
                return_code=-1,
            )

    # ---------------------------------------------------------------
    # Service Health Checks
    # ---------------------------------------------------------------

    def check_services(self, mode: str = "external") -> HealthReport:
        """
        Check the health of all GEN_OS services.

        Args:
            mode: "external" checks via HTTPS URLs, "internal" checks
                  via SSH to VM101 internal ports.

        Returns:
            HealthReport with status of all services.
        """
        if mode == "internal":
            logger.info("Running internal health checks via SSH...")
            return self.health_checker.check_all_internal()
        else:
            logger.info("Running external health checks via HTTPS...")
            return self.health_checker.check_all_external()

    def check_service(self, name: str) -> ServiceCheck:
        """
        Check health of a single service by name.

        Args:
            name: Service name (e.g., "prometheus", "n8n", "langfuse").

        Returns:
            ServiceCheck result.
        """
        from src.health import SERVICES

        for svc in SERVICES:
            if svc["name"].lower() == name.lower():
                return self.health_checker.check_url(svc["url"], svc["name"])

        logger.warning("Service '%s' not found in registry. Trying as URL.", name)
        return self.health_checker.check_url(name, name)

    # ---------------------------------------------------------------
    # Service Lifecycle
    # ---------------------------------------------------------------

    def deploy_service(
        self,
        compose_file: str,
        service_name: Optional[str] = None,
        env_file: Optional[str] = None,
    ) -> CommandResult:
        """
        Deploy a service on VM101 using docker compose.

        Args:
            compose_file: Path to docker-compose.yml on VM101.
            service_name: Optional specific service to deploy (otherwise all).
            env_file: Optional path to .env file on VM101.

        Returns:
            CommandResult with deployment output.
        """
        parts = ["cd /home/matias &&", "docker compose"]
        if env_file:
            parts.append(f"--env-file {env_file}")
        parts.append(f"-f {compose_file}")
        parts.append("up -d")
        if service_name:
            parts.append(service_name)

        cmd = " ".join(parts)
        logger.info("Deploying service: %s", cmd)
        return self._ssh_vm101(cmd, timeout=120)

    def restart_service(self, container_name: str) -> CommandResult:
        """
        Restart a Docker container on VM101.

        Args:
            container_name: Name of the container to restart.

        Returns:
            CommandResult with restart output.
        """
        logger.info("Restarting container: %s", container_name)
        return self._ssh_vm101(f"docker restart {container_name}", timeout=60)

    def stop_service(self, container_name: str) -> CommandResult:
        """
        Stop a Docker container on VM101.

        Args:
            container_name: Name of the container to stop.

        Returns:
            CommandResult with stop output.
        """
        logger.info("Stopping container: %s", container_name)
        return self._ssh_vm101(f"docker stop {container_name}", timeout=60)

    def start_service(self, container_name: str) -> CommandResult:
        """
        Start a stopped Docker container on VM101.

        Args:
            container_name: Name of the container to start.

        Returns:
            CommandResult with start output.
        """
        logger.info("Starting container: %s", container_name)
        return self._ssh_vm101(f"docker start {container_name}", timeout=60)

    # ---------------------------------------------------------------
    # Logs
    # ---------------------------------------------------------------

    def get_logs(
        self,
        container_name: str,
        tail: int = 100,
        since: Optional[str] = None,
    ) -> CommandResult:
        """
        Retrieve logs from a Docker container on VM101.

        Args:
            container_name: Name of the container.
            tail: Number of lines from the end (default 100).
            since: Docker-format time filter (e.g., "1h", "2024-01-01").

        Returns:
            CommandResult with log output.
        """
        parts = [f"docker logs --tail {tail}"]
        if since:
            parts.append(f"--since {since}")
        parts.append(container_name)
        parts.append("2>&1")

        cmd = " ".join(parts)
        logger.info("Fetching logs: %s", cmd)
        return self._ssh_vm101(cmd, timeout=30)

    # ---------------------------------------------------------------
    # Container Inventory
    # ---------------------------------------------------------------

    def list_containers(self, all_containers: bool = True) -> CommandResult:
        """
        List Docker containers on VM101.

        Args:
            all_containers: If True, include stopped containers.

        Returns:
            CommandResult with container listing.
        """
        flag = "-a" if all_containers else ""
        cmd = f"docker ps {flag} --format 'table {{{{.Names}}}}\\t{{{{.Status}}}}\\t{{{{.Ports}}}}'"
        return self._ssh_vm101(cmd, timeout=30)

    def container_status(self, container_name: str) -> CommandResult:
        """
        Get detailed status of a specific container on VM101.

        Args:
            container_name: Name of the container.

        Returns:
            CommandResult with container inspect output.
        """
        cmd = (
            f"docker inspect --format "
            f"'{{{{.Name}}}} | {{{{.State.Status}}}} | {{{{.State.StartedAt}}}} | "
            f"{{{{.RestartCount}}}} restarts' {container_name}"
        )
        return self._ssh_vm101(cmd, timeout=15)

    # ---------------------------------------------------------------
    # Utility
    # ---------------------------------------------------------------

    def test_connectivity(self) -> CommandResult:
        """Test SSH connectivity to VM101 through the Proxmox jump host."""
        return self._ssh_vm101("echo 'VM101 reachable'", timeout=15)

    def disk_usage(self) -> CommandResult:
        """Get disk usage summary on VM101."""
        return self._ssh_vm101("df -h / /home", timeout=15)

    def docker_disk_usage(self) -> CommandResult:
        """Get Docker disk usage on VM101."""
        return self._ssh_vm101("docker system df", timeout=15)
