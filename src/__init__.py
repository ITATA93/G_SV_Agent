"""
G_SV_Agent -- Server Agent for GEN_OS infrastructure management.

Manages Docker containers, Hetzner VM deployments, service health checks,
and infrastructure automation for the Antigravity ecosystem.

Modules:
    agent   - ServerAgent class for service orchestration
    health  - Health check utilities for all 22+ services
    config  - Configuration loader from .env files
"""

__version__ = "0.1.0"
__project__ = "G_SV_Agent"

from src.config import Config
from src.agent import ServerAgent
from src.health import HealthChecker

__all__ = ["Config", "ServerAgent", "HealthChecker"]
