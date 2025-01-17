FROM python:3.13-slim-bookworm

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Define an environment variable for the working directory
ENV BASE=/fast

WORKDIR $BASE

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --verbose

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . $BASE
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --verbose

# Place executables in the environment at the front of the path
ENV PATH="$BASE/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Run the FastAPI application by default
# Uses `--host 0.0.0.0` to allow access from outside the container
CMD ["bash", "-c", "alembic upgrade head && fastapi run app/main.py --host 0.0.0.0 --port 8080"]
