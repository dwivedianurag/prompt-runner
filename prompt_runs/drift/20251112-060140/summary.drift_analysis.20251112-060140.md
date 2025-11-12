# QQ Drift Analysis Template

## 1. Executive Summary (Plain English)
- **Objective:** Compare two checkpoints for namespace `ns-dra-llm-v3-prompt-cli`: baseline `20251112-004129-holomem_graph.ns-dra-llm-v3-prompt-cli.npz` vs current `20251112-000526-holomem_graph.ns-dra-llm-v3-prompt-cli.npz` using the provided holomem_diffImpact evidence and report all drift types (API surface, semantic, architecture).
- **Key Findings:**
  - **API Surface Drift:** No new top-level symbols were added according to the provided diff evidence ("added": []). There are no explicit node deletions reported, but the call-graph shows many removed call edges from CLI and OpenAI session internals — indicating probable refactor, removal or relocation of call sites (e.g., parser construction, argument registration, tool-invocation helpers). This is an API-surface-altering change in behavior (callers no longer invoking the same helpers) though symbol-level additions/removals are not recorded as added/deleted nodes.
  - **Semantic Drift:** Substantial behavioral deltas are implied: CLI parser-building and variable-loading routines no longer call their former helpers (ArgumentParser, add_argument, getenv, float conversions); OpenAISession routines show removed calls to JSON parsing, tool invocation, logging, and timestamping helpers. These removals likely change runtime behavior (parsing, tool calls, response extraction, time-stamping).
  - **Architecture Drift:** The call-graph has been substantially pruned: dozens of call edges removed (no new edges added). This reduces coupling to several helper utilities and external interactions (file IO, env reads, JSON loads, tool invocation). No new cycles or increased dependency edges are visible in the evidence; instead there is a net removal of call dependencies.
- **Immediate Actions:**
  1. Inspect the commit log or source diff that produced the two checkpoints to determine if the removed call edges are intentional (refactor / move) or accidental (regression).
  2. Run unit and integration tests that exercise CLI parsing, namespace readiness, OpenAI session tool invocation, and response parsing. Pay special attention to tests around _build_parser, _build_variables, _ensure_namespace_ready, OpenAISession.run.
  3. If the change is unintended, restore from the baseline checkpoint or revert the code change; if intended, update documentation and tests to reflect new behavior.

## 2. Technical Breakdown (Engineer-Facing)
- **Namespaces:**
  - Baseline Snapshot: `ns-dra-llm-v3-prompt-cli` @ `20251112-004129-holomem_graph.ns-dra-llm-v3-prompt-cli.npz`
  - Current Snapshot: `ns-dra-llm-v3-prompt-cli` @ `20251112-000526-holomem_graph.ns-dra-llm-v3-prompt-cli.npz`

- **HoloMem Queries & Findings:**
  1. holomem_diffImpact (baseline -> current) → evidence block provided as input. Summary: "added": [] (no newly added call edges/nodes). The diffImpact result lists a sizable set of "impacted" concepts (CLI helpers and OpenAISession internals). The diffImpact removed array contains many call edges that existed in baseline but not in current.
     - Representative removed call edges (from provided evidence):
       - prompt_runner.cli._build_parser -> calls -> prompt_runner.cli.ArgumentParser
       - prompt_runner.cli._build_parser -> calls -> prompt_runner.cli.add_argument
       - prompt_runner.cli._build_variables -> calls -> prompt_runner.cli.getenv / .get / .items
       - prompt_runner.cli._ensure_namespace_ready -> calls -> prompt_runner.cli._extract_results / _timestamp_dir / call
       - prompt_runner.openai_session.OpenAISession.__init__ -> calls -> prompt_runner.openai_session.OpenAI / _resolve_content_type / getenv
       - prompt_runner.openai_session.OpenAISession.run -> calls -> _extract_text / _invoke_tool / _log / _parse_json / ToolCallResult / _maybe_flip_content_type
       - prompt_runner.openai_session._sanitize_json_text -> calls -> _extract_json_block / loads / split / strip
     - The evidence block shows device/dimension/dtype and the Q2MARS Thm. 1 guarantee for retrieval reliability (included in the provided evidence meta).

  2. holomem_find_paths (lens="aliases") → (interpreted from call removal patterns) The removed edges indicate that many previously present call paths from top-level CLI main to helper utilities (MCPClient, OpenAISession, parse/build helpers, file IO helpers) are no longer present. This implies changes to the CLI entrypoint behaviors and the surface visible to users running the CLI (e.g., fewer side effects or absent initialization steps).

  3. holomem_get_program_slice (interpreted by inspecting impacted function set) → OpenAISession internals (run, _extract_text, _parse_json, _invoke_tool) previously formed a pipeline: receive response → extract text → optionally invoke tools → parse JSON → log/write outputs. Many calls in that pipeline are removed in the current checkpoint, implying semantic changes to that pipeline.

