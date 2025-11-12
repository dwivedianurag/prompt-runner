from __future__ import annotations

import sys
import os
import json
from typing import Any, Dict, Optional, Type
from urllib import request as http
from loader import (
    list_resources as hm_list_resources,
    read_resource as hm_read_resource,
    batch_read as hm_batch_read,
    list_overlays as hm_list_overlays,
)

from models import (
    FindParams,
    GetParams,
    FindRelevantParams,
    SynthesizeParams,
    WhatIfParams,
    RememberParams,
    ReplaceParams,
    ForgetParams,
    BatchRememberParams,
    BatchReplaceParams,
    BatchIngestParams,
    ProjectBundleParams,
    IngestPythonParams,
    TransactionParams,
    CommitParams,
    RollbackParams,
    RebuildParams,
    VerifyParams,
    QueryPathParams,
    AggregateParams,
    LinkSymbolsParams,
    ResolveSymbolParams,
    ConfigureParams,
    GCParams,
    CheckpointParams,
    StatisticsParams,
    ProfileParams,
    DescribeParams,
    DiagnoseParams,
    # DP‑Coding operators
    SessionRecordParams,
    SummarizeAnchoredParams,
    SliceContextParams,
    VerifyInvariantsParams,
    CounterexampleParams,
    HypothesizeParams,
    ConfirmHypothesisParams,
    ForgetHypothesisParams,
    ContrastParams,
    PlanParams,
    DiffImpactParams,
    TestsMapParams,
    SliceProgramParams,
    CostEstimateParams,
    AdviseRetrievalParams,
    RoleBudgetParams,
    UseNamespaceParams,
    NamespaceOnlyParams,
    ListNamespacesParams,
    DescribeNamespaceParams,
    CopyMoveNamespaceParams,
    DiffNamespacesParams,
    CrossNamespaceSearchParams,
    WithNamespaceParams,
    QuickStartParams,
    SearchParams,
    FindByParams,
    CodeSliceParams,
    ContextGraphParams,
    PathBetweenParams,
    ListClassesParams,
    ListEnumsParams,
    ListMethodsParams,
    ListCallsParams,
    GetSignatureParams,
    GetDocstringParams,
    GetImplementationParams,
    BatchGetParams,
    PruneCheckpointsParams,
)

MCP_PROTOCOL_VERSION = "2025-06-18"
DEFAULT_ENDPOINT = "http://127.0.0.1:8085/mcp"
HOLOMEM_VERSION = "2025-06-18"

# Framing: default to MCP stdio headers; legacy newline only when explicitly enabled
_FRAMING_MODE: Optional[str] = None  # 'headers' or 'newline'
_FRAMING_ENV = os.getenv("HOLOMEM_MCP_FRAMING", "").strip().lower()
_ALLOW_NEWLINE = _FRAMING_ENV == "newline"

def log_debug(message: str) -> None:
    """Lightweight, opt-in debug logging to stderr (HOLOMEM_MCP_DEBUG=1)."""
    if os.getenv("HOLOMEM_MCP_DEBUG", "").strip() not in ("1", "true", "TRUE", "yes", "on"):
        return
    try:
        msg = str(message)
        if len(msg) > 1024:
            msg = msg[:1024] + "...(truncated)"
        sys.stderr.write(f"[holomem-mcp] {msg}\n")
        sys.stderr.flush()
    except Exception:
        pass

def _jsonrpc(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}

