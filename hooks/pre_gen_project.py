#!/usr/bin/env python3
"""Pre-generation hook for FastMCP template.

Displays variant configuration information to the user before generating the project.
"""

import sys

# Template variables (filled by cookiecutter)
VARIANT = "{{ cookiecutter.template_variant }}"
PROJECT_NAME = "{{ cookiecutter.project_name }}"

# For custom variant, use user selections
DEMO_TOOLS = "{{ cookiecutter.include_demo_tools }}"
SECRET_TOOLS = "{{ cookiecutter.include_secret_tools }}"
LANGFUSE = "{{ cookiecutter.include_langfuse }}"

# Variant configurations (for preset variants)
VARIANT_CONFIG = {
    "minimal": {
        "demo_tools": "no",
        "secret_tools": "no",
        "langfuse": "no",
    },
    "standard": {
        "demo_tools": "no",
        "secret_tools": "no",
        "langfuse": "yes",
    },
    "full": {
        "demo_tools": "yes",
        "secret_tools": "yes",
        "langfuse": "yes",
    },
}


def main() -> None:
    """Display variant configuration before generation."""
    # Get config based on variant
    if VARIANT == "custom":
        config = {
            "demo_tools": DEMO_TOOLS,
            "secret_tools": SECRET_TOOLS,
            "langfuse": LANGFUSE,
        }
    else:
        config = VARIANT_CONFIG.get(VARIANT, VARIANT_CONFIG["minimal"])

    print()
    print("=" * 60)
    print(f"  Creating '{PROJECT_NAME}' with {VARIANT.upper()} variant")
    print("=" * 60)
    print()
    print("  Configuration:")
    print(f"    • Demo tools:    {config['demo_tools']}")
    print(f"    • Secret tools:  {config['secret_tools']}")
    print(f"    • Langfuse:      {config['langfuse']}")
    print()

    # Variant-specific messages
    if VARIANT == "minimal":
        print("  ℹ️  Minimal: Clean slate for production servers")
        print("     No demo code - add your own tools in app/tools/")
    elif VARIANT == "standard":
        print("  ℹ️  Standard: Recommended setup with observability")
        print("     Langfuse tracing enabled for monitoring")
    elif VARIANT == "full":
        print("  ℹ️  Full: All examples included for learning")
        print("     Demo tools show RefCache patterns")
    elif VARIANT == "custom":
        print("  ℹ️  Custom: You chose your own configuration")
        print("     Review the settings above")

    print()
    print("-" * 60)
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Warning: Pre-generation hook error: {e}", file=sys.stderr)
        # Don't fail generation on hook errors
        pass