- **Drift Details:**
  - **API Surface Drift:**
    - Added: None recorded in provided evidence ("added": []).
    - Removed: No explicit node deletions are shown as top-level removals, but call relationships were removed. The following functions lost call edges (representative list):
      - prompt_runner.cli._build_parser (lost calls to ArgumentParser, add_argument)
      - prompt_runner.cli._build_variables (lost calls to getenv, get, items, str, SystemExit)
      - prompt_runner.cli._ensure_namespace_ready (lost calls to _extract_results, _timestamp_dir, call)
      - prompt_runner.cli._env_float (lost calls to float, getenv)
      - prompt_runner.cli._extract_results (lost get, isinstance)
      - prompt_runner.cli._load_text (lost read_text)
      - prompt_runner.cli._timestamp_dir (lost now, strftime)
      - prompt_runner.cli.main (lost calls to MCPClient, OpenAISession, Path, many helper functions including parse_args, load_manifest, load_tool_catalog, run, write_text)
      - prompt_runner.openai_session.OpenAISession.__init__ (lost calls to OpenAI, RuntimeError, _resolve_content_type, getenv, max, mkdir, write_text)
      - prompt_runner.openai_session.OpenAISession._extract_text (lost RuntimeError, get, getattr, hasattr, isinstance)
      - prompt_runner.openai_session.OpenAISession._invoke_tool (lost MCPClient, _log, RuntimeError, ThreadPoolExecutor, _next_wait_interval, cancel, merge_args, submit, result)
      - prompt_runner.openai_session.OpenAISession._parse_json (lost RuntimeError, _sanitize_json_text, loads)
      - prompt_runner.openai_session.OpenAISession.run (lost _extract_text, _invoke_tool, _log, _parse_json, ToolCallResult, _maybe_flip_content_type, append, create, dumps, get, isinstance, len, str, strip)
      - prompt_runner.openai_session._sanitize_json_text (lost _extract_json_block, len, loads, lstrip, split, startswith, strip)

    - Signature Changes: The diff evidence does not explicitly show parameter list diffs or return-type changes for named nodes; it only shows that call edges were removed. Absence of call edges can indicate that either signatures changed (call sites removed because parameters no longer match) or that the callers no longer need the callee. To confirm parameter/return-type changes, examine the source diff — the provided evidence only implies that call relationships changed.

  - **Semantic Drift:**
    - prompt_runner.cli._build_parser → Behavior changed: previously this routine constructed an ArgumentParser and registered arguments via add_argument; since both calls are removed, the CLI may no longer build/accept the same arguments or may have migrated parser construction elsewhere. Practical effect: command-line flags or options may be missing or altered.

    - prompt_runner.cli._build_variables → Behavior changed: calls to getenv/float/str/get/items/SystemExit were removed; this implies environment variable parsing, default handling, conversions to float, and exit-on-missing behavior may have changed. Defaults could differ, and error conditions (SystemExit) may no longer be raised as before.

    - prompt_runner.cli._ensure_namespace_ready → Behavior changed: loss of calls to _extract_results, _timestamp_dir, call indicates that namespace readiness checks (and any result extraction or timestamped directory creation) have been removed or relocated. This can alter startup sequencing and persistence behavior.

    - prompt_runner.openai_session.OpenAISession.run and related internals → Behavior changed: removed calls show the session no longer (as per the baseline call-graph) calling the JSON parsing pipeline, tool invocation pipeline (MCPClient invocation and ThreadPoolExecutor usage), content-type resolution, and logging/timestamping helpers. This implies that responses may not be parsed into structured JSON, tool calls may no longer be issued, error handling (RuntimeError) might behave differently, and logging/timestamps may be suppressed or relocated. Defaults around content type (JSON vs text) and how tool outputs are turned into ToolCallResult objects are likely changed.

    - prompt_runner.openai_session._sanitize_json_text and _extract_json_block → Behavior changed: JSON sanitation path (extraction, stripping, lstrip, split, startswith checks) no longer connected — risk of unparsed/invalid JSON being passed into loads or greater susceptibility to malformed model outputs.

    - Overall semantic consequence: the CLI and the OpenAI session pipeline appear to have been simplified or partially removed, which could manifest as missing features (no tool invocation, fewer CLI options), changed default handling, or altered error modes.

  - **Architecture Drift:**
    - New Dependencies: None recorded ("added": []). The evidence does not show any newly-introduced call edges or imports.

    - Removed/Reversed Edges: Many removed call edges (dozens). Representative removed callers and callees are enumerated above. That indicates reduced coupling from top-level CLI functions into many helper utilities and from OpenAISession internals into parsing/tooling/logging helpers.

    - Cycles Introduced: No cycles were reported in the provided evidence. The diff shows only removed edges; no newly-introduced cycles are visible.

