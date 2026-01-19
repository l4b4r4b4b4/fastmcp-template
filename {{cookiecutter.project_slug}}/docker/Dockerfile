# {{ cookiecutter.project_name }} - Production Dockerfile
# Extends the base image with the template application
#
# Build: docker build -f docker/Dockerfile -t {{ cookiecutter.project_slug }}:latest .
# Run:   docker run -p 8000:8000 {{ cookiecutter.project_slug }}:latest
#
# The server uses streamable-http transport (recommended for remote/Docker).
# Configure via environment variables:
#   FASTMCP_PORT: Server port (default: 8000)
#   FASTMCP_HOST: Server host (default: 0.0.0.0)
#   CACHE_BACKEND: Cache backend - memory, sqlite, redis (default: redis for HTTP)
#   REDIS_URL: Redis connection URL (default: redis://localhost:6379)

# Build argument for Python version (must match base image)
ARG PYTHON_VERSION=3.12
ARG BASE_IMAGE=ghcr.io/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}-base:latest

# ==============================================================================
# Production Runtime
# ==============================================================================
FROM ${BASE_IMAGE} AS production

# Copy application code
COPY --chown=appuser:appuser app/ /app/app/

# Default: Run MCP server with streamable-http transport (recommended for remote)
CMD ["python", "-m", "app", "streamable-http"]

# ==============================================================================
# Development Runtime (with source mounting support)
# ==============================================================================
FROM ${BASE_IMAGE} AS development

# Install dev dependencies (if base doesn't include them)
# This stage is meant for docker-compose volume mounts

# Copy application code
COPY --chown=appuser:appuser app/ /app/app/

# Dev mode - can override with volume mount
CMD ["python", "-m", "app", "streamable-http"]
