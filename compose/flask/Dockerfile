FROM python:3.12-slim

# build target: either `webserver` or `deploy`. This is used to determine whether to
# install git and to select the dependency group to sync.
ARG BUILD_TARGET=webserver

# Validate the BUILD_TARGET argument.
RUN if [ "${BUILD_TARGET}" = "webserver" ] || [ "${BUILD_TARGET}" = "deploy" ]; then \
    echo "BUILD_TARGET: ${BUILD_TARGET}"; \
  else \
    echo "Invalid BUILD_TARGET: ${BUILD_TARGET}. Must be 'webserver' or 'deploy'." \
    && exit 1 ; \
  fi

# Install git if the build target is `deploy`. It's needed to install some dependencies.
RUN if [ "${BUILD_TARGET}" = "deploy" ]; then \
    apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* ; \
  fi

# use intermediate layers following these guidelines:
# https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Use `/app` as the application's working directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --group="${BUILD_TARGET}"

# Copy the project into the image
ADD . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --group="${BUILD_TARGET}"

# Install the API server - this should be in pyproject.toml, but I couldn't get it to work
RUN uv pip install -e api/server

# use the virtual environment created by uv so we don't have to prefix every command with `uv run`
ENV PATH="/app/.venv/bin:$PATH"

# Copy the entrypoint script into the image, which runs the server
COPY compose/flask/runserver /runserver
RUN chmod +x /runserver

CMD ["/runserver"]
