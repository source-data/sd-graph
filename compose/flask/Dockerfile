FROM python:3.11-slim

# build target: either `webserver` or `deploy`. This is used to determine whether to
# install git and to select the dependency group to sync.
ARG BUILD_TARGET=webserver

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Use `/app` as the application's working directory
WORKDIR /app

# Install build dependencies:
# git for building git-based dependencies: ai, hypothepy, smtag
# libgmp-dev, libmpfr-dev, and libmpc-dev for building cdlib
# the rest for building tokenizers (transitive dependency through smtag -> transformers)
ARG BUILD_PACKAGES="git build-essential curl libssl-dev openssl pkg-config"
ARG RUN_PACKAGES="libgmp-dev libmpfr-dev libmpc-dev"
RUN if [ "${BUILD_TARGET}" = "deploy" ]; then \
  apt-get update \
  && apt-get install -y --no-install-recommends ${BUILD_PACKAGES} ${RUN_PACKAGES} \
  # install rust, also for building tokenizers
  && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y ; \
fi
# Set rust environment variables
ENV PATH="/root/.cargo/bin:$PATH"

# Install dependencies using intermediate layers following these guidelines:
# https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --group="${BUILD_TARGET}"

# Uninstall build dependencies
RUN if [ "${BUILD_TARGET}" = "deploy" ]; then \
  apt-get purge -y --auto-remove ${BUILD_PACKAGES} \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && rustup self uninstall -y ; \
fi

# Copy the project into the image
ADD . /app

# Install dependencies
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
