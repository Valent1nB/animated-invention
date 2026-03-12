precommit:
	uv run detect-secrets scan > .secrets.baseline # pragma: allowlist secret
	uv run pre-commit run --all-files

detect-secrets:
	uv run detect-secrets scan > .secrets.baseline # pragma: allowlist secret

up:
	docker compose up postgres backend

up-db:
	docker compose up postgres


build:
	docker compose build

test:
	docker compose up postgres test

lint:
	uv run ruff check --fix --force-exclude
	uv run ruff format --force-exclude
	uv run mypy .

migration:
	uv run alembic revision --autogenerate -m "$(m)"

migrate:
	uv run alembic upgrade head
