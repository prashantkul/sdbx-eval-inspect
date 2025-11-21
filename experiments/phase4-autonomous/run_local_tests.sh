#!/bin/bash
#
# Local Testing Script for Phase 4 Autonomous Agent
# Run this tonight to verify everything works before tomorrow's sandboxed test
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "======================================================================="
echo "Phase 4 Autonomous Agent - Local Testing Suite"
echo "======================================================================="
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Source environment
echo "Loading environment..."
set -a
source ../../.env
set +a

# Verify OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}ERROR: OPENAI_API_KEY not set in environment${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} OpenAI API key found"
echo ""

# Clean up old test results
echo "Cleaning up old test workspaces..."
rm -rf /tmp/phase4-*-test /tmp/test-*-openai* 2>/dev/null || true
echo -e "${GREEN}✓${NC} Cleanup complete"
echo ""

# Test 1: Basic OpenAI verification
echo "======================================================================="
echo "TEST 1: Basic OpenAI Connection"
echo "======================================================================="
echo ""

bash -c "set -a; source ../../.env; set +a; conda run -n sdbx-eval-fwk python tests/test_openai_simple.py"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Test 1 PASSED${NC}"
else
    echo -e "${RED}✗ Test 1 FAILED${NC}"
    exit 1
fi
echo ""

# Test 2: Custom tools verification
echo "======================================================================="
echo "TEST 2: Custom Tools with OpenAI"
echo "======================================================================="
echo ""

bash -c "set -a; source ../../.env; set +a; conda run -n sdbx-eval-fwk python tests/test_openai_with_tools.py"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Test 2 PASSED${NC}"
else
    echo -e "${RED}✗ Test 2 FAILED${NC}"
    exit 1
fi
echo ""

# Test 3: Quick autonomous agent test (1 round)
echo "======================================================================="
echo "TEST 3: Quick Autonomous Agent (1 Round)"
echo "======================================================================="
echo ""

bash -c "set -a; source ../../.env; set +a; conda run -n sdbx-eval-fwk python tests/test_openai_quick.py"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Test 3 PASSED${NC}"

    # Show token usage
    if [ -f /tmp/phase4-quick-test/results.json ]; then
        echo ""
        echo "Token Usage:"
        cat /tmp/phase4-quick-test/results.json | python3 -m json.tool | grep -A 4 "token_usage"
    fi
else
    echo -e "${RED}✗ Test 3 FAILED${NC}"
    exit 1
fi
echo ""

# Ask user if they want to continue with longer test
echo "======================================================================="
echo "All quick tests passed! ✓"
echo "======================================================================="
echo ""
echo "Next step: Run multi-round test (3 rounds, ~5-10 minutes)"
echo ""
read -p "Continue with multi-round test? [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "======================================================================="
    echo "TEST 4: Multi-Round Autonomous Agent (3 Rounds)"
    echo "======================================================================="
    echo ""

    bash -c "set -a; source ../../.env; set +a; \
    MODEL_PROVIDER=openai \
    conda run -n sdbx-eval-fwk python tests/test_token_tracking.py"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Test 4 PASSED${NC}"

        # Show results
        if [ -f /tmp/phase4-token-test/token_test_results.json ]; then
            echo ""
            echo "Results:"
            cat /tmp/phase4-token-test/token_test_results.json | python3 -m json.tool
        fi
    else
        echo -e "${RED}✗ Test 4 FAILED${NC}"
        exit 1
    fi
fi

echo ""
echo "======================================================================="
echo "LOCAL TESTING COMPLETE"
echo "======================================================================="
echo ""
echo -e "${GREEN}✓ All tests passed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Review results in /tmp/phase4-*-test/"
echo "  2. Tomorrow morning: Run sandboxed test"
echo "  3. See TESTING_PLAN.md for full instructions"
echo ""
