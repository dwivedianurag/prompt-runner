# LLM Orchestrator

An LLM-driven MCP (Model Context Protocol) prompt runner for autonomous interaction with HoloMem (quantum-graph-based knowledge substrate). The orchestrator uses OpenAI models to execute structured prompts that analyze code drift, supply chain vulnerabilities, and other software engineering tasks.

## Features

- **Autonomous Tool Selection**: LLM decides which HoloMem tools to use based on the prompt
- **Drift Analysis**: Compare two checkpoints for API surface, semantic, and architecture drift
- **Supply Chain Analysis**: Cross-namespace vulnerability and dependency analysis
- **Smart Response Truncation**: Automatically compress large tool responses to prevent context overflow
- **Structured Output**: Timestamped logs, summaries, and tool call records

## Prerequisites

- **Python**: 3.10 or higher
- **OpenAI API Key**: For GPT-4/GPT-5 access
- **MCP Endpoint**: Running HoloMem MCP server (default: `http://127.0.0.1:8085/mcp`)
- **HoloMem Namespace**: Pre-populated namespace with code concepts and checkpoints

## Quick Start

### 1. Unzip and Navigate
```bash
unzip llm-orchestrator.zip
cd llm-orchestrator
```

### 2. Set Up Environment

**Option A: Using Setup Script (Recommended)**
```bash
./setup.sh
```

**Option B: Manual Setup with Pip Install (Recommended)**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .          # Install package in editable mode
cp .env.example .env
```

**Option C: Manual Setup without Pip Install**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Configure Environment Variables
Edit `.env` and set:
```bash
export OPENAI_API_KEY="sk-proj-..."
export OPENAI_MODEL="gpt-4o-mini"  # or "gpt-5" for larger context
export MCP_ENDPOINT="http://127.0.0.1:8085/mcp"
```

### 4. Load Environment
```bash
source .env
```

### 5. Run a Prompt
```bash
# Using shell script (recommended)
./run_drift.sh ns-dra-fastapi-10 checkpoint-a checkpoint-b

# Using prompt-runner command (if installed with pip install -e .)
prompt-runner \
  --namespace ns-dra-fastapi-10 \
  --prompt-id drift_analysis \
  --checkpoint-a 20251110-170934-holomem_graph.ns-dra-fastapi-10.npz \
  --checkpoint-b 20251111-160629-holomem_graph.ns-dra-fastapi-10.npz

# Or using Python module directly (without pip install)
python -m prompt_runner.cli \
  --namespace ns-dra-fastapi-10 \
  --prompt-id drift_analysis \
  --checkpoint-a 20251110-170934-holomem_graph.ns-dra-fastapi-10.npz \
  --checkpoint-b 20251111-160629-holomem_graph.ns-dra-fastapi-10.npz
```

## Installation

### Method 1: Pip Install (Recommended)

Installing with pip provides a `prompt-runner` console command and handles all dependencies:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable/development mode
pip install -e .

# Or install from built package
pip install llm-orchestrator-1.0.0.tar.gz
```

**Benefits:**
- Creates `prompt-runner` console command
- Automatic dependency management
- Proper package installation

### Method 2: Manual Dependencies

If you prefer not to install the package:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Note:** With this method, you must use `python -m prompt_runner.cli` instead of `prompt-runner`.

### Method 3: Setup Script

Run the automated setup script:

```bash
./setup.sh
```

This script will:
- Check Python version
- Create virtual environment
- Install the package with pip
- Create `.env` from template
- Validate project structure

## Usage

### CLI Commands

Both command formats are supported:

```bash
# If installed with pip:
prompt-runner [options]

# If using manual dependencies:
python -m prompt_runner.cli [options]
```

The examples below use `prompt-runner` for brevity. Replace with `python -m prompt_runner.cli` if not installed via pip.

#### Drift Analysis

**Full Command:**
```bash
prompt-runner \
  --namespace <namespace> \
  --prompt-id drift_analysis \
  --checkpoint-a <baseline-checkpoint-id> \
  --checkpoint-b <current-checkpoint-id> \
  [--verbose] \
  [--quiet] \
  [--output-dir prompt_runs] \
  [--no-truncate-responses] \
  [--tool-timeout 45] \
  [--heartbeat-interval 5] \
  [--preflight-tool <tool>=<json-args>] \
  [--no-preflight]
```

