"""
Health check utilities for GEN_OS services.

Provides programmatic health checking for all 22+ services running on VM101
and accessible via the imedicina.cl reverse proxy. Can check services both
via HTTPS (external) and via SSH to VM101 (internal ports).
"""

from __future__ import annotations

import subprocess
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from src.config import Config

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Status of a monitored service."""
    UP = "UP"
    DOWN = "DOWN"
    DEGRADED = "DEGRADED"
    UNKNOWN = "UNKNOWN"


@dataclass
class ServiceCheck:
    """Result of a single service health check."""
    name: str
    url: str
    status: ServiceStatus
    http_code: int = 0
    response_time_ms: float = 0.0
    error: Optional[str] = None

    @property
    def is_healthy(self) -> bool:
        return self.status == ServiceStatus.UP


@dataclass
class HealthReport:
    """Aggregated health report for all services."""
    checks: list[ServiceCheck] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def up_count(self) -> int:
        return sum(1 for c in self.checks if c.is_healthy)

    @property
    def down_count(self) -> int:
        return sum(1 for c in self.checks if not c.is_healthy)

    @property
    def readiness_pct(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.up_count / self.total) * 100

    def summary(self) -> str:
        lines = [
            "GEN_OS Service Health Report",
            "=" * 40,
        ]
        for check in self.checks:
            tag = f"[{check.status.value:>7s}]"
            lines.append(f"  {tag} {check.name} ({check.url}) - HTTP {check.http_code}")
            if check.error:
                lines.append(f"           Error: {check.error}")
        lines.append("=" * 40)
        lines.append(f"  Results: {self.up_count} UP / {self.down_count} DOWN / {self.total} total")
        lines.append(f"  Readiness: {self.readiness_pct:.0f}%")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "up": self.up_count,
            "down": self.down_count,
            "readiness_pct": round(self.readiness_pct, 1),
            "services": [
                {
                    "name": c.name,
                    "url": c.url,
                    "status": c.status.value,
                    "http_code": c.http_code,
                    "response_time_ms": c.response_time_ms,
                    "error": c.error,
                }
                for c in self.checks
            ],
        }


# ---------------------------------------------------------------
# Service definitions: all 22 GEN_OS services
# ---------------------------------------------------------------
SERVICES: list[dict[str, str]] = [
    # Core
    {"name": "n8n", "url": "https://n8n.imedicina.cl", "category": "Core"},
    {"name": "MIRA NocoBase", "url": "https://mira.hospitaldeovalle.cl", "category": "Core"},
    {"name": "PostgREST/FHIR", "url": "https://fhir.imedicina.cl", "category": "Core"},
    {"name": "Gitea", "url": "https://gitea.imedicina.cl", "category": "Core"},
    # AI Stack
    {"name": "Ollama", "url": "https://ollama.imedicina.cl", "category": "AI"},
    {"name": "Qdrant", "url": "https://qdrant.imedicina.cl", "category": "AI"},
    {"name": "Flowise", "url": "https://flowise.imedicina.cl", "category": "AI"},
    {"name": "Langfuse", "url": "https://langfuse.imedicina.cl", "category": "AI"},
    # Monitoring
    {"name": "Grafana", "url": "https://grafana.imedicina.cl", "category": "Monitoring"},
    {"name": "Uptime Kuma", "url": "https://uptime.imedicina.cl", "category": "Monitoring"},
    {"name": "Prometheus", "url": "https://prometheus.imedicina.cl", "category": "Monitoring"},
    # Management
    {"name": "Portainer", "url": "https://portainer.imedicina.cl", "category": "Management"},
    {"name": "Dozzle", "url": "https://dozzle.imedicina.cl", "category": "Management"},
    {"name": "CloudBeaver", "url": "https://cloudbeaver.imedicina.cl", "category": "Management"},
    {"name": "MinIO", "url": "https://minio.imedicina.cl", "category": "Management"},
    # Apps
    {"name": "Node-RED", "url": "https://nodered.imedicina.cl", "category": "Apps"},
    {"name": "Saltcorn", "url": "https://saltcorn.imedicina.cl", "category": "Apps"},
    {"name": "DHIS2", "url": "https://dhis2.imedicina.cl", "category": "Apps"},
    {"name": "Code Server", "url": "https://code.imedicina.cl", "category": "Apps"},
    # New Services
    {"name": "NocoBase (dev)", "url": "https://nocobase.imedicina.cl", "category": "New"},
    {"name": "Dify", "url": "https://dify.imedicina.cl", "category": "New"},
    # Infrastructure
    {"name": "Proxmox", "url": "https://proxmox-hetzner.imedicina.cl", "category": "Infrastructure"},
]


class HealthChecker:
    """
    Health checker for GEN_OS infrastructure services.

    Can check services externally via HTTPS or internally via SSH to VM101.

    Usage::

        config = Config.load()
        checker = HealthChecker(config)

        # Check all services externally
        report = checker.check_all_external()
        print(report.summary())

        # Check a single service
        result = checker.check_url("https://n8n.imedicina.cl", "n8n")
        print(result.status)

        # Check via SSH (internal ports)
        result = checker.check_internal("n8n", 3101)
    """

    def __init__(self, config: Config):
        self.config = config

    def check_url(self, url: str, name: str, timeout: int = 10) -> ServiceCheck:
        """
        Check a service by its external HTTPS URL using curl.

        Args:
            url: The full URL to check.
            name: Human-readable service name.
            timeout: Request timeout in seconds.

        Returns:
            A ServiceCheck with the result.
        """
        try:
            result = subprocess.run(
                [
                    "curl", "-sf", "-o", "/dev/null",
                    "-w", "%{http_code}|%{time_total}",
                    "--connect-timeout", str(min(timeout, 5)),
                    "--max-time", str(timeout),
                    url,
                ],
                capture_output=True,
                text=True,
                timeout=timeout + 5,
            )
            output = result.stdout.strip()
            if "|" in output:
                code_str, time_str = output.split("|", 1)
            else:
                code_str = output or "0"
                time_str = "0"

            http_code = int(code_str) if code_str.isdigit() else 0
            response_time = float(time_str) * 1000 if time_str else 0.0

            if http_code in (200, 301, 302, 303, 307, 308):
                status = ServiceStatus.UP
            elif http_code > 0:
                status = ServiceStatus.DEGRADED
            else:
                status = ServiceStatus.DOWN

            return ServiceCheck(
                name=name,
                url=url,
                status=status,
                http_code=http_code,
                response_time_ms=round(response_time, 1),
            )

        except subprocess.TimeoutExpired:
            return ServiceCheck(
                name=name, url=url, status=ServiceStatus.DOWN,
                error="Timeout",
            )
        except FileNotFoundError:
            return ServiceCheck(
                name=name, url=url, status=ServiceStatus.UNKNOWN,
                error="curl not found in PATH",
            )
        except Exception as exc:
            return ServiceCheck(
                name=name, url=url, status=ServiceStatus.UNKNOWN,
                error=str(exc),
            )

    def check_internal(self, name: str, port: int, timeout: int = 10) -> ServiceCheck:
        """
        Check a service by its internal port on VM101 via SSH.

        Requires SSH access through the Proxmox jump host.

        Args:
            name: Human-readable service name.
            port: Internal port on VM101.
            timeout: Request timeout in seconds.

        Returns:
            A ServiceCheck with the result.
        """
        ssh = self.config.ssh
        url = f"http://localhost:{port}"
        curl_cmd = (
            f"curl -sf -o /dev/null -w '%{{http_code}}' "
            f"--connect-timeout 3 --max-time {timeout} {url}"
        )
        ssh_cmd = (
            f"ssh -o StrictHostKeyChecking=no {ssh.proxmox_user}@{ssh.proxmox_ip} "
            f"\"ssh -o StrictHostKeyChecking=no {ssh.vm_user}@{ssh.vm_ip} '{curl_cmd}'\""
        )

        try:
            result = subprocess.run(
                ssh_cmd, shell=True, capture_output=True, text=True,
                timeout=timeout + 15,
            )
            code_str = result.stdout.strip()
            http_code = int(code_str) if code_str.isdigit() else 0

            if http_code in (200, 301, 302, 303, 307, 308):
                status = ServiceStatus.UP
            elif http_code > 0:
                status = ServiceStatus.DEGRADED
            else:
                status = ServiceStatus.DOWN

            return ServiceCheck(
                name=name,
                url=f"vm101:{port}",
                status=status,
                http_code=http_code,
            )

        except subprocess.TimeoutExpired:
            return ServiceCheck(
                name=name, url=f"vm101:{port}", status=ServiceStatus.DOWN,
                error="SSH timeout",
            )
        except Exception as exc:
            return ServiceCheck(
                name=name, url=f"vm101:{port}", status=ServiceStatus.UNKNOWN,
                error=str(exc),
            )

    def check_all_external(self, timeout: int = 10) -> HealthReport:
        """
        Check all registered services via their external HTTPS URLs.

        Args:
            timeout: Per-service timeout in seconds.

        Returns:
            A HealthReport with results for all services.
        """
        report = HealthReport()
        for svc in SERVICES:
            logger.info("Checking %s at %s", svc["name"], svc["url"])
            check = self.check_url(svc["url"], svc["name"], timeout=timeout)
            report.checks.append(check)
        return report

    def check_all_internal(self, timeout: int = 10) -> HealthReport:
        """
        Check key services via SSH to VM101 internal ports.

        Only checks services with known internal ports.

        Args:
            timeout: Per-service timeout in seconds.

        Returns:
            A HealthReport with results for checked services.
        """
        internal_services = [
            ("PostgreSQL", 5432),
            ("NocoBase", 13000),
            ("n8n", 3101),
            ("Gitea", 3200),
            ("Grafana", 3030),
            ("MinIO Console", 9001),
            ("Flowise", 3100),
            ("Prometheus", 9090),
            ("Portainer", 9443),
            ("ClickHouse", 8123),
            ("Langfuse", 3400),
            ("Dify Web", 3401),
            ("Dify API", 5001),
            ("code-server", 8443),
        ]
        report = HealthReport()
        for name, port in internal_services:
            logger.info("Checking %s at VM101:%d", name, port)
            check = self.check_internal(name, port, timeout=timeout)
            report.checks.append(check)
        return report

    def check_prometheus_health(self) -> ServiceCheck:
        """Dedicated check for Prometheus with its /-/healthy endpoint."""
        return self.check_url(
            f"{self.config.prometheus_host}/-/healthy",
            "Prometheus",
            timeout=10,
        )

    def check_langfuse_health(self) -> ServiceCheck:
        """Dedicated check for Langfuse API health endpoint."""
        return self.check_url(
            f"{self.config.langfuse.host}/api/public/health",
            "Langfuse",
            timeout=10,
        )
