Use the precomputed Holomem evidence below to analyze code drift within the namespace `{namespace}`.
You **cannot** call any additional MCP tools; rely solely on the provided diff data.
Compare the following two checkpoints:

Baseline: `{checkpoint_a}`

Current: `{checkpoint_b}`

Your goal is to find and summarize all forms of drift between these checkpoints:

API Surface Drift — Detect any added, removed, or renamed public functions, methods, or routes. Include parameter or return-type changes.

Semantic Drift — Identify behavioral or logic differences even when the function signatures remain the same. Look for changes in control flow, condition logic, default values, or regex patterns.

Architecture Drift — Compare module imports and call graphs to detect new dependencies, reversed edges, or new cycles.

Summarise findings in the next template:
# QQ Drift Analysis Template

## 1. Executive Summary (Plain English)
- **Objective:** <what drift scenario or checkpoints you inspected>
- **Key Findings:**
  - **API Surface Drift:** <headline on additions/removals/signature shifts>
  - **Semantic Drift:** <headline on behavioral deltas>
  - **Architecture Drift:** <headline on dependency or call-graph shifts>
- **Immediate Actions:** <top remediation or verification steps driven by the drift>

## 2. Technical Breakdown (Engineer-Facing)
- **Namespaces:**
  - Baseline Snapshot: `{namespace}` @ `{checkpoint_a}`
  - Current Snapshot: `{namespace}` @ `{checkpoint_b}`
- **HoloMem Queries & Findings:**
  1. `<query (e.g., holomem_diffImpact ... )>` → `<summary of added/removed edges or impacted nodes>`
  2. `<query (e.g., holomem_find_paths … lens="aliases")>` → `<API surface interpretation>`
  3. `<query (e.g., holomem_get_program_slice …)>` → `<semantic/logic interpretation>`
- **Drift Details:**
  - **API Surface Drift:**  
    - Added: `<functions/routes introduced>`  
    - Removed: `<functions/routes removed>`  
    - Signature Changes: `<params/returns altered>`
  - **Semantic Drift:**  
    - `<function>` → `<behavioral change (control flow, defaults, regex, etc.)>`  
    - `<function>` → `<behavioral change>`
  - **Architecture Drift:**  
    - New Dependencies: `<module/import/call additions>`  
    - Removed/Reversed Edges: `<if any>`  
    - Cycles Introduced: `<if detected>`
- **Evidence & References:**
  - `<analysis concept>` → `<summary or link>`
  - `<checkpoint comparison>` → `<hash or diff summary>`
  - `<session metrics>` → `<drift score / counts>`

## 3. Remediation Plan
- **Affected Components:** <functions/modules/routes touched by drift>
- **Required Fixes / Follow-up:** <rollback, tests to add, dependency adjustments>
- **ART Workflow:**
  1. Proposal: `<proposal concept to gate changes>`
  2. Actions: `<validation steps or mitigations to run>`
  3. Acceptance: `<thresholds for residual drift or regression risk>`

## 4. Validation & Follow-up
- **Regression Tests:** <targeted suites or scenarios to rerun>
- **Monitoring Hooks:** <runtime metrics, alerts, or future diff checkpoints>
- **Next Review:** <date, release milestone, or trigger event>

When you have gathered enough evidence, you must finish by returning exactly one JSON object:

{{"final_summary": "<markdown report filling the template above>"}}

Do not emit additional tool calls after you decide to return the summary. If you already have enough information, skip extra calls and immediately respond with the `final_summary`.
