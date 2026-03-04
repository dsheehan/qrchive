# Use the official uv image with Python 3.14
FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

# Set working directory
WORKDIR /app

# Create a non-root user and set ownership of /app
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g 1000 -m appuser && \
    chown appuser:appuser /app

# Install dependencies using a cache mount for faster builds
# and keep the environment in /app/.venv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/home/appuser/.cache/uv

# Create data directory at the root and set permissions (needs root)
USER root
RUN mkdir -p /data && chown appuser:appuser /data
USER appuser

# Copy dependency files first for better caching
COPY --chown=appuser:appuser pyproject.toml package.json ./

# Install dependencies
RUN --mount=type=cache,target=/home/appuser/.cache/uv,uid=1000,gid=1000 \
    uv sync --no-dev

# Copy the rest of the application
COPY --chown=appuser:appuser src/ ./src/

# Copy initial data to the root data directory (needs root to write to /data)
USER root
COPY --chown=appuser:appuser data/ /data/
USER appuser

# Expose the port the app runs on
EXPOSE 5000

# Health check using the new /health endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Set environment variables for Flask and data path
ENV FLASK_APP=src/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV MATTER_DATA_PATH=/data/matter.csv

# Run the application
CMD ["uv", "run", "flask", "run"]
