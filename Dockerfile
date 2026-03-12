FROM python:3.12-slim-bookworm AS base

FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY uv.lock pyproject.toml /app/


FROM builder AS prod-base
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev


FROM builder AS test-base
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-install-project --group dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --group dev


FROM base AS prod
COPY --from=prod-base /app/.venv /app/.venv
COPY --from=prod-base /app/app /app/app
COPY --from=prod-base /app/alembic.ini /app/alembic.ini
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

FROM base AS test
COPY --from=test-base /app/.venv /app/.venv
COPY --from=test-base /app/app /app/app
COPY --from=test-base /app/alembic.ini /app/alembic.ini
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
ENV ENV="test"
