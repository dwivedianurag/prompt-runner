#!/bin/bash
# setup.sh - One-time setup script for LLM Orchestrator
# Run this after unzipping the project to set up your environment

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  LLM Orchestrator Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Check Python version
echo -e "${YELLOW}[1/5] Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
REQUIRED_VERSION="3.10"

if [ -z "$PYTHON_VERSION" ]; then
    echo -e "${RED}Error: Python 3 not found${NC}"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

# Compare versions (simple string comparison works for major.minor)
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python $PYTHON_VERSION found, but $REQUIRED_VERSION or higher is required${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"
echo ""

# Step 2: Create virtual environment
echo -e "${YELLOW}[2/5] Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Skipping.${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi
echo ""

# Step 3: Activate virtual environment and install package
echo -e "${YELLOW}[3/5] Installing package and dependencies...${NC}"
source venv/bin/activate

if [ -f "pyproject.toml" ]; then
    pip install --upgrade pip > /dev/null
    pip install -e .
    echo -e "${GREEN}✓ Package installed in editable mode${NC}"
    echo -e "${GREEN}✓ 'prompt-runner' command is now available${NC}"
elif [ -f "requirements.txt" ]; then
    pip install --upgrade pip > /dev/null
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
    echo -e "${YELLOW}Note: Use 'python -m prompt_runner.cli' to run (prompt-runner command not available)${NC}"
else
    echo -e "${RED}Error: Neither pyproject.toml nor requirements.txt found${NC}"
    exit 1
fi
echo ""

# Step 4: Create .env from template
echo -e "${YELLOW}[4/5] Setting up environment configuration...${NC}"
if [ -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env already exists${NC}"
    read -p "Overwrite with .env.example? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env overwritten from template${NC}"
    else
        echo -e "${YELLOW}Keeping existing .env${NC}"
    fi
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env created from template${NC}"
    else
        echo -e "${RED}Error: .env.example not found${NC}"
        exit 1
    fi
fi
echo ""

# Step 5: Validate directory structure
echo -e "${YELLOW}[5/5] Validating project structure...${NC}"
REQUIRED_DIRS=("prompt_runner" "tools/mcp")
REQUIRED_FILES=("prompt_runner/cli.py" "prompt_runner/openai_session.py" "tools/mcp/mcp_bridge.py")

all_valid=true
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo -e "${RED}✗ Missing directory: $dir${NC}"
        all_valid=false
    fi
done

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ Missing file: $file${NC}"
        all_valid=false
    fi
done

if [ "$all_valid" = true ]; then
    echo -e "${GREEN}✓ Project structure validated${NC}"
else
    echo -e "${RED}Error: Project structure is incomplete${NC}"
    exit 1
fi
echo ""

# Final instructions
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo -e "1. ${BLUE}Configure your API keys:${NC}"
echo "   Edit .env and set:"
echo "     - OPENAI_API_KEY (get from https://platform.openai.com/api-keys)"
echo "     - MCP_ENDPOINT (your HoloMem MCP server URL)"
echo ""
echo -e "2. ${BLUE}Load environment variables:${NC}"
echo "   source .env"
echo ""
echo -e "3. ${BLUE}Activate virtual environment:${NC}"
echo "   source venv/bin/activate"
echo ""
echo -e "4. ${BLUE}Run your first analysis:${NC}"
echo "   # Using shell script wrapper"
echo "   ./run_drift.sh <namespace> <checkpoint-a> <checkpoint-b>"
echo ""
echo "   # Or using prompt-runner command directly"
echo "   prompt-runner --namespace <namespace> --prompt-id drift_analysis ..."
echo ""
echo "   # Or using Python module (if not installed with pip)"
echo "   python -m prompt_runner.cli --namespace <namespace> --prompt-id drift_analysis ..."
echo ""
echo -e "For detailed usage, see: ${GREEN}README.md${NC}"
echo ""
echo -e "${YELLOW}Important:${NC} Make sure your MCP server is running before executing prompts!"
echo ""
