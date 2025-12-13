"""CLI entry point for FastMCP Template Server.

Usage:
    uvx fastmcp-template stdio           # Local CLI mode (Claude Desktop)
    uvx fastmcp-template sse             # SSE server mode (deprecated)
    uvx fastmcp-template streamable-http # Streamable HTTP (recommended for remote)

Environment Variables:
    FASTMCP_PORT: Server port for HTTP modes (default: 8000)
    FASTMCP_HOST: Server host for HTTP modes (default: 0.0.0.0)
    CACHE_BACKEND: Cache backend - memory, sqlite, redis (default: auto)
    REDIS_URL: Redis connection URL (default: redis://localhost:6379)
    LANGFUSE_PUBLIC_KEY: Langfuse public key (optional)
    LANGFUSE_SECRET_KEY: Langfuse secret key (optional)
"""

import os
import sys

import typer

app = typer.Typer(
    name="fastmcp-template",
    help="FastMCP Template Server with RefCache and Langfuse Tracing",
    add_completion=False,
)


def _get_host() -> str:
    """Get server host from environment."""
    return os.environ.get("FASTMCP_HOST", "0.0.0.0")  # nosec B104 - intentional for Docker


def _get_port() -> int:
    """Get server port from environment."""
    return int(os.environ.get("FASTMCP_PORT", "8000"))


def _print_startup_info(transport: str) -> None:
    """Print startup information."""
    from .tracing import is_langfuse_enabled

    typer.echo(f"Transport: {transport}")
    typer.echo(
        f"Langfuse tracing: {'enabled' if is_langfuse_enabled() else 'disabled'}"
    )
    typer.echo("Context propagation: enabled (user_id, session_id, metadata)")


def _handle_shutdown() -> None:
    """Handle graceful shutdown."""
    from .tracing import flush_traces

    typer.echo("\nShutting down server...")
    flush_traces()
    typer.echo("Service stopped.")


@app.command()
def stdio() -> None:
    """Start server in stdio mode (for Claude Desktop and local CLI).

    This is the recommended mode for local usage with Claude Desktop
    or other MCP clients that communicate via stdin/stdout.

    Cache backend defaults to SQLite for persistence across sessions.
    """
    from .server import mcp

    _print_startup_info("stdio")

    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        pass
    except Exception as error:
        typer.echo(f"\nError: {error}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        _handle_shutdown()


@app.command()
def sse(
    host: str = typer.Option(None, "--host", "-h", help="Server host"),
    port: int = typer.Option(None, "--port", "-p", help="Server port"),
) -> None:
    """Start server in SSE mode (Server-Sent Events).

    Note: SSE transport is deprecated. Use streamable-http for new deployments.

    Cache backend defaults to Redis for distributed deployments.
    """
    from .server import mcp

    server_host = host or _get_host()
    server_port = port or _get_port()

    _print_startup_info("sse")
    typer.echo(f"Server: http://{server_host}:{server_port}/sse")
    typer.secho(
        "Warning: SSE transport is deprecated. Use streamable-http instead.",
        fg=typer.colors.YELLOW,
    )

    try:
        mcp.run(transport="sse", host=server_host, port=server_port)
    except KeyboardInterrupt:
        pass
    except Exception as error:
        typer.echo(f"\nError: {error}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        _handle_shutdown()


@app.command("streamable-http")
def streamable_http(
    host: str = typer.Option(None, "--host", "-h", help="Server host"),
    port: int = typer.Option(None, "--port", "-p", help="Server port"),
) -> None:
    """Start server in streamable HTTP mode (recommended for remote).

    This is the recommended mode for remote deployments, Docker containers,
    and any scenario where the client connects over HTTP.

    Cache backend defaults to Redis for distributed deployments.
    """
    from .server import mcp

    server_host = host or _get_host()
    server_port = port or _get_port()

    _print_startup_info("streamable-http")
    typer.echo(f"Server: http://{server_host}:{server_port}/mcp")

    try:
        mcp.run(transport="streamable-http", host=server_host, port=server_port)
    except KeyboardInterrupt:
        pass
    except Exception as error:
        typer.echo(f"\nError: {error}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        _handle_shutdown()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version and exit"
    ),
) -> None:
    """FastMCP Template Server with RefCache and Langfuse Tracing.

    A production-ready MCP server template demonstrating best practices
    for building Model Context Protocol servers with caching and observability.
    """
    if version:
        from . import __version__

        typer.echo(f"fastmcp-template {__version__}")
        raise typer.Exit()

    # If no command provided, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


if __name__ == "__main__":
    app()
