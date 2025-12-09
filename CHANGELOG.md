# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.1] - 2024-12-09

### Added

- Initial release of FastMCP Template
- Core server implementation with mcp-refcache integration
- Example tools demonstrating caching patterns:
  - `hello` - Simple greeting tool (no caching)
  - `generate_items` - Generate items with public namespace caching
  - `store_secret` - Store secrets with EXECUTE-only agent permissions
  - `compute_with_secret` - Private computation without revealing values
  - `get_cached_result` - Paginate through cached results
  - `health_check` - Server health status
- Admin tools registration (permission-gated)
- Template guide prompt for usage instructions
- CLI with stdio and SSE transport options
- Project configuration:
  - UV-based dependency management
  - Nix flake for reproducible development environment
  - Ruff linting and formatting
  - Pytest with asyncio support
  - Pre-commit hooks (ruff, mypy, bandit, safety)
- GitHub Actions workflows:
  - CI pipeline with Python 3.12/3.13 matrix
  - Release workflow for version tags
- IDE configuration:
  - Zed settings with Pyright LSP and MCP context servers
  - GitHub Copilot instructions
- Documentation:
  - Contributing guidelines
  - Project rules for AI coding assistants

[Unreleased]: https://github.com/l4b4r4b4b4/fastmcp-template/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/l4b4r4b4b4/fastmcp-template/releases/tag/v0.0.1
