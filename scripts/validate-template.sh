#!/usr/bin/env bash
#
# Validate FastMCP Template Generation
#
# Tests cookiecutter template generation and verifies generated projects work correctly.
# Used for local development and CI validation.
#
# Usage:
#   ./scripts/validate-template.sh minimal       # Test minimal variant
#   ./scripts/validate-template.sh standard      # Test standard variant
#   ./scripts/validate-template.sh full          # Test full variant
#   ./scripts/validate-template.sh --all         # Test all variants
#   ./scripts/validate-template.sh --help        # Show help

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variant configuration: variant_name -> expected_tests
declare -A VARIANTS=(
    ["minimal"]="60"
    ["standard"]="75"
    ["full"]="101"
    ["custom-demos-only"]="85"
    ["custom-secrets-only"]="76"
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
  ./scripts/validate-template.sh <variant>
  ./scripts/validate-template.sh --all
  ./scripts/validate-template.sh --help

Variants:
  minimal               - No demo tools, no secrets, no Langfuse (60 tests)
  standard              - No demo tools, no secrets, with Langfuse (75 tests)
  full                  - All demo and secret tools, with Langfuse (101 tests)
  custom-demos-only     - Demo tools only, with Langfuse (85 tests)
  custom-secrets-only   - Secret tools only, no Langfuse (76 tests)
  --all                 - Test all variants

Examples:
  ./scripts/validate-template.sh minimal
  ./scripts/validate-template.sh --all

HELP
}

# Validate single variant
validate_variant() {
    local variant_name=$1
    local expected_tests=${VARIANTS[$variant_name]}

    if [[ -z "$expected_tests" ]]; then
        print_msg "$RED" "❌ Unknown variant: $variant_name"
        return 1
    fi

    print_msg "$BLUE" "\n=========================================="
    print_msg "$BLUE" "Testing: $variant_name variant"
    print_msg "$BLUE" "  Expected tests: $expected_tests"
    print_msg "$BLUE" "==========================================\n"

    local output_dir="/tmp/fastmcp-template-test"
    local project_dir="$output_dir/test-$variant_name"

    # Clean up previous test
    rm -rf "$project_dir"

    # Generate project
    print_msg "$YELLOW" "→ Generating project with $variant_name variant..."

    # Handle custom variants with specific options
    case "$variant_name" in
    custom-demos-only)
        if ! uv run cookiecutter . --output-dir "$output_dir" --no-input \
            project_name="Test $variant_name" \
            project_slug="test-$variant_name" \
            template_variant="custom" \
            include_demo_tools="yes" \
            include_secret_tools="no" \
            include_langfuse="yes" >/dev/null 2>&1; then
            print_msg "$RED" "❌ Failed to generate project"
            return 1
        fi
        ;;
    custom-secrets-only)
        if ! uv run cookiecutter . --output-dir "$output_dir" --no-input \
            project_name="Test $variant_name" \
            project_slug="test-$variant_name" \
            template_variant="custom" \
            include_demo_tools="no" \
            include_secret_tools="yes" \
            include_langfuse="no" >/dev/null 2>&1; then
            print_msg "$RED" "❌ Failed to generate project"
            return 1
        fi
        ;;
    *)
        if ! uv run cookiecutter . --output-dir "$output_dir" --no-input \
            project_name="Test $variant_name" \
            project_slug="test-$variant_name" \
            template_variant="$variant_name" >/dev/null 2>&1; then
            print_msg "$RED" "❌ Failed to generate project"
            return 1
        fi
        ;;
    esac
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

    print_msg "$GREEN" "\n✅ Variant '$variant_name' validated successfully!\n"
    return 0
}

# Main execution
main() {
    if [[ $# -eq 0 || "$1" == "--help" || "$1" == "-h" ]]; then
        show_help
        exit 0
    fi

    if [[ "$1" == "--all" ]]; then
        print_msg "$BLUE" "Testing all variants..."
        local failed=0
        for variant in minimal standard full custom-demos-only custom-secrets-only; do
            if ! validate_variant "$variant"; then
                failed=$((failed + 1))
            fi
        done

        if [[ $failed -eq 0 ]]; then
            print_msg "$GREEN" "\n🎉 All variants validated successfully!"
            exit 0
        else
            print_msg "$RED" "\n❌ $failed variant(s) failed"
            exit 1
        fi
    else
        validate_variant "$1"
    fi
}

main "$@"
