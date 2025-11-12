#!/bin/bash
# run_supply_chain.sh - Wrapper script for supply chain analysis
# Usage: ./run_supply_chain.sh <namespace> <project-name> <code-namespace> <vuln-namespace> <manifest-concept> [options]

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Help text
show_help() {
    cat << EOF
Supply Chain Analysis Runner

Usage:
    $0 <namespace> <project-name> <code-namespace> <vuln-namespace> <manifest-concept> [options]

Arguments:
    namespace           Target HoloMem namespace
    project-name        Name of the project to analyze
    code-namespace      Namespace containing source code concepts
    vuln-namespace      Namespace containing vulnerability data
    manifest-concept    Manifest concept name (e.g., manifest.current)

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
    $0 ns-supply-chain my-web-app ns-code-main ns-vuln-db manifest.current

    # With verbose output
    $0 ns-supply-chain my-web-app ns-code-main ns-vuln-db manifest.current --verbose

    # With custom timeout
    $0 ns-supply-chain my-web-app ns-code-main ns-vuln-db manifest.current --tool-timeout 120

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
if [ $# -lt 5 ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo ""
    show_help
    exit 1
fi

# Parse positional arguments
NAMESPACE="$1"
PROJECT_NAME="$2"
CODE_NAMESPACE="$3"
VULN_NAMESPACE="$4"
MANIFEST_CONCEPT="$5"
shift 5

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
echo "  Namespace:         $NAMESPACE"
echo "  Project Name:      $PROJECT_NAME"
echo "  Code Namespace:    $CODE_NAMESPACE"
echo "  Vuln Namespace:    $VULN_NAMESPACE"
echo "  Manifest Concept:  $MANIFEST_CONCEPT"
echo "  Model:             ${OPENAI_MODEL:-gpt-4o-mini}"
echo "  MCP Endpoint:      $MCP_ENDPOINT"
echo ""

# Run supply chain analysis
echo -e "${GREEN}Running supply chain analysis...${NC}"
python -m prompt_runner.cli \
    --namespace "$NAMESPACE" \
    --prompt-id supply_chain \
    --project-name "$PROJECT_NAME" \
    --code-namespace "$CODE_NAMESPACE" \
    --vuln-namespace "$VULN_NAMESPACE" \
    --manifest-concept "$MANIFEST_CONCEPT" \
    "$@"

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Supply chain analysis complete!${NC}"

    # Find the latest summary file
    LATEST_SUMMARY=$(find prompt_runs/supply_chain -name "summary.supply_chain.*.md" -type f -print0 | xargs -0 ls -t | head -1)

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
    echo -e "${RED}✗ Supply chain analysis failed${NC}"
    echo "Check logs in prompt_runs/supply_chain/ for details"
    exit 1
fi
