#!/usr/bin/env bash
# Generate and test all cookiecutter template variants
# Usage: ./generate_all_variants.sh [--test]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="$TEMPLATE_DIR/.agent/tmp/variants"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

RUN_TESTS="${1:-}"

echo "Template directory: $TEMPLATE_DIR"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Clean up previous runs
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Track results
declare -a RESULTS

generate_variant() {
    local name="$1"
    local variant="$2"
    local demo="${3:-}"
    local secrets="${4:-}"
    local langfuse="${5:-}"

    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Generating: $name${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    local args=(
        --output-dir "$OUTPUT_DIR/$name"
        --no-input
        "project_name=Test $name"
        "template_variant=$variant"
        "create_github_repo=no"
    )

    if [[ "$variant" == "custom" ]]; then
        args+=("include_demo_tools=$demo")
        args+=("include_secret_tools=$secrets")
        args+=("include_langfuse=$langfuse")
    fi

    cd "$TEMPLATE_DIR"
    if uv run cookiecutter . "${args[@]}" 2>&1 | grep -v "^warning:"; then
        echo -e "${GREEN}✓ Generated successfully${NC}"
    else
        echo -e "${RED}✗ Generation failed${NC}"
        RESULTS+=("$name: GENERATION FAILED")
        return 1
    fi

    # Find the generated project directory
    local project_dir
    project_dir=$(find "$OUTPUT_DIR/$name" -mindepth 1 -maxdepth 1 -type d | head -1)

    if [[ -z "$project_dir" ]]; then
        echo -e "${RED}✗ Could not find generated project directory${NC}"
        RESULTS+=("$name: NO PROJECT DIR")
        return 1
    fi

    echo ""
    echo "Project directory: $project_dir"
    echo ""

    # Show __all__ from tools/__init__.py
    echo "=== app/tools/__init__.py __all__ ==="
    grep -A 50 "^__all__" "$project_dir/app/tools/__init__.py" | head -30
    echo ""

    if [[ "$RUN_TESTS" == "--test" ]]; then
        echo "=== Running linting and tests ==="
        cd "$project_dir"

        local lint_ok=true
        local format_ok=true
        local test_ok=true

        # Check formatting
        if uv run ruff format . --check 2>&1 | grep -v "^warning:"; then
            echo -e "${GREEN}✓ Format check passed${NC}"
        else
            echo -e "${RED}✗ Format check failed - running format${NC}"
            uv run ruff format . 2>&1 | grep -v "^warning:"
            format_ok=false
        fi

        # Check linting
        if uv run ruff check . 2>&1 | grep -v "^warning:"; then
            echo -e "${GREEN}✓ Lint check passed${NC}"
        else
            echo -e "${RED}✗ Lint check failed${NC}"
            lint_ok=false
        fi

        # Run tests with coverage
        if uv run pytest --cov --cov-fail-under=73 -q 2>&1 | grep -v "^warning:" | tail -10; then
            echo -e "${GREEN}✓ Tests passed with coverage ≥73%${NC}"
        else
            echo -e "${RED}✗ Tests or coverage failed${NC}"
            test_ok=false
        fi

        if $lint_ok && $format_ok && $test_ok; then
            RESULTS+=("$name: ${GREEN}ALL PASSED${NC}")
        else
            local status=""
            $format_ok || status+="FORMAT "
            $lint_ok || status+="LINT "
            $test_ok || status+="TEST "
            RESULTS+=("$name: ${RED}FAILED ($status)${NC}")
        fi
    else
        RESULTS+=("$name: generated (no tests)")
    fi

    echo ""
}

# Generate all variants
echo "============================================================"
echo "  Generating All Template Variants"
echo "============================================================"
echo ""

# Built-in variants
generate_variant "minimal" "minimal"
generate_variant "standard" "standard"
generate_variant "full" "full"

# Custom variants - all combinations of demo/secrets/langfuse
generate_variant "custom-none" "custom" "no" "no" "no"
generate_variant "custom-demo-only" "custom" "yes" "no" "no"
generate_variant "custom-secrets-only" "custom" "no" "yes" "no"
generate_variant "custom-langfuse-only" "custom" "no" "no" "yes"
generate_variant "custom-demo-secrets" "custom" "yes" "yes" "no"
generate_variant "custom-demo-langfuse" "custom" "yes" "no" "yes"
generate_variant "custom-secrets-langfuse" "custom" "no" "yes" "yes"
generate_variant "custom-all" "custom" "yes" "yes" "yes"

# Summary
echo ""
echo "============================================================"
echo "  Summary"
echo "============================================================"
echo ""
for result in "${RESULTS[@]}"; do
    echo -e "  $result"
done
echo ""
echo "Generated variants are in: $OUTPUT_DIR"
