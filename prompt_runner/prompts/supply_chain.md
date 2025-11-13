Please perform a Supply Chain Analysis for the source code in namespace `{code_namespace}` and use vulnerability reports in `{vuln_namespace}` namespace.

**IMPORTANT OPTIMIZATION:** All dependency and vulnerability data is pre-aggregated in the `{manifest_concept}` concept in `{code_namespace}` namespace. This concept contains all the information you need including dependencies, versions, and associated vulnerabilities. Fetch this concept ONCE and analyze its contents directly. Do NOT perform additional graph traversal, cross-namespace searches, or path queries unless absolutely necessary - all required data is already consolidated in this single concept.

**Efficient Analysis Steps:**
1. Fetch `{manifest_concept}` from `{code_namespace}` namespace (single call to holomem_get_concept or holomem_get)
2. Analyze the aggregated dependency and vulnerability data from the concept
3. Generate the comprehensive report below

Use HoloMem only. Do not use cached results. Summarise findings in the next template:
```
# QQ Response Template

## 1. Executive Summary (Plain English)
- **Objective:** <short statement of the user's goal>
- **Key Findings:** <bulleted highlights of what the analysis uncovered>
- **Immediate Actions:** <bulleted list of top remediation steps>

## 2. Technical Breakdown (Engineer-Facing)
- **Namespaces:**
  - Vulnerabilities: `{vuln_namespace}`
  - Source code: `{code_namespace}`
- **HoloMem Queries & Findings:**
  1. `<query>` → `<result/interpretation>`
  2. `<query>` → `<result/interpretation>`
- **Evidence & References:**
  - `<evidence concept>` → `<URL / summary>`
  - `<session metrics>` → `<notable CVE deltas or drift scores>`

## 3. Remediation Plan
- **Affected Components:** <list of entrypoints, packages, versions>
- **Required Upgrades / Fixes:** <versions or patches>
- **ART Workflow:**
  1. Proposal: `<proposal concept>`
  2. Actions: `<what to run>`
  3. Acceptance: `<gate thresholds (drift score, CVE added)>`

## 4. Validation & Follow-up
- **Acceptance Tests:** <tests to rerun or criteria to verify success>
- **Monitoring Hooks:** <metrics/alerts to watch>
- **Next Review:** <date or trigger>
```

When you have gathered enough evidence via HoloMem tools, you must finish by returning exactly one JSON object:

{{"final_summary": "<markdown report filling the QQ template above>"}}