**Example:**
```bash
prompt-runner \
  --namespace ns-dra-fastapi-10 \
  --prompt-id drift_analysis \
  --checkpoint-a 20251110-170934-holomem_graph.ns-dra-fastapi-10.npz \
  --checkpoint-b 20251111-160629-holomem_graph.ns-dra-fastapi-10.npz \
  --verbose
```

#### Supply Chain Analysis

**Full Command:**
```bash
prompt-runner \
  --prompt-id supply_chain \
  --code-namespace <code-namespace> \
  --vuln-namespace <vulnerability-namespace> \
  --manifest-concept <manifest-concept-name> \
  [--verbose] \
  [--quiet] \
  [--output-dir prompt_runs] \
  [--no-truncate-responses] \
  [--tool-timeout 180] \
  [--heartbeat-interval 5] \
  [--preflight-tool <tool>=<json-args>] \
  [--no-preflight]
```

**Example:**
```bash
prompt-runner \
  --prompt-id supply_chain \
  --code-namespace ns-code-main \
  --vuln-namespace ns-vuln-db \
  --manifest-concept manifest.current \
  --verbose
```

#### Handshake Only (No Prompt Execution)

**Command:**
```bash
prompt-runner --namespace <namespace>
```

**Example:**
```bash
prompt-runner --namespace ns-dra-fastapi-10
```

This performs namespace handshake and validation without running any prompts.

#### Multiple Prompts

You can run multiple prompts sequentially by repeating `--prompt-id`:
```bash
prompt-runner \
  --namespace ns-dra-fastapi-10 \
  --prompt-id drift_analysis \
  --checkpoint-a checkpoint-a-id \
  --checkpoint-b checkpoint-b-id \
  --prompt-id supply_chain \
  --project-name my-project \
  --code-namespace ns-code \
  --vuln-namespace ns-vuln \
  --manifest-concept manifest.current
```

### CLI Parameters Reference

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `--namespace` | Target HoloMem namespace | `ns-dra-llm-v3-prompt-cli` | No |
| `--prompt-id` | Prompt to execute (`drift_analysis`, `supply_chain`). Repeatable for multiple prompts. | None | No* |
| `--checkpoint-a` | Baseline checkpoint ID (drift analysis only) | None | Yes (for drift) |
| `--checkpoint-b` | Current checkpoint ID (drift analysis only) | None | Yes (for drift) |
| `--code-namespace` | Namespace containing source code concepts (supply chain) | None | Yes (for supply chain) |
| `--vuln-namespace` | Namespace containing vulnerability data (supply chain) | None | Yes (for supply chain) |
| `--manifest-concept` | Manifest concept name, e.g., `manifest.current` (supply chain) | None | Yes (for supply chain) |
| `--verbose` | Print progress messages while running | `False` | No |
| `--quiet` | Suppress console output (logs still written to files) | `False` | No |
| `--output-dir` | Directory to store run artifacts | `prompt_runs` | No |
| `--no-truncate-responses` | Disable automatic response truncation (enabled by default to prevent context overflow) | `False` | No |
| `--tool-timeout` | Seconds to wait for each MCP call before timing out | `180` (or `PROMPT_RUNNER_TOOL_TIMEOUT`) | No |
| `--heartbeat-interval` | Seconds between heartbeat logs while waiting on MCP tools | `5` (or `PROMPT_RUNNER_HEARTBEAT`) | No |
| `--max-tool-calls` | Maximum number of MCP tool calls allowed per prompt execution | `20` | No |
| `--preflight-tool` | Require an MCP tool to run before the main prompt (format: `tool` or `tool=<JSON args>`). Repeatable. | Auto (namespace switch/get) | No |
| `--no-preflight` | Disable automatic preflight tool instructions | `False` | No |

**Note:** If no `--prompt-id` is specified, only the handshake is performed.

### Shell Script Wrappers

#### Drift Analysis Script

**Usage:**
```bash
./run_drift.sh <namespace> <checkpoint-a> <checkpoint-b> [options]
```

**Example:**
```bash
./run_drift.sh \
  ns-dra-fastapi-10 \
  20251110-170934-holomem_graph.ns-dra-fastapi-10.npz \
  20251111-160629-holomem_graph.ns-dra-fastapi-10.npz \
  --verbose
```

