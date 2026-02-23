.PHONY: help up down logs psql api test lint

help:
	@echo "Targets:"
	@echo "  up     - Levanta Postgres + MCP server"
	@echo "  down   - Baja servicios"
	@echo "  logs   - Logs de servicios"
	@echo "  psql   - Entra a psql dentro del contenedor"
	@echo "  api    - Abre el endpoint /health"
	@echo "  test   - Ejecuta tests (placeholder)"
	@echo "  lint   - Placeholder lint"

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

psql:
	docker exec -it genesis-postgres psql -U $${POSTGRES_USER:-genesis} -d $${POSTGRES_DB:-genesis}

api:
	@echo "Health:"
	@curl -s http://localhost:$${API_PORT_HOST:-8080}/health | python -m json.tool

test:
	@echo "TODO: agregar tests (pytest) dentro de services/mcp_server"

lint:
	@echo "TODO: agregar ruff/black/mypy si lo deseas"
