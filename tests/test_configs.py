"""
test_configs.py - Validate configuration files for G_SV_Agent.

Tests that YAML config files are syntactically valid and contain expected keys.
"""

import os
import sys
import pytest

# Ensure pyyaml is available; it ships with most Python distributions
yaml = pytest.importorskip("yaml")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestDockerCompose:
    """Validate docker-compose.yml structure."""

    @pytest.fixture(autouse=True)
    def load_compose(self):
        compose_path = os.path.join(PROJECT_ROOT, "docker-compose.yml")
        assert os.path.exists(compose_path), "docker-compose.yml must exist"
        with open(compose_path, "r", encoding="utf-8") as f:
            self.compose = yaml.safe_load(f)

    def test_compose_is_dict(self):
        assert isinstance(self.compose, dict)

    def test_services_key_exists(self):
        assert "services" in self.compose

    def test_services_is_dict(self):
        assert isinstance(self.compose["services"], dict)

    def test_postgres_service_defined(self):
        assert "postgres" in self.compose["services"]

    def test_postgres_has_image(self):
        pg = self.compose["services"]["postgres"]
        assert "image" in pg

    def test_postgres_has_healthcheck(self):
        pg = self.compose["services"]["postgres"]
        assert "healthcheck" in pg

    def test_mcp_server_service_defined(self):
        assert "mcp-server" in self.compose["services"]

    def test_mcp_server_depends_on_postgres(self):
        mcp = self.compose["services"]["mcp-server"]
        assert "depends_on" in mcp
        deps = mcp["depends_on"]
        assert "postgres" in deps

    def test_volumes_section_exists(self):
        assert "volumes" in self.compose


class TestPoliciesYaml:
    """Validate configs/policies.yml structure."""

    @pytest.fixture(autouse=True)
    def load_policies(self):
        policies_path = os.path.join(PROJECT_ROOT, "configs", "policies.yml")
        assert os.path.exists(policies_path), "configs/policies.yml must exist"
        with open(policies_path, "r", encoding="utf-8") as f:
            self.policies = yaml.safe_load(f)

    def test_policies_is_dict(self):
        assert isinstance(self.policies, dict)

    def test_project_defaults_exists(self):
        assert "project_defaults" in self.policies

    def test_allowed_models_is_list(self):
        defaults = self.policies["project_defaults"]
        assert "allowed_models" in defaults
        assert isinstance(defaults["allowed_models"], list)
        assert len(defaults["allowed_models"]) > 0

    def test_skills_section_exists(self):
        assert "skills" in self.policies


class TestProjectStructure:
    """Validate essential project files exist."""

    def test_dockerfile_exists_for_mcp_server(self):
        dockerfile = os.path.join(
            PROJECT_ROOT, "services", "mcp_server", "Dockerfile"
        )
        assert os.path.exists(dockerfile)

    def test_requirements_exists_for_mcp_server(self):
        reqs = os.path.join(
            PROJECT_ROOT, "services", "mcp_server", "requirements.txt"
        )
        assert os.path.exists(reqs)

    def test_makefile_exists(self):
        makefile = os.path.join(PROJECT_ROOT, "Makefile")
        assert os.path.exists(makefile)

    def test_docker_init_dir_exists(self):
        init_dir = os.path.join(PROJECT_ROOT, "docker", "postgres", "init")
        assert os.path.isdir(init_dir)