**Options:** Same as CLI flags (e.g., `--verbose`, `--no-truncate-responses`)

#### Supply Chain Analysis Script

**Usage:**
```bash
./run_supply_chain.sh <code-namespace> <vuln-namespace> <manifest-concept> [options]
```

**Example:**
```bash
./run_supply_chain.sh \
  ns-code-main \
  ns-vuln-db \
  manifest.current \
  --verbose
```

**Options:** Same as CLI flags (e.g., `--verbose`, `--quiet`, `--tool-timeout`)

## Output Structure

All prompt runs generate timestamped output in the `prompt_runs/` directory:

```
prompt_runs/
├── drift/
│   └── 20251112-055102/
│       ├── status.drift_analysis.20251112-055102.log       # Status/debug log
│       ├── summary.drift_analysis.20251112-055102.md       # Final markdown report
│       ├── prompt.drift_analysis.20251112-055102.log       # Tool call log (JSON lines)
│       └── raw_responses.log                                # Raw OpenAI API responses
├── supply_chain/
│   └── 20251112-060045/
│       ├── status.supply_chain.20251112-060045.log
│       ├── summary.supply_chain.20251112-060045.md
│       ├── prompt.supply_chain.20251112-060045.log
│       └── raw_responses.log
└── handshake/
    └── 20251112-082604/
        ├── status.handshake.20251112-082604.log
        └── raw_responses.log
```

### Output Files

- **`status.*.log`**: Progress messages, tool calls, errors, and execution timeline
- **`summary.*.md`**: Final markdown report following the prompt's template (drift or supply chain)
- **`prompt.*.log`**: JSON lines log of all tool calls with arguments and responses
- **`raw_responses.log`**: Raw OpenAI API response objects for debugging

## Environment Variables

### Required

- **`OPENAI_API_KEY`**: Your OpenAI API key (starts with `sk-proj-...`)
- **`MCP_ENDPOINT`**: HoloMem MCP server endpoint URL

### Optional

- **`OPENAI_MODEL`**: Model to use (default: `gpt-4o-mini`)
  - Options: `gpt-4o-mini`, `gpt-4o`, `gpt-5-mini`, `gpt-5`
  - Context limits: GPT-4o (128K tokens), GPT-5 (200K tokens)
- **`PROMPT_RUNNER_TOOL_TIMEOUT`**: Default tool timeout in seconds (overridden by `--tool-timeout`)
- **`PROMPT_RUNNER_HEARTBEAT`**: Default heartbeat interval in seconds (overridden by `--heartbeat-interval`)
- **`PROMPT_RUNNER_PREFLIGHT_TOOLS`**: Comma-separated list of preflight tools (overridden by `--preflight-tool`)
- **`OPENAI_CONTENT_TYPE`**: Override content type (`input_text` or `output_text`). **Not recommended unless debugging.**

### Loading Environment

```bash
# From .env file
source .env

# Or inline
export OPENAI_API_KEY="sk-proj-..."
export OPENAI_MODEL="gpt-4o-mini"
export MCP_ENDPOINT="http://127.0.0.1:8085/mcp"
```

## Response Truncation

By default, the orchestrator automatically truncates large tool responses (>8000 characters) to prevent context overflow. This feature is especially useful for responses from `holomem_diffImpact` which can be very large.

### Truncation Behavior

- **Enabled by default**: Responses >8000 chars are compressed before adding to LLM context
- **Full responses preserved**: Complete responses always saved to log files
- **Smart truncation**:
  - For `holomem_diffImpact`: Keeps first 3 items from added/removed/impacted arrays, full evidence metadata, adds `_original_counts`
  - For other tools: Keeps first 5 keys, first 5 items per list/dict, adds `_truncated` flag

### Disabling Truncation

For debugging or when you need full responses in context:
```bash
python -m prompt_runner.cli \
  --namespace ns-dra-fastapi-10 \
  --prompt-id drift_analysis \
  --checkpoint-a checkpoint-a \
  --checkpoint-b checkpoint-b \
  --no-truncate-responses
```

**Warning:** Disabling truncation may cause context length exceeded errors with large responses.

## Available Prompts

### 1. Drift Analysis (`drift_analysis`)

