#!/bin/bash
# run_drift.sh - Wrapper script for drift analysis
# Usage: ./run_drift.sh <namespace> <checkpoint-a> <checkpoint-b> [options]

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Help text
show_help() {
    cat << EOF
Drift Analysis Runner

Usage:
    $0 <namespace> <checkpoint-a> <checkpoint-b> [options]

Arguments:
    namespace       Target HoloMem namespace
    checkpoint-a    Baseline checkpoint ID
    checkpoint-b    Current checkpoint ID

Options:
    --verbose                Print progress messages
    --quiet                  Suppress console output (logs still written)
    --no-truncate-responses  Disable response truncation
    --tool-timeout <sec>     MCP tool timeout in seconds (default: 45)
    --heartbeat-interval <sec> Heartbeat log interval (default: 5)
    --output-dir <dir>       Output directory (default: prompt_runs)
    --help                   Show this help message

Examples:
    # Basic usage
    $0 ns-dra-fastapi-10 checkpoint-a checkpoint-b

    # With verbose output
    $0 ns-dra-fastapi-10 checkpoint-a checkpoint-b --verbose

    # With custom timeout
    $0 ns-dra-fastapi-10 checkpoint-a checkpoint-b --tool-timeout 120

Environment:
    Requires .env file with OPENAI_API_KEY, OPENAI_MODEL, and MCP_ENDPOINT.
    Run 'source .env' before executing this script.

EOF
}

# Check for help flag
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
    exit 0
fi

# Check minimum arguments
if [ $# -lt 3 ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo ""
    show_help
    exit 1
fi

# Parse positional arguments
NAMESPACE="$1"
CHECKPOINT_A="$2"
CHECKPOINT_B="$3"
shift 3

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please create .env from .env.example and configure your API keys"
    echo ""
    echo "  cp .env.example .env"
    echo "  # Edit .env with your configuration"
    echo "  source .env"
    exit 1
fi

# Load environment variables
echo -e "${YELLOW}Loading environment from .env...${NC}"
source .env

# Validate required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}Error: OPENAI_API_KEY not set${NC}"
    echo "Please set OPENAI_API_KEY in .env file"
    exit 1
fi

if [ -z "$MCP_ENDPOINT" ]; then
    echo -e "${RED}Error: MCP_ENDPOINT not set${NC}"
    echo "Please set MCP_ENDPOINT in .env file"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Warning: Virtual environment not activated${NC}"
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    else
        echo -e "${RED}Error: Virtual environment not found${NC}"
        echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
fi

# Display configuration
echo -e "${GREEN}Configuration:${NC}"
echo "  Namespace:     $NAMESPACE"
echo "  Checkpoint A:  $CHECKPOINT_A"
echo "  Checkpoint B:  $CHECKPOINT_B"
echo "  Model:         ${OPENAI_MODEL:-gpt-4o-mini}"
echo "  MCP Endpoint:  $MCP_ENDPOINT"
echo ""

# Run drift analysis
echo -e "${GREEN}Running drift analysis...${NC}"
python -m prompt_runner.cli \
    --namespace "$NAMESPACE" \
    --prompt-id drift_analysis \
    --checkpoint-a "$CHECKPOINT_A" \
    --checkpoint-b "$CHECKPOINT_B" \
    "$@"

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Drift analysis complete!${NC}"

    # Find the latest summary file
    LATEST_SUMMARY=$(find prompt_runs/drift -name "summary.drift_analysis.*.md" -type f -print0 | xargs -0 ls -t | head -1)

    if [ -n "$LATEST_SUMMARY" ]; then
        echo -e "${GREEN}Summary: $LATEST_SUMMARY${NC}"
        echo ""
        echo "View summary:"
        echo "  cat \"$LATEST_SUMMARY\""
        echo ""
        echo "Or open in editor:"
        echo "  vim \"$LATEST_SUMMARY\""
        echo "  code \"$LATEST_SUMMARY\""
    fi
else
    echo ""
    echo -e "${RED}✗ Drift analysis failed${NC}"
    echo "Check logs in prompt_runs/drift/ for details"
    exit 1
fi