- **Evidence & References:**
  - diffImpact evidence (provided): the primary artifact used for this analysis. Key slices:
    - "added": [] (no added call edges or new nodes)
    - "impacted": [list of CLI and OpenAISession symbols] — these symbols are the focus of the change set.
    - "removed": [detailed list of removed call edges] — used to identify behavioral and architectural drift.
  - Representative removed call examples (quote from evidence):
    - ["prompt_runner.cli._build_parser", "calls", "prompt_runner.cli.ArgumentParser"]
    - ["prompt_runner.openai_session.OpenAISession.run", "calls", "prompt_runner.openai_session.OpenAISession._invoke_tool"]
    - ["prompt_runner.openai_session._sanitize_json_text", "calls", "prompt_runner.openai_session._extract_json_block"]
  - Session / meta: evidence contains Q2MARS Thm.1 guarantee and retrieval params (N=171, dimension=128 float32) — indicates reliable retrieval of the diff data.

## 3. Remediation Plan
- **Affected Components:**
  - Modules: prompt_runner.cli, prompt_runner.openai_session
  - Functions: _build_parser, _build_variables, _ensure_namespace_ready, _env_float, _extract_results, _load_text, _timestamp_dir, main, OpenAISession.__init__, OpenAISession.run, OpenAISession._invoke_tool, OpenAISession._parse_json, _sanitize_json_text, _extract_text

- **Required Fixes / Follow-up:**
  1. Source Diff Inspection: Retrieve the code diff/commit between the two checkpoints to determine whether removed call edges correspond to intentional refactors (moved logic) or regressions (accidental deletion). If a refactor, find the new call sites and update call-graph tracking/annotations; if regression, plan a revert.
  2. Unit & Integration Tests: Add/execute tests covering:
     - CLI argument parsing (coverage for add_argument calls and expected flags)
     - Environment-variable parsing and float conversions (cover _env_float paths)
     - Namespace readiness flow (ensuring _ensure_namespace_ready runs expected side-effects)
     - OpenAISession end-to-end: content-type resolution, JSON sanitation, tool invocation, and logging/timestamping
  3. Monitoring & Logging: Add telemetry that triggers if OpenAISession.run does not invoke tool-call paths when expected (e.g., if a plan requires tool calls but none are made). Validate content-type headers and JSON parsing success rates.
  4. Documentation: If change is intentional, update README and CLI docs to reflect new flags/behavior and update any API compatibility notes for external users.

- **ART Workflow:**
  1. Proposal: Create a proposal concept node in the graph (e.g., "proposal.fix.cli-and-openai-drift") describing the intended remediation and expected behavioral contract.
  2. Actions: Run the following validation steps before merging a fix:
     - Re-run holomem_diffImpact locally after applying fixes to ensure removed edges are restored or their replacements are visible.
     - Run the targeted test suites (CLI unit tests, integration tests for OpenAISession tool invocation) and require 100% pass for changed features.
     - Perform a dry_run for ART synthesize/whatIf to predict impacts on call graph and test coverage.
  3. Acceptance: Require that regression drift score (measured as the count of removed critical call edges affecting runtime features) be reduced to zero for critical paths (parser construction and OpenAISession tool invocation) and that tests validate behavior. Set thresholds: no missing tool-invocation edges, no missing parser args, and JSON parsing error-rate < 0.5% in staging.

## 4. Validation & Follow-up
- **Regression Tests:**
  - CLI: tests that assert presence and behavior of the command-line options previously added via add_argument; tests asserting environment variable parsing and float conversion.
  - OpenAISession: end-to-end tests that simulate model output containing JSON blocks, asserting that _extract_text → _sanitize_json_text → _parse_json flow produces expected structured results; tests that verify MCP tool invocation is exercised and that ToolCallResult objects are created when appropriate.
  - Namespace readiness: tests that call the CLI entrypoint flow and assert that namespace directories are timestamped/created and that results extraction occurs.

- **Monitoring Hooks:**
  - Add alerts for spikes in parsing errors (exceptions during json.loads or increased RuntimeError counts) originating from OpenAISession.
  - Add metrics for tool-invocation counts per session (if expected > 0, alert if 0 over a window).
  - Track the presence/absence of key call-graph edges in subsequent holomem_diffImpact runs (automate periodic diffs and flag regressions).

- **Next Review:**
  - Immediate: review commit diffs and run tests today (within 24 hours) to triage whether this is intended refactor vs regression.
  - Follow-up checkpoint: create a new checkpoint after fixes and re-run holomem_diffImpact; schedule a review at next release milestone or when drift is resolved.


-- End of report --

Notes: Analysis is derived solely from the provided holomem_diffImpact evidence for namespace `ns-dra-llm-v3-prompt-cli` (baseline vs current). The evidence shows no added call edges but many removed call edges affecting CLI parser construction and the OpenAISession tool/JSON/logging pipeline; these removals drive the conclusions above.