Compares two HoloMem checkpoints to detect:
- **API Surface Drift**: Added/removed functions, signature changes
- **Semantic Drift**: Logic changes, control flow modifications, default value changes
- **Architecture Drift**: New dependencies, reversed edges, introduced cycles

**Required Variables:**
- `namespace`: Target namespace
- `checkpoint_a`: Baseline checkpoint ID
- `checkpoint_b`: Current checkpoint ID

**Output:** Markdown report with executive summary, technical breakdown, remediation plan, and validation steps.

### 2. Supply Chain Analysis (`supply_chain`)

Cross-namespace analysis of project dependencies and vulnerabilities:
- Dependency tree analysis
- CVE mapping from vulnerability database
- Supply chain risk assessment
- Remediation recommendations

**Required Variables:**
- `project_name`: Name of the project
- `code_namespace`: Namespace containing source code and manifests
- `vuln_namespace`: Namespace containing vulnerability data
- `manifest_concept`: Concept name of the manifest (e.g., `manifest.current`)

**Output:** Markdown report with findings, evidence, remediation plan, and validation steps.

## Troubleshooting

### Context Length Exceeded

**Error:** `openai.BadRequestError: Error code: 400 - {'error': {'message': 'context_length_exceeded', ...}}`

**Solutions:**
1. **Use response truncation** (enabled by default)
2. **Switch to a larger model:**
   ```bash
   export OPENAI_MODEL="gpt-5"  # 200K context vs 128K for gpt-4o
   ```
3. **Tool filtering is already enabled** per prompt (only relevant tools included)

### Endless Loop / Too Many Requests

**Symptoms:** Handshake log shows hundreds or thousands of requests

**Solution:** This has been fixed in the current version. If you still encounter this:
1. Check that `prompt_runner/openai_session.py` has the content type fix
2. Verify environment variables are set correctly
3. Check MCP endpoint is responding

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'openai'`

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Error:** `RuntimeError: mcp_bridge module is required for prompt runner`

**Solution:** Ensure the `tools/mcp/` directory is present in the project root.

### MCP Connection Errors

**Error:** `Connection refused` or `MCP endpoint unreachable`

**Solution:**
1. Verify MCP server is running: `curl http://127.0.0.1:8085/mcp`
2. Check `MCP_ENDPOINT` in `.env` matches your server
3. Ensure firewall/network allows connection to MCP port

### Tool Timeout

**Error:** `MCP call 'tool_name' timed out after 45s`

**Solution:**
```bash
# Increase timeout
python -m prompt_runner.cli \
  --namespace ns-dra-fastapi-10 \
  --prompt-id drift_analysis \
  --checkpoint-a checkpoint-a \
  --checkpoint-b checkpoint-b \
  --tool-timeout 120
```

### Invalid JSON Response

**Error:** `LLM response is not valid JSON`

**Cause:** LLM returned text instead of required JSON format

**Solution:** This is usually transient. Re-run the prompt. If persistent:
1. Check that prompt templates in `prompt_runner/prompts/` have clear instructions
2. Try a different model (e.g., `gpt-5` instead of `gpt-4o-mini`)

## Project Structure

```
llm-orchestrator/
├── README.md                          # This file
├── pyproject.toml                     # Package configuration (pip install)
├── .env.example                       # Environment variable template
├── .env                               # Your environment variables (git-ignored)
├── requirements.txt                   # Python dependencies (manual install)
├── setup.sh                           # One-time setup script
├── run_drift.sh                       # Drift analysis wrapper script
├── run_supply_chain.sh                # Supply chain analysis wrapper script
├── prompt_runner/                     # Core orchestrator package
│   ├── __init__.py
│   ├── cli.py                         # CLI entry point
│   ├── openai_session.py              # LLM session management
│   ├── mcp_client.py                  # MCP bridge client
│   ├── tool_catalog.py                # Tool spec loading
│   ├── prompt_manifest.py             # Prompt metadata loading
│   ├── toolspecs.json                 # HoloMem tool definitions
│   └── prompts/                       # Prompt templates and metadata
│       ├── manifest.json              # Prompt registry
│       ├── drift_analysis.md          # Drift analysis prompt
│       ├── supply_chain.md            # Supply chain prompt
│       ├── Holomem-API-reference.md   # HoloMem API documentation
│       └── mcp_tools_reference.md     # MCP tools reference
├── tools/                             # MCP bridge and tools
│   └── mcp/
│       ├── mcp_bridge.py              # MCP protocol implementation
│       ├── loader.py                  # Tool loader
│       ├── models.py                  # Data models
│       └── holomem.mcp.config         # HoloMem MCP configuration
└── prompt_runs/                       # Output directory (created on first run)
    ├── drift/                         # Drift analysis outputs
    ├── supply_chain/                  # Supply chain outputs
    └── handshake/                     # Handshake logs
```

