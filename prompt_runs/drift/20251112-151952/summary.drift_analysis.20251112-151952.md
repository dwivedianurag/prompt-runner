# QQ Drift Analysis Template

## 1. Executive Summary (Plain English)
- **Objective:** Compare drift between checkpoints in namespace `ns-test-phase2`:
  - Baseline: `20251110-170934-holomem_graph.ns-dra-fastapi-10.npz`
  - Current: `20251111-160629-holomem_graph.ns-dra-fastapi-10.npz`
- **Key Findings:**
  - **API Surface Drift:** Unable to complete. Tool results were not retrieved in this session, so additions/removals/signature shifts could not be enumerated.
  - **Semantic Drift:** Unable to complete. No program slice/signature diffs gathered due to missing tool responses.
  - **Architecture Drift:** Unable to complete. No call-graph/import-edge deltas were available without diff results.
- **Immediate Actions:** Re-run the analysis with HoloMem tool execution enabled and capture:
  1) holomem_diffImpact for the two checkpoints,
  2) targeted holomem_get_signature/holomem_get_program_slice on impacted functions/routes,
  3) holomem_get_function_calls for modules/functions showing changed edges.

## 2. Technical Breakdown (Engineer-Facing)
- **Namespaces:**
  - Baseline Snapshot: `ns-test-phase2` @ `20251110-170934-holomem_graph.ns-dra-fastapi-10.npz`
  - Current Snapshot: `ns-test-phase2` @ `20251111-160629-holomem_graph.ns-dra-fastapi-10.npz`
- **HoloMem Queries & Findings:**
  1. `holomem_diffImpact(from_version=..., to_version=...)` → Expected: added/removed edges and impacted nodes for API/call-graph/imports; Not executed to completion.
  2. `holomem_get_signature(symbol=...)` (for impacted functions/methods/routes) → Expected: parameter/return diffs; Not executed to completion.
  3. `holomem_get_program_slice(symbol=...)` → Expected: control-flow/logic defaults/regex changes; Not executed to completion.
  4. `holomem_get_function_calls(symbol=...)` → Expected: new dependencies/reversed edges/cycles; Not executed to completion.
- **Drift Details:**
  - **API Surface Drift:**  
    - Added: <functions/routes introduced — pending>
    - Removed: <functions/routes removed — pending>
    - Signature Changes: <params/returns altered — pending>
  - **Semantic Drift:**  
    - <function> → <behavioral change — pending>
    - <function> → <behavioral change — pending>
  - **Architecture Drift:**  
    - New Dependencies: <module/import/call additions — pending>
    - Removed/Reversed Edges: <if any — pending>
    - Cycles Introduced: <if detected — pending>
- **Evidence & References:**
  - <analysis concept> → Pending (requires tool outputs)
  - <checkpoint comparison> → Baseline: `20251110-170934-holomem_graph.ns-dra-fastapi-10.npz`; Current: `20251111-160629-holomem_graph.ns-dra-fastapi-10.npz`
  - <session metrics> → Pending (requires holomem_diffImpact response)

## 3. Remediation Plan
- **Affected Components:** Pending (functions/modules/routes not enumerated yet)
- **Required Fixes / Follow-up:**
  - Re-run HoloMem diff and targeted inspections.
  - If API changes surfaced, update clients/docs and add contract tests.
  - If semantic changes surfaced, add regression tests around modified code paths.
  - If architecture drift surfaced, review new dependencies and eliminate cycles.
- **ART Workflow:**
  1. Proposal: Create a “drift triage” concept with gating checklist (API, semantic, architecture).
  2. Actions: Run holomem_diffImpact, then inspect top-N impacted symbols with get_signature/program_slice and get_function_calls.
  3. Acceptance: Zero breaking API diffs; no new cycles; semantic diffs validated by tests; call-graph changes approved.

## 4. Validation & Follow-up
- **Regression Tests:**
  - Contract tests for public routes/functions affected by diffImpact.
  - Path-specific tests for branches touched by semantic diffs.
  - Integration tests for modules with new/reversed dependencies.
- **Monitoring Hooks:**
  - Route error-rate/latency dashboards.
  - Alerts on auth/validation failures if those areas drifted.
  - Nightly checkpoint diff runs with thresholds for alerting.
- **Next Review:**
  - After completing the tool-backed diff and targeted inspections, or before the next release cut.