FROM ghcr.io/astral-sh/uv:0.12.7 AS uv
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/srv/api/.venv/bin:${PATH}"

WORKDIR /srv/api
COPY --from=uv /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-cache
COPY alembic.ini ./
COPY app ./app
COPY alembic ./alembic

RUN groupadd --system --gid 10001 api \
    && useradd --system --uid 10001 --gid 10001 --no-create-home api
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--no-proxy-headers"]
