# --- Build stage: create .venv with all dependencies ---
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

# Install base tools and curl for uv installer
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject and lockfile
COPY pyproject.toml uv.lock ./

# Download the latest uv installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer and remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure uv binary is on PATH
ENV PATH="/root/.local/bin:$PATH"

# Create and sync a virtual environment into .venv inside app dir (to match runtime path expectations)
RUN --mount=type=ssh uv venv .venv \
    && uv sync --python=.venv/bin/python --no-dev

# --- Production stage ---
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy prebuilt venv from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . .

# Create a non-root user
RUN useradd --no-create-home --home-dir /app appuser && \
    chown -R  appuser /app && \
    chmod -R u+rwX /app

USER appuser

# Activate virtual environment
ENV PATH="/app/.venv/bin:$PATH"

CMD ["sh", "./script/start.sh"]
