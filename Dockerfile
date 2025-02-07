# Use a Python image and install uv manually
FROM python:3.13-slim AS builder

# Install dependencies for uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download and install uv, then remove installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure uv binary is on PATH
ENV PATH="/root/.local/bin/:$PATH"

# Set working directory
WORKDIR /fast

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from cache instead of linking
ENV UV_LINK_MODE=copy

# Install project dependencies using lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, add the project source code and install it
# Installing separately from dependencies allows optimal layer caching
COPY alembic alembic
COPY app app
COPY alembic.ini alembic.ini
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Clean up
RUN rm -rf /root/.cache /var/lib/apt/lists/* /tmp/*

# Start again with a lightweight image
FROM python:3.13-slim

# Copy only necessary files from builder stage
COPY --from=builder /fast /fast

# Working directory is also /fast
WORKDIR /fast

# Place venv executables at front of PATH
ENV PATH="/fast/.venv/bin:$PATH"

# Reset entrypoint
ENTRYPOINT []

# Run Alembric migrations (if any) and start FastAPI server
# Use `--host 0.0.0.0` to allow access from outside container
CMD ["bash", "-c", "alembic upgrade head && fastapi run app/main.py --host 0.0.0.0 --port 8080"]