def _http_post_json(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = http.Request(url, data=data, headers={"Content-Type": "application/json"})
    with http.urlopen(req) as resp:  # nosec - local loopback endpoint
        raw = resp.read().decode("utf-8")
        return json.loads(raw)

# Canonical MCP tool name → server JSON-RPC method
NAME_TO_SERVER: Dict[str, str] = {
    # Namespace management
    "holomem_switch_to_namespace": "holomem.useNamespace",
    "holomem_get_current_namespace": "holomem.getCurrentNamespace",
    "holomem_list_namespaces": "holomem.listNamespaces",
    "holomem_describe_namespace": "holomem.describeNamespace",
    "holomem_create_namespace": "holomem.createNamespace",
    "holomem_delete_namespace": "holomem.deleteNamespace",
    "holomem_promote_namespace": "holomem.promoteNamespace",
    "holomem_verify_namespace": "holomem.verifyNamespace",
    "holomem_prune_checkpoints": "holomem.pruneCheckpoints",
    "holomem_copy_to_namespace": "holomem.copyToNamespace",
    "holomem_move_to_namespace": "holomem.moveToNamespace",
    "holomem_diff_namespaces": "holomem.diffNamespaces",
    "holomem_search_across_namespaces": "holomem.crossNamespaceSearch",
    "holomem_execute_in_namespace": "holomem.withNamespace",
    # Discovery & search
    "holomem_get_quickstart_overview": "holomem.quickStart",
    "holomem_search_by_text": "holomem.search",
    "holomem_find_by_properties": "holomem.findBy",
    "holomem_find_by_query": "holomem.find",
    "holomem_find_similar_concepts": "holomem.findRelevant",
    # Ingestion
    "holomem_ingest_python_code": "holomem.ingestPython",
    "holomem_ingest_bundle": "holomem.projectBundle",
    "holomem_ingest_many_artifacts": "holomem.batchIngest",
    # Core CRUD & retrieval
    "holomem_store_concept": "holomem.remember",
    "holomem_replace_concept": "holomem.replace",
    "holomem_remove_concept": "holomem.forget",
    "holomem_get_concept": "holomem.get",
    "holomem_store_many_concepts": "holomem.batchRemember",
    "holomem_replace_many_concepts": "holomem.batchReplace",
    "holomem_describe_capabilities": "holomem.describe",
    # Exploration & graph traversal
    "holomem_get_program_slice": "holomem.sliceProgram",
    "holomem_expand_neighborhood": "holomem.sliceContext",
    "holomem_find_paths": "holomem.queryPath",
    "holomem_get_code_slice": "holomem.codeSlice",
    "holomem_get_neighborhood": "holomem.contextGraph",
    "holomem_shortest_paths_between": "holomem.pathBetween",
    "holomem_list_classes": "holomem.listClasses",
    "holomem_list_enums": "holomem.listEnums",
    "holomem_get_class_methods": "holomem.listMethods",
    "holomem_get_function_calls": "holomem.listCalls",
    "holomem_get_function_callers": "holomem.listCallers",
    # Implementation & metadata
    "holomem_get_signature": "holomem.getSignature",
    "holomem_get_docstring": "holomem.getDocstring",
    "holomem_get_implementation_anchors": "holomem.getImplementation",
    "holomem_get_many_symbols": "holomem.batchGet",
    # Testing & constraints
    "holomem_get_tests_map": "holomem.testsMap",
    "holomem_validate_invariants": "holomem.verifyInvariants",
    "holomem_find_counterexample": "holomem.counterexample",
    # Reasoning, planning & analysis
    "holomem_synthesize_concept": "holomem.synthesize",
    "holomem_create_plan": "holomem.plan",
    "holomem_create_hypothesis": "holomem.hypothesize",
    "holomem_confirm_hypothesis": "holomem.confirmHypothesis",
    "holomem_remove_hypothesis": "holomem.forgetHypothesis",
    "holomem_compare_concepts": "holomem.contrast",
    "holomem_summarize_anchored": "holomem.summarizeAnchored",
    "holomem_aggregate_metrics": "holomem.aggregate",
    "holomem_advise_retrieval": "holomem.adviseRetrieval",
    "holomem_estimate_cost": "holomem.costEstimate",
    "holomem_explore_counterfactual": "holomem.whatIf",
    # Identity & symbols
    "holomem_link_symbols": "holomem.linkSymbols",
    "holomem_resolve_symbol": "holomem.resolveSymbol",
    # Versioning & transactions
    "holomem_create_checkpoint": "holomem.checkpoint",
    "holomem_diff_impact": "holomem.diffImpact",
    "holomem_validate_graph": "holomem.validateGraph",
    "holomem_restore_checkpoint": "holomem.restore_checkpoint",
    "holomem_begin_transaction": "holomem.beginTransaction",
    "holomem_commit_transaction": "holomem.commit",
    "holomem_rollback_transaction": "holomem.rollback",
    # Maintenance & admin
    "holomem_rebuild_indexes": "holomem.rebuild",
    "holomem_verify_indexes": "holomem.verify",
    "holomem_diagnose_system": "holomem.diagnose",
    "holomem_get_system_stats": "holomem.statistics",
    "holomem_collect_garbage": "holomem.gc",
    "holomem_profile_system": "holomem.profile",
    "holomem_get_config": "holomem.getConfig",
    "holomem_update_config": "holomem.configure",
    "holomem_get_role_budget": "holomem.roleBudget",
    "holomem_record_session": "holomem.sessionRecord",
    # Helper / utility (bridge-local) + standard helpers
    "holomem_get_versions": "holomem.version",
    "holomem_get_capabilities": "holomem.capabilities",
    "resources_batch_read": "resources.batch_read",
    "overlays_list": "overlays.list",
}

# Backward‑compatibility aliases for legacy MCP underscore names used by some tests/clients.
# These map older names (camelCase parts preserved) to the same server dotted methods.
# Kept minimal and data-only to avoid altering core logic.
NAME_TO_SERVER.update(
    {
        # Core/CRUD (legacy)
        "holomem_find": "holomem.find",
        "holomem_get": "holomem.get",
        "holomem_findRelevant": "holomem.findRelevant",
        "holomem_synthesize": "holomem.synthesize",
        "holomem_whatIf": "holomem.whatIf",
        "holomem_remember": "holomem.remember",
        "holomem_replace": "holomem.replace",
        "holomem_forget": "holomem.forget",
        "holomem_batchRemember": "holomem.batchRemember",
        "holomem_batchReplace": "holomem.batchReplace",
        "holomem_batchIngest": "holomem.batchIngest",
        # Transactions (legacy)
        "holomem_beginTransaction": "holomem.beginTransaction",
        "holomem_commit": "holomem.commit",
        "holomem_rollback": "holomem.rollback",
        # Maintenance & config (legacy)
        "holomem_rebuild": "holomem.rebuild",
        "holomem_verify": "holomem.verify",
        "holomem_queryPath": "holomem.queryPath",
        "holomem_aggregate": "holomem.aggregate",
        "holomem_linkSymbols": "holomem.linkSymbols",
        "holomem_resolveSymbol": "holomem.resolveSymbol",
        "holomem_describe": "holomem.describe",
        "holomem_configure": "holomem.configure",
        "holomem_getConfig": "holomem.getConfig",
        "holomem_gc": "holomem.gc",
        "holomem_checkpoint": "holomem.checkpoint",
        "holomem_restore_checkpoint": "holomem.restore_checkpoint",
        "holomem_diagnose": "holomem.diagnose",
        "holomem_statistics": "holomem.statistics",
        "holomem_profile": "holomem.profile",
        # Namespaces (legacy)
        "holomem_useNamespace": "holomem.useNamespace",
        "holomem_getCurrentNamespace": "holomem.getCurrentNamespace",
        "holomem_listNamespaces": "holomem.listNamespaces",
        "holomem_describeNamespace": "holomem.describeNamespace",
        "holomem_createNamespace": "holomem.createNamespace",
        "holomem_deleteNamespace": "holomem.deleteNamespace",
        "holomem_promoteNamespace": "holomem.promoteNamespace",
        "holomem_verifyNamespace": "holomem.verifyNamespace",
        "holomem_copyToNamespace": "holomem.copyToNamespace",
        "holomem_moveToNamespace": "holomem.moveToNamespace",
        "holomem_diffNamespaces": "holomem.diffNamespaces",
        "holomem_crossNamespaceSearch": "holomem.crossNamespaceSearch",
        # Ingestion (legacy)
        "holomem_ingestPython": "holomem.ingestPython",
        # DP‑Coding (legacy)
        "holomem_sessionRecord": "holomem.sessionRecord",
        "holomem_summarizeAnchored": "holomem.summarizeAnchored",
        "holomem_verifyInvariants": "holomem.verifyInvariants",
        "holomem_counterexample": "holomem.counterexample",
        "holomem_hypothesize": "holomem.hypothesize",
        "holomem_confirmHypothesis": "holomem.confirmHypothesis",
        "holomem_forgetHypothesis": "holomem.forgetHypothesis",
        "holomem_contrast": "holomem.contrast",
        "holomem_plan": "holomem.plan",
        "holomem_diffImpact": "holomem.diffImpact",
        "holomem_testsMap": "holomem.testsMap",
        # Advisory cost estimate (legacy)
        "holomem_costEstimate": "holomem.costEstimate",
        # Retrieval advice (legacy)
        "holomem_adviseRetrieval": "holomem.adviseRetrieval",
    }
)

def _to_server_method(tool_name: str) -> str:
    """Map MCP tool name to server JSON-RPC method (canonical names only)."""
    return NAME_TO_SERVER.get(tool_name, tool_name)

def call_holomem(method: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    method = _to_server_method(method)
    endpoint = os.getenv("HOLOMEM_HTTP_ENDPOINT", DEFAULT_ENDPOINT)
    resp = _http_post_json(endpoint, _jsonrpc(method, arguments))
    if isinstance(resp, list):
        resp = resp[0]
    if "error" in resp and resp["error"] is not None:
        raise RuntimeError(f"HoloMem error: {resp['error']}")
    return resp.get("result", {})

def _schema_of(model: Type) -> Dict[str, Any]:
    try:
        return model.model_json_schema()  # type: ignore[attr-defined]
    except Exception:
        return {"type": "object"}

def _sanitize_schema_for_mcp(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Relax Pydantic JSON Schema to be MCP‑UI friendly.

    Some clients hide tools when they encounter properties without explicit types
    (e.g., Pydantic Any). We ensure every property has a basic "type" unless it
    uses $ref/anyOf/oneOf/allOf. We default to type "object" for safety.
    """
    try:
        s = dict(schema or {})
        if not isinstance(s, dict):
            return {"type": "object"}
        # Top-level type
        if "$ref" not in s and "type" not in s:
            s["type"] = "object"
        props = s.get("properties")
        if isinstance(props, dict):
            for k, v in list(props.items()):
                if not isinstance(v, dict):
                    props[k] = {"type": "object"}
                    continue
                if any(key in v for key in ("$ref", "anyOf", "oneOf", "allOf")):
                    continue
                if "type" not in v:
                    v["type"] = "object"
        return s
    except Exception:
        return {"type": "object"}

# -- Argument normalization helpers -------------------------------------------------

def _maybe_parse_json_obj(v: Any) -> Any:
    """If v is a JSON-encoded object string, parse and return the dict; else v.

    This helps MCP clients that stringify nested object fields (e.g., has/is_a)
    before sending tools/call. We only coerce when the parsed value is a dict.
    """
    if isinstance(v, str):
        try:
            obj = json.loads(v)
            if isinstance(obj, dict):
                return obj
        except Exception:
            return v
    return v

# --- Framing (Headers by default; legacy newline when enabled) ---

def _send_headers(body: bytes) -> None:
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    sys.stdout.buffer.write(header)
    sys.stdout.buffer.write(body)
    sys.stdout.flush()

def send_message(message: Dict[str, Any]) -> None:
    """Send a JSON-RPC message. Headers by default; newline only when env enables it."""
    json_str = json.dumps(message, separators=(",", ":"), ensure_ascii=False)
    mode = _FRAMING_MODE or ("newline" if _ALLOW_NEWLINE else "headers")
    try:
        if mode == "headers":
            _send_headers(json_str.encode("utf-8"))
        else:
            sys.stdout.buffer.write((json_str + "\n").encode("utf-8"))
            sys.stdout.flush()
    except BrokenPipeError:
        sys.exit(0)
    log_debug(f"Sent: {json_str}")

def _read_headers_and_body(first_line: str) -> Optional[Dict[str, Any]]:
    """Read Content-Length framed message (supports extra headers in any order)."""
    global _FRAMING_MODE
    _FRAMING_MODE = "headers"
    headers: Dict[str, str] = {}
    line = first_line
    # Collect headers until blank line
    while line is not None:
        if not line or line in ("\r\n", "\n", "\r", ""):
            break
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
        raw = sys.stdin.buffer.readline()
        if not raw:
            return None
        line = raw.decode("latin-1")
    clen = headers.get("content-length")
    if not clen:
        log_debug("Missing Content-Length header")
        return None
    try:
        length = int(clen)
    except Exception:
        log_debug(f"Invalid Content-Length: {clen}")
        return None
    # Read exactly N bytes
    buf = bytearray()
    while len(buf) < length:
        chunk = sys.stdin.buffer.read(length - len(buf))
        if not chunk:
            return None
        buf.extend(chunk)
    payload = bytes(buf).decode("utf-8")
    msg = json.loads(payload)
    log_debug(f"Received: {payload}")
    return msg

def read_message() -> Optional[Dict[str, Any]]:
    """Read a JSON-RPC message (headers by default; newline legacy when enabled)."""
    global _FRAMING_MODE
    try:
        # Legacy test mode: newline-delimited JSON
        if _ALLOW_NEWLINE:
            line = sys.stdin.readline()
            if not line:
                log_debug("EOF reached")
                return None
            payload = line.rstrip("\r\n")
            if not payload:
                return read_message()
            _FRAMING_MODE = _FRAMING_MODE or "newline"
            msg = json.loads(payload)
            log_debug(f"Received: {payload}")
            return msg
        # Headers default: peek first line and classify
        raw = sys.stdin.buffer.readline()
        if not raw:
            log_debug("EOF reached")
            return None
        line = raw.decode("latin-1")
        head = line.lstrip()
        # If JSON arrives unexpectedly, accept newline to avoid stalling
        if head.startswith("{") or head.startswith("["):
            payload = head.rstrip("\r\n")
            _FRAMING_MODE = _FRAMING_MODE or "newline"
            msg = json.loads(payload)
            log_debug(f"Received: {payload}")
            return msg
        # Header framing if line looks like a header (k:v) and not JSON
        if head.lower().startswith("content-length:") or (":" in head and not (head.startswith("{") or head.startswith("["))):
            return _read_headers_and_body(line)
        # Unknown or empty line: ignore safely
        if not head.strip():
            return read_message()
        return None
    except json.JSONDecodeError as e:
        log_debug(f"JSON decode error: {e}")
        return None
    except BrokenPipeError:
        return None
    except Exception as e:
        log_debug(f"Error reading message: {e}")
        return None

def build_tools_catalog() -> list[Dict[str, Any]]:
    """
    Builds the final catalog of all tools, using inline schemas instead of $ref
    and ensuring a valid fallback for empty schemas.
    """
    # Inline DP‑Coding schemas (no $refs) so MCP clients can discover params
    dp_inline_schemas: Dict[str, Dict[str, Any]] = {
        "holomem.sliceProgram": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "holomem://schemas/dp-coding/sliceProgram.schema.json",
            "title": "sliceProgram",
            "type": "object",
            "properties": {
                "symbol": { "type": "string" },
                "lens": { "type": "string" },
                "bounds": { "type": "object" }
            },
            "required": ["symbol"]
        },
        "holomem.verifyInvariants": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "holomem://schemas/dp-coding/verifyInvariants.schema.json",
            "title": "verifyInvariants",
            "type": "object",
            "properties": {
                "rules": { "type": "array", "items": { "type": "object" } },
                "lens": { "type": "string" }
            },
            "required": ["rules"]
        },
        "holomem.contrast": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "holomem://schemas/dp-coding/contrast.schema.json",
            "title": "contrast",
            "type": "object",
            "properties": {
                "probe": {},
                "candidates": { "type": "array", "items": { "type": "string" } },
                "lens": { "type": "string" },
                "score_mode": { "type": "string" }
            },
            "required": ["probe", "candidates"]
        },
        "holomem.testsMap": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "holomem://schemas/dp-coding/testsMap.schema.json",
            "title": "testsMap",
            "type": "object",
            "properties": {
                "node": { "type": "string" },
                "coverage_uri": { "type": "string" }
            },
            "required": ["node"]
        },
        "holomem.summarizeAnchored": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "holomem://schemas/dp-coding/summarizeAnchored.schema.json",
            "title": "summarizeAnchored",
            "type": "object",
            "properties": {
                "nodes": { "type": "array", "items": { "type": "string" } },
                "lens": { "type": "string" },
                "max_tokens": { "type": "integer" }
            },
            "required": ["nodes"]
        },
        "holomem.sliceContext": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "holomem://schemas/dp-coding/sliceContext.schema.json",
            "title": "sliceContext",
            "type": "object",
            "properties": {
                "from": { "type": "array", "items": { "type": "string" } },
                "goal": { "type": "object" },
                "max_nodes": { "type": "integer" },
                "page_size": { "type": "integer" },
                "page_token": { "type": "string" },
                "lens": { "type": "string" }
            },
            "required": ["from"]
        },
    }

    # Coding‑first catalog ordering and task‑oriented descriptions (inline schemas; no $refs)
    entries: list[tuple[str, str, Type | None]] = [
        # == Namespaces ==
        ("holomem.useNamespace", "Switch to a namespace for isolation (session-scoped).", UseNamespaceParams),
        ("holomem.getCurrentNamespace", "Return the current namespace.", None),
        ("holomem.listNamespaces", "List available namespaces persisted on disk.", None),
        ("holomem.describeNamespace", "Summarize a namespace (counts).", DescribeNamespaceParams),
        ("holomem.createNamespace", "Create (initialize) a namespace.", NamespaceOnlyParams),
        ("holomem.deleteNamespace", "Delete namespace graph + sidecars.", NamespaceOnlyParams),
        ("holomem.promoteNamespace", "Promote from default to a named namespace (enable persistence).", NamespaceOnlyParams),
        ("holomem.verifyNamespace", "Verify manifest/digest integrity for a namespace.", NamespaceOnlyParams),
        ("holomem.pruneCheckpoints", "Keep the last N checkpoints (lexicographic, latest first).", PruneCheckpointsParams),
        ("holomem.copyToNamespace", "Copy concepts from one namespace to another.", CopyMoveNamespaceParams),
        ("holomem.moveToNamespace", "Move concepts from one namespace to another.", CopyMoveNamespaceParams),
        ("holomem.diffNamespaces", "Compare two namespaces (added/removed/changed).", DiffNamespacesParams),
        ("holomem.crossNamespaceSearch", "Search across multiple namespaces (NL).", CrossNamespaceSearchParams),
        ("holomem.withNamespace", "Execute a nested tools/call inside a namespace view.", WithNamespaceParams),

        # == Discovery & Search (wrappers) ==
        ("holomem.quickStart", "Quick overview of a namespace (summary + entry points).", QuickStartParams),
        ("holomem.search", "Natural-language search across names + metadata (bounded).", SearchParams),
        ("holomem.findBy", "Structured find with minimal inputs (has/is_a).", FindByParams),
        # == Ingestion ==
        ("holomem.ingestPython", "Parse a Python module into code concepts and explicit calls (per‑file, idempotent).", IngestPythonParams),
        ("holomem.projectBundle", "Deterministically ingest a pre‑parsed bundle (ConceptDTOs + triples) for brownfield DTOs.", ProjectBundleParams),
        ("holomem.batchIngest", "Batch ingest artifacts with on_error policy; for simple property ingests (not parsing code).", BatchIngestParams),

        # == Core CRUD & Retrieval ==
        ("holomem.remember", "Assert/merge properties for a concept (idempotent).", RememberParams),
        ("holomem.replace", "Atomic replace of properties (set to exactly), with validation.", ReplaceParams),
        ("holomem.forget", "Remove a property or relation (policy‑aware neutralization).", ForgetParams),
        ("holomem.get", "Get full details for a concept (properties + asserted relations).", GetParams),
        ("holomem.find", "Structured find by has/is_a with topk/pagination.", FindParams),
        ("holomem.findRelevant", "Semantic search by probe or concept name.", FindRelevantParams),
        ("holomem.describe", "Describe roles, relations, policies, and capabilities.", DescribeParams),
        ("holomem.batchRemember", "Batch assertion of properties/relations (transactional modes).", BatchRememberParams),
        ("holomem.batchReplace", "Batch replace properties across items (transactional modes).", BatchReplaceParams),

        # == Exploration & Graph Traversal ==
        ("holomem.sliceProgram", "Structural slice around a symbol (symbol=module[.Class][.method]); include certificates.", None),
        ("holomem.sliceContext", "Deterministic BFS‑LEX neighborhood from nodes; defaults lens=aliases; supports pagination.", None),
        ("holomem.queryPath", "Simple paths with cycle pruning, edge_filter, explain diagnostics, and certificates; defaults lens=aliases.", QueryPathParams),
        # == Exploration (wrappers over DP) ==
        ("holomem.codeSlice", "Focused structural slice for a symbol (bounded).", CodeSliceParams),
        ("holomem.contextGraph", "Neighborhood graph around a node (bounded BFS-LEX).", ContextGraphParams),
        ("holomem.pathBetween", "Bounded shortest paths (namespaced union/first_hit).", PathBetweenParams),
        ("holomem.listClasses", "List classes under an optional module prefix.", ListClassesParams),
        ("holomem.listEnums", "List enums under an optional module prefix.", ListEnumsParams),
        ("holomem.listMethods", "List methods for a class.", ListMethodsParams),
        ("holomem.listCalls", "List direct callees for a symbol.", ListCallsParams),

        # == Implementation & Metadata ==
        ("holomem.getSignature", "Return signature metadata for a symbol (bounded).", GetSignatureParams),
        ("holomem.getDocstring", "Return docstring summary/full (bounded).", GetDocstringParams),
        ("holomem.getImplementation", "Return implementation anchors; optional excerpt (bounded).", GetImplementationParams),
        ("holomem.batchGet", "Batch compact summaries for symbols (paginated).", BatchGetParams),

        # == Testing & Constraints ==
        ("holomem.testsMap", "Map a code node to tests (reads tested_by property/relation); optional coverage provenance.", None),
        ("holomem.verifyInvariants", "Verify bounded invariants; return minimal counterexamples.", None),
        ("holomem.counterexample", "Find a minimal counterexample for a single invariant.", CounterexampleParams),

        # == Reasoning, Planning & Analysis ==
        ("holomem.synthesize", "Steer a concept toward a goal state (advisory, evidence‑first).", SynthesizeParams),
        ("holomem.plan", "Materialize a plan as nodes with depends_on edges from high‑level steps.", PlanParams),
        ("holomem.hypothesize", "Add hypothesis claims (not materialized).", HypothesizeParams),
        ("holomem.confirmHypothesis", "Confirm (materialize) hypothesis claims.", ConfirmHypothesisParams),
        ("holomem.forgetHypothesis", "Forget hypothesis claims.", ForgetHypothesisParams),
        ("holomem.contrast", "Explain ranking via feature deltas (probe vs candidates); supports lens.", None),
        ("holomem.summarizeAnchored", "Summarize anchored nodes; supports lens and token bounds.", None),
        ("holomem.aggregate", "Aggregate simple metrics (e.g., COUNT) over cohorts.", AggregateParams),
        ("holomem.adviseRetrieval", "Recommend exact vs ANN+candidates based on N (dataset size).", AdviseRetrievalParams),
        ("holomem.costEstimate", "Advisory cost estimate for an operation’s payload size.", CostEstimateParams),
        ("holomem.whatIf", "Create a counterfactual concept and analyze impacts (what‑if).", WhatIfParams),

        # == Identity & Symbol Resolution ==
        ("holomem.linkSymbols", "Link language symbols to a canonical concept.", LinkSymbolsParams),
        ("holomem.resolveSymbol", "Resolve a language symbol (e.g., python fqname) to canonical identity.", ResolveSymbolParams),

        # == Versioning & Impact ==
        ("holomem.checkpoint", "Create a snapshot of the current graph (id + evidence).", VerifyParams),
        ("holomem.diffImpact", "Compute change impact between snapshots (added/removed edges, impacted nodes).", DiffImpactParams),
        ("holomem.restore_checkpoint", "Restore a previously saved checkpoint (destructive).", CheckpointParams),

        # == Transactions ==
        ("holomem.beginTransaction", "Begin a transaction (snapshot isolation).", TransactionParams),
        ("holomem.commit", "Commit a transaction; return index versions.", CommitParams),
        ("holomem.rollback", "Rollback a transaction.", RollbackParams),

        # == Maintenance & Admin ==
        ("holomem.rebuild", "Rebuild reverse index versions for roles (accepts roles list).", RebuildParams),
        ("holomem.verify", "Verify index consistency; return versions and issues.", VerifyParams),
        ("holomem.diagnose", "Scan system and indexes for potential issues (advisory).", DiagnoseParams),
        ("holomem.statistics", "Graph/performance/health statistics.", StatisticsParams),
        ("holomem.gc", "Garbage collection: pattern‑based candidates; support dry_run.", GCParams),
        ("holomem.profile", "Capture profiling/tracing signals (bounded duration).", ProfileParams),
        ("holomem.getConfig", "Return current configuration.", VerifyParams),
        ("holomem.configure", "Update server configuration (some options require restart).", ConfigureParams),
        ("holomem.roleBudget", "Report strict_N for a role; warn near caps.", RoleBudgetParams),
        ("holomem.sessionRecord", "Record an auditable session payload (ledger id).", SessionRecordParams),
    ]

    # Fast lookup for server method → (description, model)
    entry_index: Dict[str, tuple[str, Type | None]] = {sm: (desc, model) for (sm, desc, model) in entries}

    # Helper/utility schemas by server method
    helper_schemas: Dict[str, Dict[str, Any]] = {
        "holomem.version": {"type": "object", "properties": {}},
        "holomem.capabilities": {"type": "object", "properties": {}},
        "resources.batch_read": {"type": "object", "properties": {"uris": {"type": "array", "items": {"type": "string"}}}},
        "overlays.list": {"type": "object", "properties": {}},
    }

    tools: list[Dict[str, Any]] = []

    # Emit canonical tools only (underscore names), sourcing schemas/descriptions from server methods
    for tool_name, server_method in NAME_TO_SERVER.items():
        schema: Dict[str, Any] = {}
        examples: list[Dict[str, Any]] = []
        if server_method in dp_inline_schemas:
            schema = dp_inline_schemas[server_method]
        elif server_method in helper_schemas:
            schema = helper_schemas[server_method]
        else:
            desc_model = entry_index.get(server_method)
            if desc_model and desc_model[1] is not None:
                schema = _schema_of(desc_model[1])  # type: ignore[index]
        # Extend remember schema to accept optional 'relations'
        if server_method == "holomem.remember":
            try:
                props = schema.setdefault("properties", {}) if isinstance(schema, dict) else {}
                # oneOf: object map role->array[string] | array of triples | array of dicts {type,target}
                rel_schema = {
                    "oneOf": [
                        {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}},
                        {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "minItems": 3,
                                "maxItems": 3,
                                "prefixItems": [
                                    {"type": ["string", "null"]},
                                    {"type": "string"},
                                    {"type": "string"}
                                ],
                                "items": False
                            }
                        },
                        {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "role": {"type": "string"},
                                    "target": {"type": "string"},
                                    "dst": {"type": "string"}
                                },
                                "additionalProperties": True
                            }
                        },
                    ]
                }
                props["relations"] = rel_schema
            except Exception:
                pass
        schema = _sanitize_schema_for_mcp(schema or {})
        if not schema:
            schema = {"type": "object"}

        # Minimal examples for a few key tools
        if server_method == "holomem.useNamespace":
            examples = [{"name": "example", "arguments": {"name": "projA"}}]
        if server_method == "holomem.pathBetween":
            examples = [{"name": "example", "arguments": {"from": ["A"], "to": ["B"], "max_depth": 3, "namespaces": ["main","dev"], "policy": "union"}}]
        if server_method == "holomem.queryPath":
            examples = [
                {"name": "manual", "arguments": {"from": ["pkg.mod.Caller.fn"], "to": ["pkg2.auth.Service.login"], "lens": "aliases", "max_depth": 6}},
                {"name": "auto_intent", "arguments": {"from": ["pkg.tasks.TaskManager"], "to": ["pkg.auth.AuthService"], "lens": "aliases", "mode": "auto", "max_depth": 6}},
            ]
        if server_method == "holomem.aggregate":
            examples = [
                {"name": "flat_group_by", "arguments": {"group_by": {"kind": "fn"}, "metrics": {"cnt_total": {"op": "COUNT_TOTAL"}}}},
                {"name": "canonical_group_by", "arguments": {"group_by": {"has": {"kind": "fn"}}, "metrics": {"cnt": {"op": "COUNT"}}}},
            ]
        if server_method == "holomem.getImplementation":
            examples = [{"name": "example", "arguments": {"symbol": "pkg.mod:Class.method", "max_excerpt": 320}}]
        if server_method == "holomem.restore_checkpoint":
            examples = [{"name": "example", "arguments": {"id": "20240918-120102-alpha-v12"}}]
        if server_method == "holomem.verifyNamespace":
            examples = [{"name": "example", "arguments": {"name": "alpha"}}]
        if server_method == "holomem.promoteNamespace":
            examples = [{"name": "example", "arguments": {"name": "alpha"}}]
        if server_method == "holomem.pruneCheckpoints":
            examples = [{"name": "example", "arguments": {"name": "alpha", "keep": 10}}]
        if server_method == "holomem.validateGraph":
            examples = [{"name": "example", "arguments": {"max_samples": 10}}]

        # Ensure restore_checkpoint.id is required
        if server_method == "holomem.restore_checkpoint":
            try:
                req = schema.get("required") or []
                if "id" not in req:
                    req.append("id")
                schema["required"] = req
            except Exception:
                pass

        # Description from index or helper defaults
        desc = entry_index.get(server_method, ("", None))[0]
        if not desc and server_method == "holomem.version":
            desc = "Return bridge/server versions and protocol version."
        if not desc and server_method == "holomem.capabilities":
            desc = "Return client-usable capability hints and defaults."
        if not desc and server_method == "resources.batch_read":
            desc = "Batch read resource URIs; order preserving."
        if not desc and server_method == "overlays.list":
            desc = "List registered overlays with kind and precedence."

        tools.append({
            "name": tool_name,
            "description": desc or tool_name,
            "inputSchema": schema,
            "examples": examples,
        })

    return tools

TOOLS_CATALOG = build_tools_catalog()

def handle_request(msg: Dict[str, Any]) -> None:
    """Handle a single JSON-RPC request or notification."""
    msg_id = msg.get("id")
    method = msg.get("method")
    params = msg.get("params", {})
    log_debug(f"Handling {method} with id={msg_id}")
    try:
        # Handle notifications (no id field)
        if msg_id is None:
            if method == "notifications/initialized":
                log_debug("Received initialized notification (no response needed)")
                return
            elif method == "notifications/cancelled":
                log_debug(f"Request cancelled: {params}")
                return
            # Ignore other notifications
            log_debug(f"Ignoring notification: {method}")
            return
        # Handle requests (have id field)
        if method == "initialize":
            # Extract client's protocol version if provided
            client_proto = params.get("protocolVersion", MCP_PROTOCOL_VERSION)
            result = {
                "protocolVersion": client_proto,
                "capabilities": {
                    "tools": {"dynamicRegistration": False},
                    "resources": {"dynamicRegistration": False},
                    "prompts": {"dynamicRegistration": False}
                },
                "serverInfo": {
                    "name": "holomem",
                    "version": HOLOMEM_VERSION
                }
            }
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": result
            }
            send_message(response)
            return
        elif method == "ping":
            send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {}
            })
            return
        elif method == "tools/list":
            send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": TOOLS_CATALOG}
            })
            return
        elif method == "prompts/list":
            prompts = [
                {
                    "name": "dp_slice_program_example",
                    "description": "Example: sliceProgram for a symbol under explicit lens.",
                    "arguments": {"method": "holomem.sliceProgram", "arguments": {"symbol": "A.B.C:func", "lens": "explicit"}},
                },
                {
                    "name": "dp_verify_invariants_example",
                    "description": "Example: verifyInvariants with a simple path_exists rule.",
                    "arguments": {"method": "holomem.verifyInvariants", "arguments": {"rules": [{"type": "path_exists", "from": "A", "to": "B", "max_depth": 2}]}},
                },
                {
                    "name": "dp_contrast_example",
                    "description": "Example: contrast probe vs candidates under aliases lens.",
                    "arguments": {"method": "holomem.contrast", "arguments": {"probe": "P", "candidates": ["A", "B"], "lens": "aliases"}},
                },
                {
                    "name": "dp_tests_map_example",
                    "description": "Example: testsMap with a coverage URI.",
                    "arguments": {"method": "holomem.testsMap", "arguments": {"node": "P", "coverage_uri": "file:///tmp/coverage.json"}},
                },
                {
                    "name": "dp_summarize_anchored_example",
                    "description": "Example: summarizeAnchored for nodes under aliases lens.",
                    "arguments": {"method": "holomem.summarizeAnchored", "arguments": {"nodes": ["A", "B"], "lens": "aliases"}},
                },
                {
                    "name": "dp_slice_context_example",
                    "description": "Example: sliceContext from a node with bounds.",
                    "arguments": {"method": "holomem.sliceContext", "arguments": {"from": ["A"], "max_nodes": 64, "lens": "aliases"}},
                },
            ]
            send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"prompts": prompts}
            })
            return
        elif method == "resources/list":
            try:
                resources = hm_list_resources()
            except Exception:
                resources = []
            # Make DP‑Coding schemas discoverable for $ref resolvers
            dp_schema_uris = [
                "holomem://schemas/dp-coding/sliceProgram.schema.json",
                "holomem://schemas/dp-coding/verifyInvariants.schema.json",
                "holomem://schemas/dp-coding/contrast.schema.json",
                "holomem://schemas/dp-coding/testsMap.schema.json",
                "holomem://schemas/dp-coding/summarizeAnchored.schema.json",
                "holomem://schemas/dp-coding/sliceContext.schema.json",
            ]
            resources += [
                {
                    "name": f"holomem_schema_dp_coding_{uri.rsplit('/',1)[-1].replace('.schema.json','')}",
                    "uri": uri,
                    "description": "DP‑Coding JSON Schema",
                    "mimeType": "application/json",
                    "uriOnly": True,
                }
                for uri in dp_schema_uris
            ]
            send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"resources": resources}
            })
            return
        elif method == "resources/read":
            uri = params.get("uri")
            try:
                mime, content = hm_read_resource(uri)
                send_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"uri": uri, "mimeType": mime, "content": content}
                })
            except Exception as e:
                send_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32602, "message": f"{e}"}
                })
            return
        elif method == "resources/batch_read":
            uris = params.get("uris") or []
            try:
                result = hm_batch_read(list(uris))
            except Exception:
                result = []
            send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"resources": result}
            })
            return
        elif method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments", {})
            try:
                # Bridge-local helper tools (no server round-trip)
                if name in {"holomem_get_versions", "holomem_get_capabilities", "resources_batch_read", "overlays_list"}:
                    if name == "holomem_get_versions":
                        payload = {"holomem": HOLOMEM_VERSION, "protocolVersion": MCP_PROTOCOL_VERSION}
                    elif name == "holomem_get_capabilities":
                        payload = {
                            "defaults": {
                                "findRelevant": {"mode": "auto", "score_mode": "rank"}
                            }
                        }
                    elif name == "resources_batch_read":
                        uris = list(arguments.get("uris") or [])
                        payload = {"resources": hm_batch_read(uris)}
                    elif name == "overlays_list":
                        payload = {"overlays": hm_list_overlays()}
                    else:
                        payload = {}
                    text_content = json.dumps(payload, ensure_ascii=False)[:4000]
                    response_result = {"content": [{"type": "text", "text": text_content}], "isError": False}
                    send_message({"jsonrpc": "2.0", "id": msg_id, "result": response_result})
                    return
                # Normalize arguments for known nested fields when some clients send
                # stringified JSON (e.g., has/is_a for findBy and find.query.*, and edge_filter for find_paths).
                try:
                    if name == "holomem_find_by_properties":
                        if "has" in arguments:
                            arguments["has"] = _maybe_parse_json_obj(arguments.get("has"))
                        if "is_a" in arguments:
                            arguments["is_a"] = _maybe_parse_json_obj(arguments.get("is_a"))
                    elif name == "holomem_find_by_query":
                        q = arguments.get("query")
                        if isinstance(q, dict):
                            if "has" in q:
                                q["has"] = _maybe_parse_json_obj(q.get("has"))
                            if "is_a" in q:
                                q["is_a"] = _maybe_parse_json_obj(q.get("is_a"))
                    elif name == "holomem_find_paths":
                        # edge_filter accepts a list[str] or an object (e.g., {"roles":[...]}).
                        # Tolerate clients that send a JSON-encoded string for this field.
                        ef = arguments.get("edge_filter")
                        if isinstance(ef, str):
                            try:
                                parsed = json.loads(ef)
                                if isinstance(parsed, (list, dict)):
                                    arguments["edge_filter"] = parsed
                            except Exception:
                                pass
                except Exception:
                    # Best-effort normalization; fall through to backend
                    pass
                # Call the HoloMem backend (maps holomem_* to holomem.*)
                result = call_holomem(_to_server_method(name), arguments)
                # Format the response according to MCP spec
                try:
                    text_content = json.dumps(result, ensure_ascii=False)[:4000]
                except Exception:
                    text_content = '{"status": "success"}'
                response_result = {
                    "content": [
                        {
                            "type": "text",
                            "text": text_content
                        }
                    ],
                    "isError": False
                }
                send_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": response_result
                })
            except Exception as e:
                error_result = {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error calling tool: {str(e)}"
                        }
                    ],
                    "isError": True
                }
                send_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": error_result
                })
            return
        elif method in ("shutdown", "exit"):
            send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {}
            })
            sys.exit(0)
            return
        else:
            # Unknown method
            send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            })
    except Exception as e:
        log_debug(f"Error handling request: {e}")
        if msg_id is not None:
            send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            })

def main() -> None:
    """Main entry point for the MCP server."""
    log_debug("HoloMem MCP server starting...")
    # Make sure we're in line-buffered mode
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(line_buffering=True)
    if hasattr(sys.stdin, 'reconfigure'):
        sys.stdin.reconfigure(line_buffering=True)
    try:
        while True:
            # Read next message
            msg = read_message()
            if msg is None:
                continue  # Skip empty lines or invalid JSON
            # Handle the message
            handle_request(msg)
    except EOFError:
        log_debug("EOF reached, shutting down")
    except KeyboardInterrupt:
        log_debug("Server interrupted")
    except Exception as e:
        log_debug(f"Server error: {e}")
        import traceback
        log_debug(traceback.format_exc())
    finally:
        log_debug("Server shutting down")

if __name__ == "__main__":
    main()
