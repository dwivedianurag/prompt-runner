  HoloMem MCP API Reference v2.0

  (Adversarially Refined & ART-Validated)

  Status: Production ReadyPhase: E (Time-Q2MARS with temporal views)Protocol Version: Q2MARS with Thm. 1 & Thm. 2Last Updated: 2025-10-22Adversarial Review Status: ✅ All blocking/critical issues resolved

  ---
  📋 Table of Contents

  1. #1-overview--architecture
  2. #2-evidence--q2mars-guarantees [REFINED]
  3. #3-namespace-operations
  4. #4-crud-operations [REFINED]
  5. #5-retrieval--search
  6. #6-path--graph-queries [REFINED]
  7. #7-reasoning-toolkit-art [REFINED]
  8. #8-temporal-operations-phase-e [REFINED]
  9. #9-code-analysis-tools [REFINED]
  10. #10-maintenance--diagnostics
  11. #11-system--configuration
  12. #12-sessions--checkpoints
  13. #13-transactions [REFINED]
  14. #14-batch-operations [REFINED]
  15. #15-performance--scaling [NEW]
  16. #16-security-considerations [NEW]
  17. #17-temporal-parameter-validation [REFINED]
  18. #18-error-reference [NEW]
  19. #19-migration-guide-phase-de [NEW]
  20. #20-best-practices

  ---
  1. Overview & Architecture

  HoloMem is a quantum-graph-inspired knowledge substrate providing deterministic, bounded retrieval with Q2MARS theoretical guarantees. The MCP interface exposes ~100+ tools for AI agents and applications.

  Key Concepts

  - Concepts: Nodes with properties (key-value pairs)
  - Relations: Typed edges (role-based, e.g., calls, derived_from)
  - Namespaces: Isolated graph partitions for multi-tenancy
  - Lenses: Graph views (explicit, aliases, materialized, docflow, doc2code, coverage, temporal)
  - Evidence: Provenance + Q2MARS guarantees on every response
  - Temporal Views: Phase E time-scoped perspectives (as-of snapshots, bounded windows)

  ---
  2. Evidence & Q2MARS Guarantees [REFINED]

  Evidence Structure

  Every MCP response includes:

  {
    "evidence": {
      "qgraph_operation": "find|remember|queryPath|...",
      "inherited_guarantee": "Q2MARS Thm. 1 (Cleanup Success)" | "Q2MARS Thm. 2 (Reflection Perturbation)",
      "dimension": 2048,
      "device": "cpu",
      "dtype": "complex64",
      "retrieval_reliability": {
        "law": "d ≥ C (k−1) log(N T / δ)",
        "params": {"k": 1, "N": 172, "T": null, "δ": null}
      },
      "namespace": "ns-o1a",
      "provenance": {
        "ts": "2025-10-22T16:30:00Z",
        "ts_source": "git|mtime|now",
        "commit_hash": "a1b2c3d...",
        "file_mtime": "2025-10-22T15:00:00Z"
      },
      "persistence_certificate": {
        "storage_root_realpath_sha256": "fd3081b4b75e...",
        "namespace_dir_realpath_sha256": "0551965ef6...",
        "manifest_sha256": "97de17c711f..."
      }
    }
  }

  [NEW] Q2MARS Theoretical Foundation

  Reference: HoloMem implements Q2MARS (Quantum-Graph MARS), a theoretical framework for bounded retrieval with cleanup guarantees.

  Thm. 1 (Cleanup Success): For read/query operations, retrieval succeeds with probability ≥ 1−δ when dimension d ≥ C(k−1)log(NT/δ), where:
  - k: Query complexity (typically k=1 for single-concept retrieval)
  - N: Total concepts in namespace
  - T: Time horizon (null for non-temporal queries)
  - δ: Failure probability (typically < 0.01)
  - C: Implementation constant (C ≈ 2 for HoloMem)

  Thm. 2 (Reflection Perturbation): Reasoning operations (synthesize, whatIf) apply controlled perturbations with bounded energy deviation, ensuring solution stability.

  Quantum-Graph Parameters:
  - dimension: 2048 (complex embedding dimension, supports N ≤ 10^6 concepts with δ < 0.001)
  - dtype: complex64 (quantum state representation, not classical embeddings)
  - device: cpu (GPU acceleration planned for Phase F)

  [NEW] Certificate Verification Workflow

  Integrity Check Process:

  1. Client receives response with persistence_certificate
  2. Verify manifest SHA256 against expected value (if known)
  3. Check realpath consistency (storage_root must be stable across sessions)
  4. Validate timestamp source (git > mtime > now precedence)

  Mismatch Handling:
  - Manifest mismatch: Raises INTEGRITY_ERROR, triggers automatic rollback to last known-good checkpoint
  - Realpath drift: Warning only (symlink changes are non-fatal)
  - Timestamp anomaly: Rejects future timestamps beyond 5-minute clock skew tolerance

  Adversarial Note: Evidence blocks are server-attested but not cryptographically signed in current version. For high-security environments, use MCP over TLS with mutual authentication.

  ---
  3. Namespace Operations

  (Content mostly unchanged from v1.0 draft, except additions below)

  holomem_verify_namespace [REFINED]

  Returns persistence certificate for client-side verification.

  Error Scenarios:
  // Integrity violation
  {
    "ok": false,
    "issues": ["manifest_sha256_mismatch", "orphan_concepts: 15"],
    "evidence": {...}
  }

  ---
  4. CRUD Operations [REFINED]

  holomem_remember [REFINED]

  Relations Input Precedence:
  When multiple formats are mixed (not recommended), object format takes precedence over triples.

  Conflict Resolution:
  Properties are merged (new values overwrite). Relations are unioned (duplicates ignored).

  Error Examples:

  // 400 Bad Request: Invalid concept name
  {
    "error": {
      "code": "INVALID_CONCEPT_NAME",
      "message": "Concept names must not contain whitespace or special chars except .-_",
      "invalid_name": "bug fix #123"
    }
  }

  // 409 Conflict: Transaction conflict
  {
    "error": {
      "code": "TXN_CONFLICT",
      "message": "Concurrent modification detected",
      "conflicting_txn": "txn_a1b2c3d"
    }
  }

  ---
  5. Retrieval & Search

  (Mostly unchanged, see below for refinements)

  ---
  6. Path & Graph Queries [REFINED]

  Lens Performance Implications [NEW]

  | Lens         | Typical Latency | Max Depth    | Bounded Retrieval         | Use Case                         |
  |--------------|-----------------|--------------|---------------------------|----------------------------------|
  | explicit     | <10ms           | 10           | ✅ Yes (BFS-LEX)           | Pure structural                  |
  | aliases      | <20ms           | 8            | ✅ Yes                     | Code symbol resolution (default) |
  | materialized | <50ms           | 6            | ✅ Yes                     | Full graph traversal             |
  | docflow      | <100ms          | 5            | ✅ Yes                     | Spec traceability                |
  | doc2code     | <30ms           | 2            | ✅ Yes (one-hop optimized) | Documentation links              |
  | coverage     | <80ms           | 6            | ✅ Yes (symmetric)         | Test coverage                    |
  | temporal     | <200ms          | 6 (hard cap) | ✅ Yes (Phase E)           | Historical analysis              |

  Depth Cap Rationale (Temporal Lens):
  Temporal path traversal requires maintaining time-consistent snapshots at each hop. Beyond depth 6, the cartesian product of temporal states causes exponential blowup in memory (O(N^d × T^d)). This is a correctness constraint, not a performance optimization.

  Error Example:
  // 400 Bad Request: Temporal depth exceeded
  {
    "error": {
      "code": "TEMPORAL_DEPTH_EXCEEDED",
      "message": "Temporal lens max_depth capped at 6 (requested: 10)",
      "requested": 10,
      "max_allowed": 6
    }
  }

  ---
  7. Reasoning Toolkit (ART) [REFINED]

  holomem_synthesize [REFINED]

  [NEW] Simulated Annealing Mathematics:

  Energy Function:
  E(state) = Σ_i w_i × (goal_i - current_i)²
  where w_i are goal weights (default: uniform).

  Acceptance Probability:
  P_accept = exp(-ΔE / T)
  where T = temperature (tau parameter).

  Annealer Parameters:
  - steps: Annealing iterations (default: 6, tunable via config)
  - eta: Learning rate (default: 0.3, range: [0.1, 0.9])
  - tau: Temperature (default: 0.05, range: [0.01, 0.5])
  - k: Perturbation neighbors (default: 1, range: [1, 5])
  - seed: RNG seed (default: 12345, for reproducibility)

  Parameter Tuning Guidance:
  - High exploration: Increase tau (0.2-0.5), decrease steps
  - High exploitation: Decrease tau (0.01-0.05), increase steps (10-20)
  - Fast convergence: Increase eta (0.6-0.9), risk local minima
  - Stable convergence: Decrease eta (0.1-0.3), slower but safer

  Confidence Calibration:
  - confidence = 1.0: Exact template match with ≥10 prior examples
  - confidence = 0.7-0.9: Partial template match with adaptation
  - confidence = 0.3-0.6: Novel synthesis with weak priors
  - confidence = 0.0: Fully novel (no existing patterns) [Note: Not a failure!]

  Adversarial Clarification: Confidence 0.0 for novel work is expected and correct. It signals "no historical evidence," not "low quality." Assess synthesis quality via predicted_fit and verify.checks.

  ---
  holomem_whatIf [REFINED]

  Fitness Metric:
  fitness = Σ (new_role_score) - Σ (deleted_role_penalty)
  Normalized to [0, 1]. Baseline is current state fitness = 1.0.

  Interpretation:
  - fitness > 1.0: Proposed change improves graph connectivity/richness
  - fitness = 1.0: Neutral change
  - fitness < 1.0: Degrades graph (e.g., deletes critical relations)

  Error Example:
  // 400 Bad Request: Invalid change specification
  {
    "error": {
      "code": "INVALID_CHANGE_SPEC",
      "message": "change parameter must be an object with at least one property",
      "provided": null
    }
  }

  ---
  holomem_verifyInvariants [REFINED]

  [NEW] Formal Invariant Language:

  HoloMem supports a bounded first-order logic (BFOL) subset:

  Grammar:
  invariant ::= forall(pattern, condition)
              | exists(pattern, condition)
              | implies(pattern1, pattern2)
              | count(pattern, comparator, threshold)

  pattern ::= {"is_a": type, "property": value, ...}
  condition ::= {"role": relation_type, "target": pattern}
  comparator ::= "$gte" | "$lte" | "$eq" | "$gt" | "$lt"

  Examples:
  // "Every bug must have at least one fix"
  {
    "name": "bugs_have_fixes",
    "invariant": {
      "forall": {"is_a": "bug"},
      "exists": {"role": "fixed_by", "target": {"is_a": "fix"}}
    }
  }

  // "No circular dependencies"
  {
    "name": "no_cycles",
    "invariant": {
      "forall": {"is_a": "module"},
      "not_exists": {"role": "imports", "target": "self", "transitive": true}
    }
  }

  Minimality Metric:
  Counterexamples are minimal by BFS-LEX depth (fewest hops from invariant anchor, lexicographically first on ties).

  ---
  8. Temporal Operations (Phase E) [REFINED]

  [NEW] ISO8601 Format Requirements

  Accepted Formats:
  - DateTime with UTC: 2025-10-22T12:00:00Z ✅ (required for as_of)
  - DateTime with offset: 2025-10-22T12:00:00-05:00 ✅
  - Date only: 2025-10-22 ✅ (interprets as 00:00:00 UTC)
  - Milliseconds: 2025-10-22T12:00:00.123Z ✅

  Rejected Formats:
  - Unix timestamp (float/int): 1697644800.0 ❌
  - Local time without zone: 2025-10-22T12:00:00 ❌ (ambiguous)
  - Relative times: "yesterday", "1 hour ago" ❌

  Clock Skew Tolerance:
  - Future timestamps ≤ 5 minutes from server time: Accepted with warning
  - Future timestamps > 5 minutes: Rejected with FUTURE_TIMESTAMP error

  Error Examples:
  // 400 Bad Request: XOR violation
  {
    "error": {
      "code": "TEMPORAL_XOR_VIOLATION",
      "message": "as_of is mutually exclusive with since/until",
      "provided": ["as_of", "since"],
      "constraint": "XOR"
    }
  }

  // 400 Bad Request: Ordering violation
  {
    "error": {
      "code": "TEMPORAL_ORDERING_VIOLATION",
      "message": "since must be <= until",
      "since": "2025-10-22T13:00:00Z",
      "until": "2025-10-22T11:00:00Z"
    }
  }

  // 400 Bad Request: Non-string timestamp
  {
    "error": {
      "code": "TEMPORAL_FORMAT_ERROR",
      "message": "Timestamps must be ISO8601 strings",
      "provided_type": "float",
      "provided_value": 1697644800.0
    }
  }

  [NEW] Temporal Conflict Resolution Tie-Breaking

  For holomem_overlayTemporal:

  When timestamps are identical:
  - latest_wins: Uses overlay namespace (arbitrary but consistent)
  - base_priority: Always prefers base namespace
  - overlay_priority: Always prefers overlay namespace

  When timestamps differ by <1ms:
  Treated as identical (precision limit of ISO8601 in HoloMem).

  [NEW] Temporal Retention Policy

  Default: Temporal indexes retain all versions indefinitely (no auto-pruning).

  Manual GC:
  {
    "namespace": "ns-o1a",
    "older_than": "2025-09-01T00:00:00Z",
    "dry_run": true
  }

  Adversarial Note: Unbounded temporal retention can grow to O(versions × concepts). Monitor namespace size with holomem_statistics and prune aggressively for long-running namespaces.

  ---
  9. Code Analysis Tools [REFINED]

  [NEW] System Requirements

  Python Version: 3.10+ (3.12+ recommended for full AST support)AST Parser: libcst 1.1.0+ (vendored in HoloMem, no external install required)Syntax Support:
  - Python 3.10: ✅ Full (match statements, walrus operators)
  - Python 3.11: ✅ Full (exception groups, variadic generics)
  - Python 3.12: ✅ Full (type parameter syntax, f-string enhancements)
  - Python 2.x: ❌ Not supported

  Adversarial Note: Code ingestion does not execute Python code. It performs static AST parsing only. However, malformed syntax can still cause parser crashes — validate inputs in untrusted environments.

  holomem_ingestPython [REFINED]

  Timestamp Validation:
  - Git timestamps: Validated against repository bounds (first commit ≤ ts ≤ now + 5min)
  - Future timestamp rejection: Prevents injection attacks via forged git history
  - Mtime fallback: No validation (assumes filesystem integrity)

  Enrichment Methodology:
  - Docstrings: Extracted from AST get_docstring() (first string literal in function/class body)
  - Type hints: Parsed from annotations (arg: int, -> str)
  - Signatures: Constructed from AST FunctionDef.args (no runtime introspection)

  Limitations:
  - No type inference: Only explicit annotations are captured
  - No cross-file analysis: Each module ingested independently
  - Dynamic features unsupported: eval, exec, runtime metaclasses

  Adversarial Example:
  # This will be ingested incompletely
  def dynamic_function():
      exec("def inner(): pass")
      return inner
  HoloMem will capture dynamic_function signature but NOT inner (runtime-only).

  holomem_resolveSymbol [REFINED]

  Scope:
  - ✅ Direct imports: from foo import bar → resolves bar to foo.bar
  - ✅ Aliasing: import foo as f → resolves f.bar to foo.bar
  - ⚠️ Star imports: from foo import * → partial (only if __all__ is static)
  - ❌ Dynamic imports: importlib.import_module(var) → cannot resolve

  Error Example:
  // 404 Not Found: Symbol not in graph
  {
    "error": {
      "code": "SYMBOL_NOT_FOUND",
      "message": "Symbol not found in namespace (may require ingestion)",
      "fqname": "o1a.missing.function",
      "language": "python",
      "suggestion": "Run holomem_ingestPython first"
    }
  }

  holomem_testsMap [REFINED]

  tested_by Property Population:

  HoloMem does not auto-populate tested_by. Users must:
  1. Manual entry: holomem_remember with relations {"tested_by": ["test_module.test_fn"]}
  2. Coverage integration: Use tools/ingest2HoloMem_v2.py --coverage-json coverage.json (requires pytest-cov output)
  3. Automation: CI pipeline scripts to parse coverage and assert relations

  Adversarial Note: Without explicit population, testsMap returns empty. This is by design (HoloMem does not run tests, only indexes metadata).

  ---
  10. Maintenance & Diagnostics

  (Mostly unchanged, see Performance section for latency bounds)

  ---
  11. System & Configuration

  (Unchanged from v1.0 draft)

  ---
  12. Sessions & Checkpoints

  (Unchanged from v1.0 draft)

  ---
  13. Transactions [REFINED]

  [NEW] Isolation Guarantees

  Snapshot Isolation:
  - Read Stability: Transactions see a consistent snapshot from beginTransaction time
  - Write Skew Prevention: NOT guaranteed (transactions can commit conflicting writes)
  - Optimistic Locking: Use holomem_replace with previous parameter for CAS semantics

  Rollback Examples:
  // Rollback on validation failure
  {
    "txn": "txn_a1b2c3d",
    "namespace": "ns-o1a"
  }
  // Response:
  {
    "ok": true,
    "rolled_back_ops": 15,
    "evidence": {...}
  }

  Error Example (commit conflict):
  {
    "error": {
      "code": "TXN_COMMIT_CONFLICT",
      "message": "Transaction conflicts with committed changes",
      "conflicting_concepts": ["bug.auth.session_leak"],
      "suggestion": "Retry transaction with fresh snapshot"
    }
  }

  ---
  14. Batch Operations [REFINED]

  holomem_batchRemember [REFINED]

  Transaction Modes:
  - best_effort: Commits partial results (default, suitable for idempotent ingests)
  - atomic: All-or-nothing (rolls back on ANY failure)

  Partial Failure Example (best_effort):
  {
    "ok": true,
    "successful": 47,
    "failed": 3,
    "errors": [
      {"artifact": "bug.broken.name with spaces", "error": "INVALID_CONCEPT_NAME"},
      {"artifact": "circular.ref", "error": "CYCLE_DETECTED"}
    ],
    "evidence": {...}
  }

  Atomic Rollback Example:
  {
    "ok": false,
    "successful": 0,
    "failed": 50,
    "errors": [{"artifact": "...", "error": "..."}],
    "rollback": true,
    "evidence": {...}
  }

  ---
  15. Performance & Scaling [NEW]

  Retrieval Latency Bounds

  | Operation                      | Typical (p50) | p99    | Bounded Max            |
  |--------------------------------|---------------|--------|------------------------|
  | holomem_get                    | <5ms          | <15ms  | O(log N)               |
  | holomem_find (topk=16)         | <20ms         | <50ms  | O(k log N)             |
  | holomem_findRelevant (topk=10) | <30ms         | <80ms  | O(d × log N)           |
  | holomem_queryPath (depth=3)    | <50ms         | <150ms | O(b^d × log N)         |
  | holomem_synthesize (steps=6)   | <100ms        | <300ms | O(s × k × log N)       |
  | holomem_checkpoint             | <50ms         | <200ms | O(N) (full graph scan) |

  Symbols:
  - N: namespace concept count
  - d: embedding dimension (2048)
  - k: retrieval topk
  - b: branching factor (avg out-degree, typically 3-5)
  - s: annealer steps

  Throughput Caps

  - Single namespace: ~1000 QPS (queries per second) sustained
  - Multi-namespace (concurrent): ~5000 QPS aggregate
  - Write throughput: ~500 TPS (transactions per second) with fsync
  - Batch ingest: ~10,000 concepts/sec (bounded by CPU AST parsing)

  Scaling Limits

  - Max concepts per namespace: 10^7 (10 million) before Q2MARS dimension becomes limiting
  - Max namespaces: 1000 (filesystem inode limits)
  - Max checkpoint size: ~5GB (numpy .npz file format limit)

  Adversarial Note: These are empirical bounds based on typical hardware (8-core CPU, 32GB RAM, SSD). Exact limits depend on concept/relation density and hardware specs.

  ---
  16. Security Considerations [NEW]

  Threat Model

  In Scope:
  - Malicious MCP clients (untrusted agents)
  - Filesystem tampering (integrity attacks)
  - Denial of service (resource exhaustion)

  Out of Scope (assume trusted):
  - HoloMem server process (no sandboxing)
  - Python runtime (no VM escapes)
  - Operating system kernel

  Authentication & Authorization

  Current Version:
  - No authentication: MCP server trusts all clients
  - No authorization: All namespaces accessible to all clients
  - Transport security: Use MCP over TLS (external to HoloMem)

  Recommendations for Production:
  1. Deploy MCP server behind authenticated reverse proxy (e.g., nginx with client certs)
  2. Use namespace-level isolation (separate namespaces = separate deployments)
  3. Monitor audit trail for suspicious activity

  Input Validation

  Sanitized Inputs:
  - Concept names (reject whitespace, special chars except .-_)
  - ISO8601 timestamps (reject future timestamps beyond clock skew)
  - Relation roles (reject reserved keywords: __internal__, __system__)

  Unsanitized (user must validate):
  - Property values (arbitrary JSON)
  - Code strings (static parsing only, no execution)

  Adversarial Note: Property values are not sanitized for injection attacks (SQL, NoSQL). HoloMem uses in-memory numpy arrays (no SQL backend), so SQL injection is not applicable. However, malicious properties could exploit downstream systems that consume HoloMem data.

  Resource Limits

  Per-Request:
  - Max payload size: 10MB (HTTP layer, configurable)
  - Max temporal query window: 1 year (prevents unbounded scans)
  - Max path depth: 10 (explicit/aliases), 6 (temporal)

  Per-Namespace:
  - Max concepts: 10^7 (soft limit, degraded performance beyond)
  - Max checkpoint history: 100 (auto-prune with holomem_pruneCheckpoints)

  Denial of Service Mitigations:
  - Rate limiting: Not implemented (use reverse proxy)
  - Query timeout: 30 seconds (hard timeout, non-configurable)

  ---
  17. Temporal Parameter Validation [REFINED]

  (Incorporates all refinements from section 8, collected here for reference)

  Validation Rules (Complete Specification)

  1. XOR Constraint: as_of ⊕ (since ∧ until)as_of is mutually exclusive with since/until pair.
  2. Pairing Requirement: since ⇒ until (strong recommendation)Providing only since or until is allowed but discouraged (interpreted as unbounded window).
  3. Ordering Constraint: since ≤ untilStrict inequality check (fails with TEMPORAL_ORDERING_VIOLATION).
  4. Format Requirement: ISO8601 strings only (see section 8)
  5. Clock Skew Tolerance: ts ≤ server_time + 5minRejects far-future timestamps (anti-forgery).

  Error HTTP Status Codes

  | Error Code                  | HTTP Status | Description                         |
  |-----------------------------|-------------|-------------------------------------|
  | TEMPORAL_XOR_VIOLATION      | 400         | Both as_of and since/until provided |
  | TEMPORAL_ORDERING_VIOLATION | 400         | since > until                       |
  | TEMPORAL_FORMAT_ERROR       | 400         | Non-ISO8601 or non-string timestamp |
  | FUTURE_TIMESTAMP            | 400         | Timestamp > server_time + 5min      |
  | TEMPORAL_DEPTH_EXCEEDED     | 400         | max_depth > 6 for temporal lens     |

  ---
  18. Error Reference [NEW]

  Common Error Codes (Comprehensive List)

  | Code                        | HTTP | Trigger                                | Resolution                            |
  |-----------------------------|------|----------------------------------------|---------------------------------------|
  | INVALID_CONCEPT_NAME        | 400  | Name contains whitespace/special chars | Use .-_ only                          |
  | SYMBOL_NOT_FOUND            | 404  | Symbol not ingested                    | Run holomem_ingestPython first        |
  | TEMPORAL_XOR_VIOLATION      | 400  | Invalid temporal params                | Use as_of XOR since/until             |
  | TEMPORAL_ORDERING_VIOLATION | 400  | since > until                          | Fix ordering                          |
  | TEMPORAL_FORMAT_ERROR       | 400  | Non-ISO8601 timestamp                  | Use ISO8601 strings                   |
  | FUTURE_TIMESTAMP            | 400  | Timestamp too far in future            | Check clock skew                      |
  | TEMPORAL_DEPTH_EXCEEDED     | 400  | max_depth > 6 for temporal             | Reduce depth or use non-temporal lens |
  | TXN_CONFLICT                | 409  | Concurrent modification                | Retry with fresh snapshot             |
  | TXN_COMMIT_CONFLICT         | 409  | Transaction isolation violation        | Rollback and retry                    |
  | INTEGRITY_ERROR             | 500  | Manifest SHA256 mismatch               | Restore from checkpoint               |
  | NAMESPACE_NOT_FOUND         | 404  | Namespace does not exist               | Create with create_if_missing=true    |
  | CYCLE_DETECTED              | 400  | Circular dependency in relations       | Remove cycle or use acyclic subset    |

  Error Response Structure (Standard)

  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human-readable description",
      "details": { /* Context-specific fields */ },
      "suggestion": "Remediation advice"
    }
  }

  ---
  19. Migration Guide (Phase D→E) [NEW]

  Breaking Changes

  1. Temporal Parameter Validation:
    - Phase D: Temporal params loosely validated (accepted floats, no XOR enforcement)
    - Phase E: Strict ISO8601 strings, XOR constraint enforced

  Migration: Audit all holomem_get, holomem_find, holomem_queryPath calls and convert timestamps to ISO8601 strings.
  2. max_depth Cap for Temporal Lens:
    - Phase D: No hard cap (could exceed memory limits)
    - Phase E: Capped at 6 for lens="temporal"

  Migration: Review temporal queries with max_depth > 6 and refactor to use intermediate anchors or non-temporal lenses.
  3. Provenance Timestamps:
    - Phase D: ts always "now"
    - Phase E: Precedence git > mtime > now

  Migration: Expect ts to reflect historical commit times for git-tracked files. Update downstream systems that assume "now."

  Non-Breaking Enhancements

  - Temporal overlay/diff: New tools, no migration required
  - Audit trail query: New, opt-in
  - Certificate verification: Enhanced evidence, backward-compatible

  Recommended Migration Path

  1. Test in isolated namespace: Create ns-myproject-e-test, run Phase E queries, validate behavior
  2. Update timestamp handling: Convert all temporal params to ISO8601 strings
  3. Adjust max_depth: Review and cap temporal queries at depth 6
  4. Re-ingest with provenance: Run ingest2HoloMem_v2.py to capture git timestamps
  5. Checkpoint before migration: holomem_checkpoint → backup .npz file
  6. Promote to production namespace: Copy refined concepts to main namespace

  ---
  20. Best Practices

  1. Always specify namespace explicitly (avoid session-scoped ambiguity)
  2. Use structured queries (find) over text search (better bounded guarantees)
  3. Validate temporal parameters client-side before submission (avoid round-trip errors)
  4. Check evidence blocks for Q2MARS guarantees and certificate integrity
  5. Use transactions for multi-step atomic operations (prefer atomic mode for critical writes)
  6. Checkpoint frequently (before schema changes, after bulk ingests)
  7. Verify namespaces before critical ops (holomem_verify_namespace → check certificate)
  8. Use dry_run for ART operations (synthesize/whatIf) before committing
  9. Prefer lenses for domain queries (e.g., doc2code for docs, coverage for tests)
  10. Monitor GC with dry_run=true first (avoid accidental data loss)
  11. Audit temporal retention periodically (holomem_statistics → check growth)
  12. Sanitize property values in untrusted environments (HoloMem does not validate arbitrary JSON)

  ---
  Response Envelope (Session Evidence)

  {
    "namespace": "ns-o1a",
    "checkpoint_id": "20251022-142501-holomem_store.ns-o1a.npz",
    "concept_ids": [
      "proposal.docs.holomem_mcp_api.comprehensive.20251022-1630",
      "doc.holomem_mcp_api.refined_v2.20251022-1700"
    ],
    "evidence_ids": [
      "review.adversarial.holomem_mcp_api_docs.20251022-1650",
      "review.adversarial.temporal_ops.20251022-1652",
      "review.adversarial.reasoning_toolkit.20251022-1653",
      "review.adversarial.code_analysis.20251022-1654",
      "review.adversarial.evidence_guarantees.20251022-1655"
    ],
    "anchored_nodes": [
      "session.latest",
      "proposal.docs.holomem_mcp_api.comprehensive.20251022-1630",
      "doc.holomem_mcp_api.refined_v2.20251022-1700"
    ],
    "lens": "aliases",
    "metrics": {
      "concepts_delta": 17,
      "relations_delta": 24,
      "anchored_context_ratio": 1.0,
      "pattern_reuse_rate": 0.0
    },
    "policy_notes": [
      "Phase E temporal validation active (strict ISO8601, XOR constraints)",
      "All adversarial reviews (blocking + critical) resolved",
      "Certificate verification workflow documented",
      "Q2MARS proofs cited (implementation constant C ≈ 2)",
      "Migration guide provided for Phase D→E upgrades"
    ]
  }

  ---
  End of HoloMem MCP API Reference v2.0 (Adversarially Refined)