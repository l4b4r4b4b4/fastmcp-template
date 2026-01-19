# Task 01: CLI Framework & Project Setup

**Status:** ⚪ Not Started
**Created:** 2025-01-08
**Last Updated:** 2025-01-08

---

## Objective

Create the foundational package structure and CLI interface for the fastmcp-create scaffolding tool. This includes setting up the Python package, implementing the basic command-line interface using Typer, and establishing the project architecture that subsequent tasks will build upon.

---

## Context & Research

### Similar Tools Analysis

**create-react-app:**
- Single command: `npx create-react-app my-app`
- Interactive prompts for configuration
- Progress indicators during setup
- Clear success/error messages

**cookiecutter:**
- Template-based project generation
- JSON configuration for variables
- Extensive validation
- Git repository support

**copier:**
- Modern alternative to cookiecutter
- Update existing projects from templates
- Migration system for template changes
- YAML configuration

**Key Takeaways:**
- Users expect single-command simplicity
- Interactive prompts should have sensible defaults
- Progress feedback is essential
- Clear error messages with actionable solutions

---

## Implementation Plan

### 1. Package Structure Setup

```
fastmcp-create/
├── README.md
├── LICENSE
├── pyproject.toml
├── .gitignore
├── src/
│   └── fastmcp_create/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── scaffold.py
│       ├── cleanup.py
│       ├── templates.py
│       ├── config.py
│       └── utils.py
└── tests/
    ├── __init__.py
    ├── test_cli.py
    ├── test_config.py
    └── fixtures/
        └── sample_template/
```

**Key Files:**

**`pyproject.toml`:**
```toml
[project]
name = "fastmcp-create"
version = "0.1.0"
description = "Scaffolding tool for FastMCP template projects"
authors = [{name = "Your Name", email = "you@example.com"}]
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
dependencies = [
    "typer[all]>=0.9.0",
    "rich>=13.0.0",
    "jinja2>=3.1.0",
    "tomli>=2.0.0; python_version < '3.11'",
    "tomli-w>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=6.0.0",
    "ruff>=0.8.0",
    "mypy>=1.8.0",
]

[project.scripts]
fastmcp-create = "fastmcp_create.cli:app"
fastmcp-init = "fastmcp_create.cli:init_app"

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "RUF"]
ignore = ["E501"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=fastmcp_create --cov-report=term-missing"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**`__init__.py`:**
```python
"""FastMCP Template Scaffolding Tool.

Automates the cleanup and customization of fastmcp-template
for new MCP server projects.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
```

**`__main__.py`:**
```python
"""CLI entry point for fastmcp-create."""

from fastmcp_create.cli import app

if __name__ == "__main__":
    app()
```

---

### 2. CLI Interface with Typer

**`cli.py` - Main CLI Application:**

```python
"""Command-line interface for fastmcp-create."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel

from fastmcp_create.config import ProjectConfig
from fastmcp_create.scaffold import scaffold_project

app = typer.Typer(
    name="fastmcp-create",
    help="Create a new FastMCP server project from the template.",
    add_completion=False,
)

init_app = typer.Typer(
    name="fastmcp-init",
    help="Initialize FastMCP template in the current directory.",
    add_completion=False,
)

console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        from fastmcp_create import __version__
        console.print(f"fastmcp-create version {__version__}")
        raise typer.Exit()


@app.command()
def create(
    project_name: Annotated[
        str,
        typer.Argument(help="Name of the project to create"),
    ],
    description: Annotated[
        Optional[str],
        typer.Option("--description", "-d", help="Project description"),
    ] = None,
    author: Annotated[
        Optional[str],
        typer.Option("--author", "-a", help="Author name and email"),
    ] = None,
    server_type: Annotated[
        str,
        typer.Option(
            "--type", "-t",
            help="Server type: stdio, http, or both",
        ),
    ] = "stdio",
    no_git: Annotated[
        bool,
        typer.Option("--no-git", help="Skip git initialization"),
    ] = False,
    no_install: Annotated[
        bool,
        typer.Option("--no-install", help="Skip dependency installation"),
    ] = False,
    template_source: Annotated[
        Optional[str],
        typer.Option(
            "--template",
            help="Template source (git URL or local path)",
        ),
    ] = None,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
) -> None:
    """Create a new FastMCP server project.

    Creates a new directory with the project name, clones the
    fastmcp-template, removes demo tools, and configures the
    project with your settings.

    Examples:
        fastmcp-create my-mcp-server
        fastmcp-create my-server --description "My API" --author "Me <me@example.com>"
        fastmcp-create my-server --type http --no-git
    """
    console.print(
        Panel.fit(
            "🚀 [bold cyan]FastMCP Project Creator[/bold cyan]",
            border_style="cyan",
        )
    )

    # Interactive prompts if values not provided
    if description is None:
        description = typer.prompt(
            "Project description",
            default="A FastMCP server",
        )

    if author is None:
        author = typer.prompt(
            "Author (name <email>)",
            default="",
        )

    # Validate server type
    if server_type not in ("stdio", "http", "both"):
        console.print(
            "[red]Error:[/red] Server type must be 'stdio', 'http', or 'both'"
        )
        raise typer.Exit(1)

    # Build configuration
    config = ProjectConfig(
        project_name=project_name,
        project_title=_title_case(project_name),
        description=description,
        author=author,
        server_type=server_type,
        init_git=not no_git,
        install_deps=not no_install,
        template_source=template_source or _default_template_source(),
    )

    # Validate project name
    if not _is_valid_project_name(project_name):
        console.print(
            f"[red]Error:[/red] Invalid project name '{project_name}'"
        )
        console.print(
            "Project name must be a valid Python package name "
            "(lowercase, alphanumeric, underscores only)"
        )
        raise typer.Exit(1)

    # Check if directory already exists
    project_path = Path.cwd() / project_name
    if project_path.exists():
        console.print(
            f"[red]Error:[/red] Directory '{project_name}' already exists"
        )
        raise typer.Exit(1)

    # Execute scaffolding
    try:
        scaffold_project(config, project_path, console)

        console.print()
        console.print(
            Panel.fit(
                f"✨ [bold green]Success![/bold green]\n\n"
                f"Your FastMCP server is ready in [cyan]{project_name}/[/cyan]\n\n"
                f"Next steps:\n"
                f"  [cyan]cd {project_name}[/cyan]\n"
                f"  [cyan]uv run pytest[
