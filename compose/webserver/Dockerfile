FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ADD . /app
WORKDIR /app
RUN uv sync --locked --group=webserver
RUN uv pip install -e api/server

COPY compose/webserver/entrypoint /entrypoint
RUN chmod +x /entrypoint

ENTRYPOINT ["/entrypoint"]
