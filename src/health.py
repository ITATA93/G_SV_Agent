"""
Health check utilities for GEN_OS services.

Provides programmatic health checking for all services running on VM100/VM101
and accessible via the imedicina.cl reverse proxy. Can check services both
via HTTPS (external) and via SSH to VMs (internal ports).

Service definitions are loaded from configs/services.yml (Single Source of Truth).
"""

from __future__ import annotations

import subprocess
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from src.config import Config

logger = logging.getLogger(__name__)

# Path to the canonical service registry
_SERVICES_YAML = Path(__file__).resolve().parent.parent / "configs" / "services.yml"


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
# Load service definitions from configs/services.yml
# ---------------------------------------------------------------

def _parse_yaml_simple(path: Path) -> list[dict]:
    """Parse the services YAML without requiring PyYAML.

    Handles the flat list-of-dicts structure used in configs/services.yml.
    Falls back gracefully if the file is missing.
    """
    if not path.exists():
        logger.warning("services.yml not found at %s — using empty list", path)
        return []

    services: list[dict] = []
    current: dict | None = None
    text = path.read_text(encoding="utf-8")

    for line in text.splitlines():
        stripped = line.strip()
        # Skip comments and blank lines
        if not stripped or stripped.startswith("#"):
            continue
        # New list item
        if stripped.startswith("- "):
            if current is not None:
                services.append(current)
            current = {}
            # The first key-value pair is on the same line as "- "
            kv = stripped[2:].strip()
            if ":" in kv:
                key, val = kv.split(":", 1)
                current[key.strip()] = _parse_yaml_value(val.strip())
        elif ":" in stripped and current is not None:
            key, val = stripped.split(":", 1)
            current[key.strip()] = _parse_yaml_value(val.strip())

    if current is not None:
        services.append(current)

    return services


def _parse_yaml_value(val: str):
    """Convert a YAML scalar value to a Python type."""
    if not val or val == "null":
        return None
    if val in ("true", "True"):
        return True
    if val in ("false", "False"):
        return False
    # Remove surrounding quotes
    if (val.startswith('"') and val.endswith('"')) or \
       (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    # Try int
    try:
        return int(val)
    except ValueError:
        pass
    return val


def load_services(path: Path | None = None) -> list[dict[str, str]]:
    """Load the service catalog from configs/services.yml.

    Returns a list of dicts with at least: name, url (url_external), category.
    Services without an external URL (e.g. ClickHouse) are included with url=None.
    Only deployed services are included.
    """
    if path is None:
        path = _SERVICES_YAML

    try:
        import yaml  # type: ignore[import-untyped]
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    except ImportError:
        raw = _parse_yaml_simple(path)
    except Exception as exc:
        logger.warning("Failed to load services.yml via PyYAML: %s — trying simple parser", exc)
        raw = _parse_yaml_simple(path)

    if not raw:
        return []

    services = []
    for entry in raw:
        if not entry.get("deployed", True):
            continue
        services.append({
            "name": entry.get("name", "unknown"),
            "url": entry.get("url_external") or "",
            "category": entry.get("category", "Other"),
            "port_internal": entry.get("port_internal"),
            "vm": entry.get("vm"),
            "container": entry.get("container"),
        })
    return services


def load_internal_services(path: Path | None = None) -> list[tuple[str, int]]:
    """Load services with internal ports for SSH-based health checks.

    Returns list of (name, port) tuples for all deployed services with a port_internal.
    """
    all_services = load_services(path)
    result = []
    for svc in all_services:
        port = svc.get("port_internal")
        if port and isinstance(port, int):
            result.append((svc["name"], port))
    return result


# Module-level SERVICES loaded at import time for backward compatibility
SERVICES: list[dict[str, str]] = load_services()


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

        Only checks services that have an external URL.

        Args:
            timeout: Per-service timeout in seconds.

        Returns:
            A HealthReport with results for all services.
        """
        report = HealthReport()
        for svc in SERVICES:
            if not svc.get("url"):
                continue
            logger.info("Checking %s at %s", svc["name"], svc["url"])
            check = self.check_url(svc["url"], svc["name"], timeout=timeout)
            report.checks.append(check)
        return report

    def check_all_internal(self, timeout: int = 10) -> HealthReport:
        """
        Check services via SSH to VM internal ports.

        Loads port mappings from configs/services.yml.

        Args:
            timeout: Per-service timeout in seconds.

        Returns:
            A HealthReport with results for checked services.
        """
        internal_services = load_internal_services()
        report = HealthReport()
        for name, port in internal_services:
            logger.info("Checking %s at VM:%d", name, port)
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
