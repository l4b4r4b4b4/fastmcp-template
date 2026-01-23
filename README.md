# FastMCP Cookiecutter Template

[![Template CI](https://github.com/l4b4r4b4b4/fastmcp-template/actions/workflows/test-template.yml/badge.svg)](https://github.com/l4b4r4b4b4/fastmcp-template/actions/workflows/test-template.yml)
[![Template Verified](https://img.shields.io/badge/Template-5%2F5%20Configs%20Verified-success?style=flat-square&logo=checkmarx&logoColor=white)](VERIFICATION.md)
[![Last Verified](https://img.shields.io/badge/Last%20Verified-Jan%202025-blue?style=flat-square&logo=calendar&logoColor=white)](VERIFICATION.md)
[![Tests Passing](https://img.shields.io/badge/Tests-397%2F397%20Passing-brightgreen?style=flat-square&logo=pytest&logoColor=white)](VERIFICATION.md)

🚀 Production-ready [FastMCP](https://github.com/jlowin/fastmcp) server template with [mcp-refcache](https://github.com/l4b4r4b4b4/mcp-refcache) integration for building AI agent tools that handle large data efficiently.

## Quick Start

### Using Cookiecutter

```bash
# Install cookiecutter (one-time)
uv tool install cookiecutter
# or: pipx install cookiecutter

# Generate your project (interactive)
cookiecutter gh:l4b4r4b4b4/fastmcp-template

# Or use a variant directly with auto-detected GitHub info
cookiecutter gh:l4b4r4b4b4/fastmcp-template --no-input \
  project_name="My Server" \
  template_variant=standard \
  github_username="$(gh api user --jq .login)" \
  author_name="$(gh api user --jq .name)" \
  author_email="$(gh api user --jq .email)"

# Navigate to your new project
cd your-mcp-server

# Start developing!
uv run pytest
uv run your-mcp-server stdio
```

**💡 Tip:** If you have `gh` CLI authenticated, the template will auto-detect your GitHub username when creating repositories. For other fields, use the command above to pass your GitHub profile info automatically.

### What You Get

A fully-configured FastMCP server with:

- ✅ **Reference-Based Caching** - Handle large data without context window limits
- ✅ **Preview Generation** - Automatic previews for large results
- ✅ **Pagination** - Navigate datasets efficiently
- ✅ **Access Control** - Separate user/agent permissions
- ✅ **Private Computation** - Agents compute with values they cannot see
- ✅ **Docker Ready** - Production containers with multi-stage builds
- ✅ **GitHub Actions** - CI/CD with PyPI publishing and GHCR containers
- ✅ **Optional Langfuse** - Built-in observability integration
- ✅ **Type-Safe** - Full type hints with Pydantic models
- ✅ **Testing Ready** - pytest with 73% coverage requirement
- ✅ **Pre-commit Hooks** - Ruff formatting and linting

## Template Variants

Choose a variant based on your needs:

| Variant | Demo Tools | Secret Tools | Langfuse | Custom Rules | Tests | Best For |
|---------|------------|--------------|----------|--------------|-------|----------|
| `minimal` | ❌ | ❌ | ❌ | ❌ | 60 | Production servers, clean slate |
| `standard` | ❌ | ❌ | ✅ | ❌ | 75 | Recommended with observability |
| `full` | ✅ | ✅ | ✅ | ❌ | 101 | Learning, reference implementation |
| `custom` | (choose) | (choose) | (choose) | (choose) | varies | Advanced users, specific needs |

### Minimal (Production)

Clean slate with no demo code - perfect for production servers:

```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template --no-input \
  project_name="My Server" \
  template_variant=minimal
```

Generates:
- ✅ Health check tool
- ✅ Cache query tool
- ✅ Admin tools (permission-gated)
- ❌ No demo/example code
- ❌ No Langfuse dependency

### Standard (Recommended)

Production-ready with Langfuse observability:

```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template --no-input \
  project_name="My Server" \
  template_variant=standard
```

Includes everything in minimal plus:
- ✅ Langfuse tracing integration
- ✅ Context management tools
- ✅ Trace info tools

### Full (Learning)

All features and examples for learning:

```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template --no-input \
  project_name="My Server" \
  template_variant=full
```

Includes everything plus:
- ✅ `hello` - Basic tool pattern
- ✅ `generate_items` - Cached large data with RefCache
- ✅ `store_secret` / `compute_with_secret` - Private computation pattern

### Custom (Advanced)

Choose exactly which features you want:

```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template

# When prompted:
template_variant: custom
include_demo_tools [no]: yes
include_secret_tools [no]: no
include_langfuse [yes]: yes
include_custom_rules [no]: no
```

Or non-interactively:
```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template --no-input \
  project_name="My Server" \
  template_variant=custom \
  include_demo_tools=yes \
  include_secret_tools=no \
  include_langfuse=yes \
  include_custom_rules=no
```

This gives you full control over all 8 possible combinations of features.

### Auto-Detecting Your GitHub Info

If you have `gh` CLI installed and authenticated, you can automatically use your GitHub profile information:

```bash
# Auto-detect GitHub username, name, and email
cookiecutter gh:l4b4r4b4b4/fastmcp-template \
  github_username="$(gh api user --jq .login)" \
  author_name="$(gh api user --jq .name)" \
  author_email="$(gh api user --jq .email)"
```

Or create a shell alias for convenience:
```bash
# Add to ~/.bashrc or ~/.zshrc
alias mcp-new='cookiecutter gh:l4b4r4b4b4/fastmcp-template \
  github_username="$(gh api user --jq .login)" \
  author_name="$(gh api user --jq .name)" \
  author_email="$(gh api user --jq .email)"'

# Then just run:
mcp-new
```

### GitHub Repository Creation

The template can automatically create a GitHub repository and push your initial commit:

```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template

# When prompted:
create_github_repo [no]: yes
github_repo_visibility [public]: public  # or private
```

**Requirements:**
- [GitHub CLI](https://cli.github.com) installed (`brew install gh` or see https://cli.github.com)
- Authenticated with `gh auth login`

**What it does:**
1. Auto-detects your authenticated GitHub username
2. Creates a new GitHub repository under your account
3. Sets it as the remote origin
4. Pushes the initial commit

**If setup fails:**
The template will show warnings but won't abort. You can create the repo manually:
```bash
gh auth login  # If not authenticated
gh repo create your-project --public --source=. --push
```

**Note:** Repository creation is **enabled by default** (`create_github_repo=yes`). Set to `no` if you want to skip it.

### Initial Release & PyPI Publishing

The template can automatically trigger a v0.0.0 release that publishes to PyPI:

**Step 1: Set up PyPI Pending Trusted Publisher (before generating)**

1. Go to https://pypi.org/manage/account/publishing/
2. Add a "pending publisher" with:
   - **PyPI Project Name:** `your-project-slug` (e.g., `legal-mcp`)
   - **Owner:** Your GitHub username (e.g., `l4b4r4b4b4`)
   - **Repository:** Same as project slug (e.g., `legal-mcp`)
   - **Workflow name:** `publish.yml`
   - **Environment:** `pypi` (or leave blank)

**Step 2: Generate with initial release enabled**

```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template --no-input \
  project_name="Legal MCP" \
  template_variant=minimal \
  github_username="$(gh api user --jq .login)" \
  author_name="$(gh api user --jq .name)" \
  author_email="$(gh api user --jq .email)" \
  trigger_initial_release=yes
```

**What happens:**
1. Project is generated
2. GitHub repository is created (public)
3. Branch protection ruleset is configured
4. `v0.0.0` tag is created and pushed
5. Release workflow triggers → publishes to PyPI automatically

**Requirements:**
- Public repository (PyPI trusted publishers require public repos)
- Pending trusted publisher configured on PyPI
- `gh` CLI authenticated

### Branch Protection

The template automatically sets up a branch protection ruleset for `main` with:

- ✅ **Pull request required** - No direct pushes to main
- ✅ **Required status checks** - Must pass before merge:
  - Lint & Format
  - Test (Python 3.12)
  - Test (Python 3.13)
  - Security Scan
  - CI Success
- ✅ **No force pushes** - Protects commit history

This provides a solid foundation for DevOps workflows. You can extend it later with:
- Additional branches (develop, staging, production)
- Required reviewers
- Code owner reviews
- Deployment environments

View/edit rulesets: `https://github.com/<username>/<repo>/settings/rules`

**If you skip the initial release**, you can trigger it manually later:
```bash
git tag -a v0.0.0 -m "Initial release - validates release pipeline"
git push origin v0.0.0
```

## Features

### Reference-Based Caching (RefCache)

Instead of returning large data directly, return a reference:

```python
@mcp.tool
@cache.cached(namespace="public")
async def fetch_large_dataset(query: str) -> list[dict]:
    """Fetch dataset - returns reference for large results."""
    data = await get_data(query)  # e.g., 10,000 rows
    return data  # RefCache automatically creates reference
```

Agent receives a reference instead of 10,000 rows in context window.

### Private Computation

Store sensitive values agents can compute with but not read:

```python
@mcp.tool
def store_secret(name: str, value: float) -> dict:
    """Store value with EXECUTE-only permission."""
    policy = AccessPolicy(
        user_permissions=Permission.FULL,
        agent_permissions=Permission.EXECUTE,  # Can use, cannot read
    )
    ref = cache.set(f"secret_{name}", value, policy=policy)
    return {"ref_id": ref.ref_id}

@mcp.tool
def compute_with_secret(secret_ref: str, multiplier: float) -> dict:
    """Compute using secret without revealing it."""
    secret = cache.resolve(secret_ref, actor=DefaultActor.system())
    return {"result": secret * multiplier}
```

## Project Structure

```
your-mcp-server/
├── app/                     # Application code
│   ├── server.py            # Main MCP server
│   ├── tools/               # Tool modules
│   └── __main__.py          # CLI entry point
├── tests/                   # Test suite
│   ├── conftest.py
│   └── test_server.py
├── docker/                  # Docker configurations
│   ├── Dockerfile.base      # Python base with dependencies
│   ├── Dockerfile           # Production image
│   └── Dockerfile.dev       # Development with hot reload
├── .github/workflows/       # CI/CD pipelines
│   ├── ci.yml               # Lint, test, security
│   ├── publish.yml          # PyPI publishing
│   └── release.yml          # Docker builds
├── .agent/                  # AI assistant workspace
│   ├── scratchpad.md        # Main session notes
│   └── goals/               # Goal tracking
│       ├── scratchpad.md    # Goals index
│       ├── 00-Template-Goal/  # Goal template
│       └── 01-Initial-Setup-And-Release/  # First goal (validate 0.0.0 release)
├── pyproject.toml           # Project configuration
├── docker-compose.yml       # Local development
└── README.md                # Project documentation
```

## Next Steps After Generation

1. **Follow Goal 01** - Every generated project includes a first goal:
   ```bash
   cd your-mcp-server
   cat .agent/goals/01-Initial-Setup-And-Release/scratchpad.md
   ```
   This guides you through:
   - Setting up the development environment
   - Running tests and quality checks
   - Publishing version 0.0.0 to validate the release pipeline

2. **Verify GitHub repository** (if you enabled repo creation)
   ```bash
   git remote -v              # Check remote is set
   # Visit https://github.com/your-username/your-project
   ```

3. **Run the validation checklist**
   ```bash
   uv sync                    # Install dependencies
   uv run pytest            # Run tests
   ruff check . --fix && ruff format .  # Code quality
   ```

4. **Try the server**
   ```bash
   uv run your-mcp-server stdio
   ```

5. **Customize the .rules file** (if you enabled custom rules)
   - Edit the "Project-Specific Rules" section
   - Add your team's conventions, constraints, or guidelines

6. **Add your tools**
   - Create tool modules in `app/tools/`
   - Register in `app/server.py`
   - Add tests in `tests/`

7. **Configure GitHub publishing** (optional)
   - PyPI: Add trusted publisher at pypi.org
   - GHCR: GitHub Actions will publish on release

## Testing the Template

### Automated CI Testing

The template is automatically tested on every push and pull request. CI validates 5 configurations:
- ✅ Minimal - 60 tests
- ✅ Standard - 75 tests
- ✅ Full - 101 tests
- ✅ Custom (demos only) - 85 tests
- ✅ Custom (secrets only) - 76 tests

Each configuration is tested for:
- Successful project generation
- All tests passing
- Linting passes (ruff check)
- No hardcoded template values
- Correct test count

### Local Testing

Test a specific variant before submitting changes:

```bash
# Test preset variants
./scripts/validate-template.sh minimal
./scripts/validate-template.sh standard
./scripts/validate-template.sh full

# Test custom combinations
./scripts/validate-template.sh custom-demos-only
./scripts/validate-template.sh custom-secrets-only

# Test all variants
./scripts/validate-template.sh --all
```

### Manual Verification

Generate and test a project manually:

```bash
# Generate project
uv run cookiecutter . --output-dir /tmp/test-project --no-input \
  project_name="Test Project" \
  template_variant=full

# Test generated project
cd /tmp/test-project/test-project
uv run pytest -v
uv run ruff check .
```

### Verification Report

See [VERIFICATION.md](VERIFICATION.md) for comprehensive manual testing results:
- Detailed test breakdowns for all variants
- Manual verification of demo tools functionality
- Architecture notes and troubleshooting guides
- 397 total tests verified across 5 configurations (60 + 75 + 101 + 85 + 76)

## Features in Detail
## Development

To work on the template itself (not generate projects):

```bash
git clone https://github.com/l4b4r4b4b4/fastmcp-template
cd fastmcp-template

# The actual template is in {{cookiecutter.project_slug}}/
ls "{{cookiecutter.project_slug}}/"

# Test template generation locally
cookiecutter . --no-input
# or
cookiecutter .  # With prompts
```

## Documentation

- **Template README**: See [`{{cookiecutter.project_slug}}/README.md`]({{cookiecutter.project_slug}}/README.md) for generated project documentation
- **FastMCP**: https://github.com/jlowin/fastmcp
- **mcp-refcache**: https://github.com/l4b4r4b4b4/mcp-refcache
- **MCP Protocol**: https://modelcontextprotocol.io/

## Contributing

See [CONTRIBUTING.md]({{cookiecutter.project_slug}}/CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE]({{cookiecutter.project_slug}}/LICENSE) for details.

## Related Projects

- [mcp-refcache](https://github.com/l4b4r4b4b4/mcp-refcache) - Reference-based caching for MCP servers
- [FastMCP](https://github.com/jlowin/fastmcp) - High-performance MCP framework
- [Model Context Protocol](https://modelcontextprotocol.io/) - Protocol specification

---

**Generated with ❤️ using [Cookiecutter](https://github.com/cookiecutter/cookiecutter)**
