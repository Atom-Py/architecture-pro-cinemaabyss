FROM python:3.14-slim-bookworm AS python-stage
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  UV_PROJECT_ENVIRONMENT=/app/.venv
RUN useradd --system --uid 1000 --user-group --no-create-home app
WORKDIR /app


FROM python-stage AS uv-stage
ENV UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /usr/local/bin/
COPY pyproject.toml uv.lock ./


FROM uv-stage AS dependencies-stage
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-install-project --no-dev


FROM python-stage AS app-stage
ENV PYTHONPATH=/app/src
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml ./
COPY --from=dependencies-stage /app/.venv .venv/
COPY src/ src/
EXPOSE 8000
USER app
CMD [".venv/bin/python", "src/web/main.py"]
