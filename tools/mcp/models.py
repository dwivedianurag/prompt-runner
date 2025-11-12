from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, ConfigDict


class Namespaced(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    namespace: Optional[str] = None


class JSONRPCRequest(BaseModel):
    jsonrpc: str
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Any = None


class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Any = None


class FindParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    query: Dict[str, Any] = Field(default_factory=dict)
    topk: int = 16
    strict: Optional[bool] = None
    page_size: int = 0
    page_token: Optional[str] = None
    # score interpretability and explain controls (optional)
    score_mode: Optional[str] = None  # "raw" | "percent" | "rank"
    explain: Optional[Union[bool, Dict[str, Any]]] = None
    namespace: Optional[str] = None


class GetParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    # Canonical: name; accept alias concept_name
    name: str = Field(alias="concept_name")
    namespace: Optional[str] = None


class FindRelevantParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    probe: Any
    topk: int = 10
    page_size: int = 0
    page_token: Optional[str] = None
    score_mode: Optional[str] = None  # "raw" | "percent" | "rank"
    mode: Optional[str] = Field(default="full")  # "full" | "pattern"
    min_overlap: Optional[Dict[str, int]] = None  # e.g., {"goals":1,"constraints":1}
    explain: Optional[bool] = Field(default=True)
    namespace: Optional[str] = None


class SynthesizeParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    concept_name: str
    goal: Dict[str, Any] = Field(default_factory=dict)
    dry_run: Optional[bool] = Field(default=True)
    explain: Optional[bool] = Field(default=True)
    namespace: Optional[str] = None


class WhatIfParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    concept_name: str
    change: Dict[str, Any] = Field(default_factory=dict)
    trace_depth: int = 2
    include_performance: Optional[bool] = False
    dry_run: Optional[bool] = Field(default=True)
    explain: Optional[bool] = Field(default=True)
    namespace: Optional[str] = None


class RememberParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    # Canonical: name + roles; accept aliases concept_name, properties
    name: str = Field(alias="concept_name")
    roles: Dict[str, Any] = Field(default_factory=dict, alias="properties")
    provenance: Dict[str, Any] = Field(default_factory=dict)
    txn: Optional[str] = None
    namespace: Optional[str] = None


class ReplaceParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    # Canonical name; alias concept_name
    name: str = Field(alias="concept_name")
    previous: Dict[str, Any] = Field(default_factory=dict)
    new: Dict[str, Any] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    txn: Optional[str] = None
    namespace: Optional[str] = None


class ForgetParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    # Canonical name; alias concept_name
    name: str = Field(alias="concept_name")
    property: Optional[Dict[str, Any]] = None
    relation: Optional[Dict[str, Any]] = None
    provenance: Dict[str, Any] = Field(default_factory=dict)
    txn: Optional[str] = None
    namespace: Optional[str] = None


class BatchRememberParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    concepts: List[Dict[str, Any]]
    provenance: Dict[str, Any] = Field(default_factory=dict)
    transaction_mode: str = "best_effort"
    txn: Optional[str] = None
    namespace: Optional[str] = None


class BatchReplaceParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    items: List[Dict[str, Any]]
    provenance: Dict[str, Any] = Field(default_factory=dict)
    transaction_mode: str = "best_effort"
    txn: Optional[str] = None
    namespace: Optional[str] = None


class BatchIngestParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    artifacts: List[Dict[str, Any]]
    provenance: Dict[str, Any] = Field(default_factory=dict)
    on_error: str = "continue"
    error_threshold: float = 1.0
    txn: Optional[str] = None
    namespace: Optional[str] = None


class TransactionParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    isolation: str = "snapshot"
    namespace: Optional[str] = None


class CommitParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    txn: str
    namespace: Optional[str] = None


class RollbackParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    txn: str
    namespace: Optional[str] = None


class QueryPathParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_: List[str] = Field(default_factory=list, alias="from")
    to: List[str] = Field(default_factory=list)
    # Accept either a list of relation types or an object with roles
    edge_filter: Optional[Union[List[str], Dict[str, Any]]] = None
    not_through: Optional[List[str]] = None
    max_depth: int = 3
    page_size: int = 0
    page_token: Optional[str] = None
    # URLens and diagnostics (current-build support optional per tools/list schema)
    lens: Optional[Literal["explicit", "aliases", "materialized"]] = None
    # Optional intent resolution helper: "auto" expands classes/modules to method candidates
    mode: Optional[Literal["manual", "auto"]] = None
    explain: Optional[bool] = None
    namespace: Optional[str] = None
    namespaces: Optional[List[str]] = None
    policy: Optional[Literal["first_hit", "union"]] = None


class SliceContextParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_: List[str] = Field(default_factory=list, alias="from")
    goal: Optional[Dict[str, Any]] = None
    max_nodes: Optional[int] = 128
    page_size: int = 0
    page_token: Optional[str] = None
    lens: Optional[Literal["explicit", "aliases", "materialized"]] = None
    explain: Optional[bool] = None
    namespace: Optional[str] = None


class AggregateParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    group_by: Dict[str, Any]
    metrics: Dict[str, Any]
    having: Optional[Dict[str, Any]] = None
    namespace: Optional[str] = None


class LinkSymbolsParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    canonical_name: str
    symbols: List[Dict[str, str]]
    namespace: Optional[str] = None


class ResolveSymbolParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    language: str
    fqname: str
    namespace: Optional[str] = None


class ConfigureParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    config: Dict[str, Any]


class GCParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    remove_unreferenced: bool = False
    older_than: Optional[str] = None
    pattern: Optional[str] = None
    dry_run: bool = True
    namespace: Optional[str] = None


class CheckpointParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: Optional[str] = None
    namespace: Optional[str] = None


class RebuildParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    roles: Optional[List[str]] = None
    namespace: Optional[str] = None


class VerifyParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    pass


class DiagnoseParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    pass


class StatisticsParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    kind: Optional[str] = None
    filter: Optional[Dict[str, Any]] = None
    namespace: Optional[str] = None


class ProfileParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    duration: int = 100
    capture: Optional[List[str]] = None


class DescribeParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    kind: str = "all"
    role: Optional[str] = None
    include_values: bool = True
    page_size: int = 0
    page_token: Optional[str] = None
    namespace: Optional[str] = None

class ValidateGraphParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    max_samples: int = 20
    namespace: Optional[str] = None


class GetManyParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    names: List[str] = Field(default_factory=list)
    include_item_evidence: bool = False
    namespace: Optional[str] = None


class ProjectBundleParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    kind: str
    payload: Any
    provenance: Dict[str, Any] = Field(default_factory=dict)
    namespace: Optional[str] = None

class IngestPythonParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    module: str
    code: str
    provenance: Dict[str, Any] = Field(default_factory=dict)
    enrich: Optional[bool] = False
    txn: Optional[str] = None
    namespace: Optional[str] = None

class SessionRecordParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)
    evidence: Dict[str, Any] = Field(default_factory=dict)

class SummarizeAnchoredParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    nodes: List[str]
    lens: Optional[Literal["explicit", "aliases", "materialized"]] = None
    max_tokens: Optional[int] = None

class SliceContextParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_: List[str] = Field(default_factory=list, alias="from")
    goal: Optional[Dict[str, Any]] = None
    max_nodes: Optional[int] = 128
    page_size: int = 0
    page_token: Optional[str] = None
    lens: Optional[Literal["explicit", "aliases", "materialized"]] = None
    explain: Optional[bool] = None

class VerifyInvariantsParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    rules: List[Dict[str, Any]]
    lens: Optional[Literal["explicit", "aliases", "materialized"]] = None

class CounterexampleParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    invariant: Dict[str, Any]
    lens: Optional[Literal["explicit", "aliases", "materialized"]] = None
    max_depth: Optional[int] = None

class HypothesizeParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    claims: List[Dict[str, Any]]

class ConfirmHypothesisParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    ids: List[str]

class ForgetHypothesisParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    ids: List[str]

class ContrastParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    probe: Any
    candidates: List[str]
    lens: Optional[Literal["explicit", "aliases", "materialized"]] = None
    score_mode: Optional[str] = None
    namespace: Optional[str] = None

class PlanParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    steps: List[Dict[str, Any]]
    namespace: Optional[str] = None

class DiffImpactParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_version: str
    to_version: str
    lens: Optional[Literal["explicit", "aliases", "materialized"]] = None
    namespace: Optional[str] = None

class TestsMapParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    node: str
    coverage_uri: Optional[str] = None
    namespace: Optional[str] = None

class SliceProgramParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    symbol: str
    lens: Optional[Literal["explicit", "aliases", "materialized"]] = None
    bounds: Optional[Dict[str, Any]] = None
    namespace: Optional[str] = None

class CostEstimateParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)
    namespace: Optional[str] = None

class AdviseRetrievalParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    N: int
    target_latency: Optional[str] = None
    platform: Optional[str] = None
    namespace: Optional[str] = None

class RoleBudgetParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    role: str
    warn: Optional[bool] = None
    cap: Optional[int] = None
    namespace: Optional[str] = None

# --- Namespace Tools & Wrappers ---

class UseNamespaceParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str
    create_if_missing: Optional[bool] = None

class NamespaceOnlyParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str

class ListNamespacesParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    pass

class DescribeNamespaceParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str

class CopyMoveNamespaceParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_: str = Field(alias="from")
    to: str
    filter: Optional[Dict[str, Any]] = None

class DiffNamespacesParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_: str = Field(alias="from")
    to: str

class CrossNamespaceSearchParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    namespaces: List[str]
    text: str
    topk: Optional[int] = 10

class WithNamespaceParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str
    fallback: Optional[List[str]] = None
    policy: Optional[Literal["first_hit","union"]] = None
    operation: Dict[str, Any]

class QuickStartParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    topk: Optional[int] = 10
    namespace: Optional[str] = None

class SearchParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    text: str
    topk: Optional[int] = 16
    namespace: Optional[str] = None

class FindByParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    has: Optional[Dict[str, Any]] = None
    is_a: Optional[Dict[str, Any]] = None
    topk: Optional[int] = 16
    strict: Optional[bool] = None
    namespace: Optional[str] = None

class CodeSliceParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    symbol: str
    lens: Optional[Literal["explicit","aliases","materialized"]] = None
    enrich: Optional[bool] = None
    namespace: Optional[str] = None

class ContextGraphParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    node: str
    max_nodes: Optional[int] = 128
    lens: Optional[Literal["explicit","aliases","materialized"]] = None
    enrich: Optional[bool] = None
    namespace: Optional[str] = None

class PathBetweenParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_: List[str] = Field(default_factory=list, alias="from")
    to: List[str] = Field(default_factory=list)
    max_depth: int = 3
    lens: Optional[Literal["explicit","aliases","materialized"]] = None
    explain: Optional[bool] = None
    edge_filter: Optional[List[str]] = None
    namespace: Optional[str] = None
    namespaces: Optional[List[str]] = None
    policy: Optional[Literal["first_hit","union"]] = None

class ListClassesParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    module: Optional[str] = None
    topk: Optional[int] = 20
    enrich: Optional[bool] = None
    namespace: Optional[str] = None

class ListEnumsParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    module: Optional[str] = None
    topk: Optional[int] = 20
    namespace: Optional[str] = None

class ListMethodsParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    class_: str = Field(alias="class")
    topk: Optional[int] = 50
    strict: Optional[bool] = None
    enrich: Optional[bool] = None
    namespace: Optional[str] = None

class ListCallsParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    symbol: str
    lens: Optional[Literal["explicit","aliases"]] = None
    namespace: Optional[str] = None

class GetSignatureParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    symbol: str
    namespace: Optional[str] = None

class GetDocstringParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    symbol: str
    full: Optional[bool] = None
    namespace: Optional[str] = None

class GetImplementationParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    symbol: str
    max_excerpt: Optional[int] = 320
    namespace: Optional[str] = None

class BatchGetParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    symbols: List[str]
    page_size: Optional[int] = 32
    page_token: Optional[str] = None
    namespace: Optional[str] = None

class PruneCheckpointsParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str
    keep: int
