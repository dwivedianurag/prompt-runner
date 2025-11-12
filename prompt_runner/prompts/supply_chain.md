Please perform a Supply Chain Analysis on the project `{project_name}` in namespace `{code_namespace}` and use vulnerability reports in `{vuln_namespace}` namespace. The main source of dependencies is the `{manifest_concept}` concept in `{code_namespace}` namespace. Use HoloMem only. Do not use cached results. Summarise findings in the next template:
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
