#!/usr/bin/env bash
#
# Validate FastMCP Template Generation
#
# Tests cookiecutter template generation and verifies generated projects work correctly.
# Used for local development and CI validation.
#
# Usage:
#   ./scripts/validate-template.sh minimal       # Test minimal configuration
#   ./scripts/validate-template.sh full          # Test full configuration
#   ./scripts/validate-template.sh --all         # Test all configurations
#   ./scripts/validate-template.sh --help        # Show help

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration map
declare -A CONFIGS=(
    ["minimal"]="no:no:75"
    ["full"]="yes:yes:101"
    ["demos-only"]="yes:no:86"
    ["secrets-only"]="no:yes:85"
)

# Print colored message
print_msg() {
    local color=$1
    local msg=$2
    echo -e "${color}${msg}${NC}"
}

# Show usage
show_help() {
    cat <<HELP
FastMCP Template Validation Script

Usage:
  ./scripts/validate-template.sh <config>
  ./scripts/validate-template.sh --all
  ./scripts/validate-template.sh --help

Configurations:
  minimal       - No demo tools, no secret tools (74 tests)
  full          - All demo and secret tools (101 tests)
  demos-only    - Demo tools only (86 tests)
  secrets-only  - Secret tools only (85 tests)
  --all         - Test all configurations

Examples:
  ./scripts/validate-template.sh minimal
  ./scripts/validate-template.sh --all

HELP
}

# Validate single configuration
validate_config() {
    local config_name=$1
    local config_value=${CONFIGS[$config_name]}

    if [[ -z "$config_value" ]]; then
        print_msg "$RED" "❌ Unknown configuration: $config_name"
        return 1
    fi

    IFS=':' read -r demo_tools secret_tools expected_tests <<<"$config_value"

    print_msg "$BLUE" "\n=========================================="
    print_msg "$BLUE" "Testing: $config_name"
    print_msg "$BLUE" "  Demo tools: $demo_tools"
    print_msg "$BLUE" "  Secret tools: $secret_tools"
    print_msg "$BLUE" "  Expected tests: $expected_tests"
    print_msg "$BLUE" "==========================================\n"

    local output_dir="/tmp/fastmcp-template-test"
    local project_dir="$output_dir/test-$config_name"

    # Clean up previous test
    rm -rf "$project_dir"

    # Generate project
    print_msg "$YELLOW" "→ Generating project..."
    if ! uv run cookiecutter . --output-dir "$output_dir" --no-input \
        project_name="Test $config_name" \
        project_slug="test-$config_name" \
        include_demo_tools="$demo_tools" \
        include_secret_tools="$secret_tools" >/dev/null 2>&1; then
        print_msg "$RED" "❌ Failed to generate project"
        return 1
    fi
    print_msg "$GREEN" "✓ Project generated"

    # Run tests
    print_msg "$YELLOW" "→ Running tests..."
    if ! (cd "$project_dir" && uv run pytest -q >/dev/null 2>&1); then
        print_msg "$RED" "❌ Tests failed"
        (cd "$project_dir" && uv run pytest --tb=short)
        return 1
    fi
    print_msg "$GREEN" "✓ Tests passed"

    # Verify test count
    print_msg "$YELLOW" "→ Verifying test count..."
    local test_count=$(cd "$project_dir" && uv run pytest --collect-only -q 2>/dev/null | grep -c "test_" || echo "0")
    if [[ "$test_count" -ne "$expected_tests" ]]; then
        print_msg "$RED" "❌ Test count mismatch: expected $expected_tests, found $test_count"
        return 1
    fi
    print_msg "$GREEN" "✓ Test count correct: $test_count"

    # Run linting (with auto-fix for Jinja2-generated whitespace issues)
    print_msg "$YELLOW" "→ Running linting checks..."
    (cd "$project_dir" && uv run ruff check . --fix >/dev/null 2>&1) || true
    if ! (cd "$project_dir" && uv run ruff check . >/dev/null 2>&1); then
        print_msg "$RED" "❌ Linting failed"
        (cd "$project_dir" && uv run ruff check .)
        return 1
    fi
    print_msg "$GREEN" "✓ Linting passed"

    # Check for hardcoded values
    print_msg "$YELLOW" "→ Checking for hardcoded template values..."
    if grep -r "fastmcp-template" "$project_dir" --exclude-dir=.git --exclude-dir=.venv --exclude-dir=.ruff_cache --exclude="*.pyc" >/dev/null 2>&1; then
        print_msg "$RED" "❌ Found hardcoded 'fastmcp-template' references"
        grep -r "fastmcp-template" "$project_dir" --exclude-dir=.git --exclude-dir=.venv --exclude-dir=.ruff_cache --exclude="*.pyc"
        return 1
    fi
    print_msg "$GREEN" "✓ No hardcoded template values"

    print_msg "$GREEN" "\n✅ Configuration '$config_name' validated successfully!\n"
    return 0
}

# Main execution
main() {
    if [[ $# -eq 0 || "$1" == "--help" || "$1" == "-h" ]]; then
        show_help
        exit 0
    fi

    if [[ "$1" == "--all" ]]; then
        print_msg "$BLUE" "Testing all configurations..."
        local failed=0
        for config in minimal full demos-only secrets-only; do
            if ! validate_config "$config"; then
                failed=$((failed + 1))
            fi
        done

        if [[ $failed -eq 0 ]]; then
            print_msg "$GREEN" "\n🎉 All configurations validated successfully!"
            exit 0
        else
            print_msg "$RED" "\n❌ $failed configuration(s) failed"
            exit 1
        fi
    else
        validate_config "$1"
    fi
}

main "$@"
