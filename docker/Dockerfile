# FastMCP Template - Production Dockerfile
# Extends the base image with the template application
#
# Build: docker build -f docker/Dockerfile -t fastmcp-template:latest .
# Run:   docker run -p 8000:8000 fastmcp-template:latest
#
# The server uses streamable-http transport (recommended for remote/Docker).
# Configure via environment variables:
#   FASTMCP_PORT: Server port (default: 8000)
#   FASTMCP_HOST: Server host (default: 0.0.0.0)
#   CACHE_BACKEND: Cache backend - memory, sqlite, redis (default: redis for HTTP)
#   REDIS_URL: Redis connection URL (default: redis://localhost:6379)

ARG BASE_IMAGE=ghcr.io/l4b4r4b4b4/fastmcp-base:latest

# ==============================================================================
# Production Runtime
# ==============================================================================
FROM ${BASE_IMAGE} AS production

# Copy application code
COPY app/ /app/app/

# Default: Run MCP server with streamable-http transport (recommended for remote)
# Uses typer CLI via uv for consistent environment
CMD ["uv", "run", "fastmcp-template", "streamable-http"]

# ==============================================================================
# Development Runtime (with source mounting support)
# ==============================================================================
FROM ${BASE_IMAGE} AS development

# Install dev dependencies (if base doesn't include them)
# This stage is meant for docker-compose volume mounts

# Copy application code
COPY app/ /app/app/

# Dev mode - can override with volume mount
# Uses typer CLI via uv for consistent environment
CMD ["uv", "run", "fastmcp-template", "streamable-http"]
