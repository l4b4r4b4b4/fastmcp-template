# Temporary Directory

This directory is used for temporary files during development and testing.

## Purpose

- **Local testing**: Generate test projects here without polluting the main workspace
- **Variant testing**: The `scripts/generate_all_variants.sh` script outputs to `scripts/variants/`
- **Debugging**: Store temporary outputs when investigating issues

## Guidelines

- **Do not commit** files in this directory (it's gitignored)
- **Clean periodically** to avoid stale files
- Use for ephemeral work only

## Usage

```bash
# Generate a test project here
uv run cookiecutter .. --output-dir . --no-input project_name="Test" template_variant=minimal

# Clean up
rm -rf */
```
