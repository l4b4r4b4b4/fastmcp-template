#!/usr/bin/env python3
"""Post-generation hook for FastMCP template.

This script runs after Cookiecutter generates the project and automates
common setup tasks like dependency installation and git initialization.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str, critical: bool = False) -> bool:
    """Run a command and return success status.

    Args:
        cmd: Command and arguments as list
        description: Human-readable description of the task
        critical: If True, exit on failure; if False, warn and continue

    Returns:
        True if command succeeded, False otherwise
    """
    print(f"→ {description}...")
    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )
        print(f"  ✓ {description} complete")
        return True
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        print(f"  ✗ {description} failed: {error_msg}")
        if critical:
            print("\nFatal error during project setup. Exiting.")
            sys.exit(1)
        return False
    except FileNotFoundError:
        print(f"  ✗ Command not found: {cmd[0]}")
        if critical:
            print(
                f"\nRequired tool '{cmd[0]}' not found. Please install it and try again."
            )
            sys.exit(1)
        return False


def check_command_exists(cmd: str) -> bool:
    """Check if a command is available in PATH."""
    try:
        subprocess.run(
            ["which", cmd],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main() -> None:
    """Run post-generation setup tasks."""
    project_slug = "{{ cookiecutter.project_slug }}"
    project_name = "{{ cookiecutter.project_name }}"
    extra_deps = "{{ cookiecutter.extra_dependencies }}".strip()
    extra_dev_deps = "{{ cookiecutter.extra_dev_dependencies }}".strip()
    create_github_repo = "{{ cookiecutter.create_github_repo }}"
    github_repo_visibility = "{{ cookiecutter.github_repo_visibility }}"
    github_username = "{{ cookiecutter.github_username }}"

    print("\n" + "=" * 70)
    print(f"Setting up '{project_name}'...")
    print("=" * 70 + "\n")

    # Track overall success
    warnings = []

    # Task 1: Install dependencies with uv
    if check_command_exists("uv"):
        if not run_command(["uv", "sync"], "Installing dependencies"):
            warnings.append("Dependency installation failed. Run 'uv sync' manually.")
        else:
            # Install extra dependencies if specified
            if extra_deps:
                deps_list = [d.strip() for d in extra_deps.split(",") if d.strip()]
                if deps_list:
                    if not run_command(
                        ["uv", "add", *deps_list],
                        f"Adding extra dependencies: {', '.join(deps_list)}",
                    ):
                        warnings.append(
                            f"Failed to add dependencies: {', '.join(deps_list)}"
                        )

            # Install extra dev dependencies if specified
            if extra_dev_deps:
                dev_deps_list = [
                    d.strip() for d in extra_dev_deps.split(",") if d.strip()
                ]
                if dev_deps_list:
                    if not run_command(
                        ["uv", "add", "--dev", *dev_deps_list],
                        f"Adding extra dev dependencies: {', '.join(dev_deps_list)}",
                    ):
                        warnings.append(
                            f"Failed to add dev dependencies: {', '.join(dev_deps_list)}"
                        )
    else:
        print("→ Installing dependencies...")
        print("  ✗ uv not found - skipping dependency installation")
        warnings.append(
            "uv not found. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
        )

    # Task 2: Initialize git repository
    git_available = check_command_exists("git")
    git_init_success = False

    if git_available:
        # Check if .git exists in current directory (not parent)
        git_dir = Path.cwd() / ".git"
        if git_dir.exists():
            print("→ Initializing Git repository...")
            print("  ⓘ Git repository already initialized in this directory")
            git_init_success = True
        else:
            # Initialize new git repo (even if inside another repo - nested repos are valid)
            if run_command(["git", "init"], "Initializing Git repository"):
                git_init_success = True
            else:
                warnings.append("Git initialization failed. Run 'git init' manually.")
    else:
        print("→ Initializing Git repository...")
        print("  ✗ git not found - skipping git initialization")
        warnings.append("git not found. Install it to use version control.")

    # Task 3: Create initial commit (only if git init succeeded)
    initial_commit_success = False
    if git_init_success:
        if run_command(["git", "add", "."], "Staging files"):
            if run_command(
                ["git", "commit", "-m", "Initial commit from FastMCP template"],
                "Creating initial commit",
            ):
                initial_commit_success = True

    # Task 4: Create GitHub repository (if requested and commit succeeded)
    if create_github_repo == "yes" and initial_commit_success:
        if check_command_exists("gh"):
            # Check if gh CLI is authenticated and get username
            print("→ Checking GitHub authentication...")
            try:
                auth_check = subprocess.run(
                    ["gh", "auth", "status"],
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=Path.cwd(),
                )

                # Try to get authenticated username
                try:
                    username_result = subprocess.run(
                        ["gh", "api", "user", "--jq", ".login"],
                        check=True,
                        capture_output=True,
                        text=True,
                        cwd=Path.cwd(),
                    )
                    detected_username = username_result.stdout.strip()
                    if detected_username:
                        github_username = detected_username
                except subprocess.CalledProcessError:
                    pass  # Use default from cookiecutter.json

                print("  ✓ GitHub CLI authenticated")

                # Create remote repository and push
                visibility_flag = f"--{github_repo_visibility}"
                repo_name = f"{github_username}/{project_slug}"
                if run_command(
                    [
                        "gh",
                        "repo",
                        "create",
                        project_slug,
                        visibility_flag,
                        "--source=.",
                        "--push",
                    ],
                    f"Creating {github_repo_visibility} GitHub repository '{repo_name}'",
                ):
                    print(f"  ✓ Repository URL: https://github.com/{repo_name}")
                else:
                    warnings.append(
                        f"Failed to create GitHub repo. Create manually: gh repo create {project_slug} {visibility_flag} --source=. --push"
                    )
            except subprocess.CalledProcessError:
                print("  ✗ GitHub CLI not authenticated")
                warnings.append(
                    "gh CLI not authenticated. Run 'gh auth login' to authenticate, then: "
                    f"gh repo create {project_slug} --{github_repo_visibility} --source=. --push"
                )
        else:
            print("→ Creating GitHub repository...")
            print("  ✗ gh CLI not found - skipping GitHub repository creation")
            warnings.append(
                "gh CLI not found. Install it with: brew install gh (macOS) or see https://cli.github.com"
            )
    elif create_github_repo == "yes" and not initial_commit_success:
        warnings.append(
            "Skipped GitHub repo creation because initial commit failed. Create repo manually after fixing git setup."
        )

    # Print success message
    print("\n" + "=" * 70)
    print(f"✓ Project '{project_name}' created successfully!")
    print("=" * 70 + "\n")

    # Print warnings if any
    if warnings:
        print("⚠️  Warnings:")
        for warning in warnings:
            print(f"   • {warning}")
        print()

    # Print next steps
    print("Next steps:")
    print(f"  1. cd {project_slug}")
    if not check_command_exists("uv"):
        print("  2. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("  3. uv sync                    # Install dependencies")
        print("  4. uv run pytest              # Run tests")
    else:
        print("  2. uv run pytest              # Run tests")
        print("  3. uv run ruff check .        # Check code quality")
    print("  4. uv run fastmcp dev app/server.py  # Start development server")
    if create_github_repo == "yes" and initial_commit_success:
        print(
            f"\n✓ GitHub repository created: https://github.com/{github_username}/{project_slug}"
        )
    print("\nDocumentation:")
    print("  • README.md           - Getting started guide")
    print("  • TOOLS.md            - Tool implementation guide")
    print("  • CONTRIBUTING.md     - Development guidelines")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error during setup: {e}", file=sys.stderr)
        print("The project was created but post-generation setup failed.")
        print("You may need to run setup commands manually.")
        sys.exit(1)