## Advanced Usage

### Custom Preflight Tools

Run specific MCP tools before the main prompt:
```bash
python -m prompt_runner.cli \
  --namespace ns-dra-fastapi-10 \
  --prompt-id drift_analysis \
  --checkpoint-a checkpoint-a \
  --checkpoint-b checkpoint-b \
  --preflight-tool holomem_describe_namespace \
  --preflight-tool 'holomem_find_by_query={"namespace":"ns-dra-fastapi-10","query":{"has":{"is_a":"proposal"}},"topk":5}'
```

### Disable Preflight

Skip automatic namespace handshake (not recommended):
```bash
python -m prompt_runner.cli \
  --namespace ns-dra-fastapi-10 \
  --prompt-id drift_analysis \
  --checkpoint-a checkpoint-a \
  --checkpoint-b checkpoint-b \
  --no-preflight
```

### Environment Variable Overrides

Override CLI defaults via environment variables:
```bash
export PROMPT_RUNNER_TOOL_TIMEOUT=120
export PROMPT_RUNNER_HEARTBEAT=10
export PROMPT_RUNNER_PREFLIGHT_TOOLS="holomem_switch_to_namespace,holomem_get_current_namespace"

python -m prompt_runner.cli \
  --namespace ns-dra-fastapi-10 \
  --prompt-id drift_analysis \
  --checkpoint-a checkpoint-a \
  --checkpoint-b checkpoint-b
```

## Integration Examples

### CI/CD Pipeline

```bash
#!/bin/bash
# ci-drift-check.sh

set -e

# Load environment
source .env

# Get latest two checkpoints
CHECKPOINTS=$(ls -t /path/to/checkpoints/ | head -2)
CHECKPOINT_B=$(echo "$CHECKPOINTS" | sed -n 1p)
CHECKPOINT_A=$(echo "$CHECKPOINTS" | sed -n 2p)

# Run drift analysis
python -m prompt_runner.cli \
  --namespace ns-ci-${CI_PIPELINE_ID} \
  --prompt-id drift_analysis \
  --checkpoint-a "$CHECKPOINT_A" \
  --checkpoint-b "$CHECKPOINT_B" \
  --quiet

# Check for breaking changes
if grep -q "API Surface Drift: Yes" prompt_runs/drift/*/summary.*.md; then
  echo "BREAKING CHANGE DETECTED"
  exit 1
fi
```

### Scheduled Analysis

```bash
# crontab entry: Run drift analysis daily at 2 AM
0 2 * * * /path/to/llm-orchestrator/run_drift.sh ns-prod checkpoint-yesterday checkpoint-today --quiet
```

### Shell Script Integration

```bash
#!/bin/bash
# analyze.sh - Wrapper for drift analysis

NAMESPACE="ns-dra-fastapi-10"
CHECKPOINT_A="$1"
CHECKPOINT_B="$2"

if [ -z "$CHECKPOINT_A" ] || [ -z "$CHECKPOINT_B" ]; then
  echo "Usage: $0 <checkpoint-a> <checkpoint-b>"
  exit 1
fi

cd /path/to/llm-orchestrator
source .env
source venv/bin/activate

python -m prompt_runner.cli \
  --namespace "$NAMESPACE" \
  --prompt-id drift_analysis \
  --checkpoint-a "$CHECKPOINT_A" \
  --checkpoint-b "$CHECKPOINT_B" \
  --verbose

# Find the latest summary
LATEST_SUMMARY=$(ls -t prompt_runs/drift/*/summary.*.md | head -1)
echo "Analysis complete. Summary: $LATEST_SUMMARY"

# Optional: Send summary via email, Slack, etc.
# cat "$LATEST_SUMMARY" | mail -s "Drift Analysis Report" team@example.com
```

## Contributing

This is an internal tool. For bug reports or feature requests, contact the development team.

## License

Internal use only.
