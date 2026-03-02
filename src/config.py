"""
Configuration loader for G_SV_Agent.

Loads settings from .env files and environment variables.
Provides typed access to all infrastructure configuration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


def _load_dotenv(env_path: Path) -> dict[str, str]:
    """Parse a .env file into a dictionary. Skips comments and blank lines."""
    result: dict[str, str] = {}
    if not env_path.exists():
        return result
    with open(env_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            result[key] = value
    return result


@dataclass
class PostgresConfig:
    """Postgres connection settings."""
    db: str = "genesis"
    user: str = "genesis"
    password: str = "genesis_dev_password"
    host: str = "postgres"
    port: int = 5432

    @property
    def dsn(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


@dataclass
class SSHConfig:
    """SSH jump-host settings for reaching VM101 through Proxmox."""
    proxmox_ip: str = "65.21.233.178"
    proxmox_user: str = "root"
    vm_ip: str = "10.10.10.101"
    vm_user: str = "matias"


@dataclass
class LangfuseConfig:
    """Langfuse LLM observability settings."""
    public_key: str = ""
    secret_key: str = ""
    host: str = "https://langfuse.imedicina.cl"

    @property
    def is_configured(self) -> bool:
        return bool(self.public_key and self.secret_key
                    and "CHANGEME" not in self.public_key)


@dataclass
class Config:
    """
    Central configuration for G_SV_Agent.

    Usage::

        config = Config.load()         # loads from .env in project root
        config = Config.load("/path/to/.env")
        print(config.postgres.dsn)
        print(config.ssh.proxmox_ip)
        print(config.langfuse.is_configured)
    """

    postgres: PostgresConfig = field(default_factory=PostgresConfig)
    ssh: SSHConfig = field(default_factory=SSHConfig)
    langfuse: LangfuseConfig = field(default_factory=LangfuseConfig)

    api_host: str = "0.0.0.0"
    api_port: int = 8080
    log_level: str = "INFO"

    embedding_provider: str = "dummy"
    embedding_dim: int = 1536
    default_project: str = "local-dev"

    prometheus_host: str = "https://prometheus.imedicina.cl"
    prometheus_port: int = 9090

    tailscale_auth_key: Optional[str] = None

    @classmethod
    def load(cls, env_path: Optional[str] = None) -> "Config":
        """
        Load configuration from a .env file and/or environment variables.

        Environment variables take precedence over .env file values.

        Args:
            env_path: Path to .env file. Defaults to project root .env.

        Returns:
            A fully populated Config instance.
        """
        if env_path is None:
            project_root = Path(__file__).resolve().parent.parent
            env_file = project_root / ".env"
        else:
            env_file = Path(env_path)

        file_vars = _load_dotenv(env_file)

        def get(key: str, default: str = "") -> str:
            """Get value from env vars first, then .env file, then default."""
            return os.environ.get(key, file_vars.get(key, default))

        postgres = PostgresConfig(
            db=get("POSTGRES_DB", "genesis"),
            user=get("POSTGRES_USER", "genesis"),
            password=get("POSTGRES_PASSWORD", "genesis_dev_password"),
            host=get("POSTGRES_HOST", "postgres"),
            port=int(get("POSTGRES_PORT", "5432")),
        )

        ssh = SSHConfig(
            proxmox_ip=get("PROXMOX_IP", "65.21.233.178"),
            proxmox_user=get("PROXMOX_SSH_USER", "root"),
            vm_ip=get("VM_SERVICES_IP", "10.10.10.101"),
            vm_user=get("VM_SERVICES_USER", "matias"),
        )

        langfuse = LangfuseConfig(
            public_key=get("LANGFUSE_PUBLIC_KEY", ""),
            secret_key=get("LANGFUSE_SECRET_KEY", ""),
            host=get("LANGFUSE_HOST", "https://langfuse.imedicina.cl"),
        )

        tailscale_key = get("TAILSCALE_AUTH_KEY", "") or None
        if tailscale_key and "CHANGEME" in tailscale_key:
            tailscale_key = None

        return cls(
            postgres=postgres,
            ssh=ssh,
            langfuse=langfuse,
            api_host=get("API_HOST", "0.0.0.0"),
            api_port=int(get("API_PORT", "8080")),
            log_level=get("LOG_LEVEL", "INFO"),
            embedding_provider=get("EMBEDDING_PROVIDER", "dummy"),
            embedding_dim=int(get("EMBEDDING_DIM", "1536")),
            default_project=get("DEFAULT_PROJECT_NAME", "local-dev"),
            prometheus_host=get("PROMETHEUS_HOST", "https://prometheus.imedicina.cl"),
            prometheus_port=int(get("PROMETHEUS_PORT", "9090")),
            tailscale_auth_key=tailscale_key,
        )

    def summary(self) -> str:
        """Return a human-readable summary of the configuration (secrets redacted)."""
        lines = [
            "G_SV_Agent Configuration",
            "========================",
            f"  Postgres:    {self.postgres.host}:{self.postgres.port}/{self.postgres.db}",
            f"  SSH Target:  {self.ssh.proxmox_user}@{self.ssh.proxmox_ip} -> {self.ssh.vm_user}@{self.ssh.vm_ip}",
            f"  API:         {self.api_host}:{self.api_port} (log_level={self.log_level})",
            f"  Langfuse:    {'configured' if self.langfuse.is_configured else 'NOT configured'}",
            f"  Prometheus:  {self.prometheus_host}:{self.prometheus_port}",
            f"  Tailscale:   {'configured' if self.tailscale_auth_key else 'NOT configured'}",
            f"  Embeddings:  {self.embedding_provider} (dim={self.embedding_dim})",
        ]
        return "\n".join(lines)
