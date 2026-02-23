from __future__ import annotations

import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    postgres_db: str = os.getenv("POSTGRES_DB", "genesis")
    postgres_user: str = os.getenv("POSTGRES_USER", "genesis")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "genesis_dev_password")
    postgres_host: str = os.getenv("POSTGRES_HOST", "postgres")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))

    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8080"))

    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "dummy")
    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "1536"))

    default_project_name: str = os.getenv("DEFAULT_PROJECT_NAME", "local-dev")

    @property
    def dsn(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

settings = Settings()
