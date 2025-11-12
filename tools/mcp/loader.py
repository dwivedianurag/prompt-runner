from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parent


def _path_for_uri(uri: str) -> Path:
    """Map a holomem:// URI to a file under resources/.

    Example: holomem://sro/relation_aliases.json → <ROOT>/sro/relation_aliases.json
    """
    if not uri.startswith("holomem://"):
        raise ValueError(f"unsupported URI: {uri}")
    rest = uri[len("holomem://"):]
    return ROOT / rest



def list_resources() -> List[Dict[str, Any]]:
    """Return a list of resource descriptors for MCP resources/list.

    Large documents are marked uriOnly=true to encourage resources/read.
    """
    entries = [
        {
            "name": "holomem_sro_relation_aliases",
            "uri": "holomem://sro/relation_aliases.json",
            "description": "URLens relation-alias registry (preferred over equivalences.relation_aliases).",
            "mimeType": "application/json",
            "uriOnly": True,
        },
        {
            "name": "holomem_schema_urlens_relation_aliases",
            "uri": "holomem://schemas/urlens/relation_aliases.schema.json",
            "description": "JSON Schema for URLens relation-alias rules (Draft-07).",
            "mimeType": "application/json",
            "uriOnly": True
        },
        {
            "name": "holomem_schema_evidence",
            "uri": "holomem://schemas/evidence.schema.json",
            "description": "JSON Schema for H-AST/HoloMem evidence objects (Draft-07).",
            "mimeType": "application/json",
            "uriOnly": True
        },
        {
            "name": "holomem_sro_ontology",
            "uri": "holomem://sro/ontology.json",
            "description": "Structural Reasoning Ontology (SRO)",
            "mimeType": "application/json",
            "uriOnly": True,
        },
        {
            "name": "holomem_sro_extractors",
            "uri": "holomem://sro/extractors.json",
            "description": "Ambiguity-safe extractors (hard/soft/negative)",
            "mimeType": "application/json",
            "uriOnly": True,
        },
        {
            "name": "holomem_sro_equivalences",
            "uri": "holomem://sro/equivalences.json",
            "description": "Platform/domain equivalence mappings with provenance/weights",
            "mimeType": "application/json",
            "uriOnly": True,
        },
        {
            "name": "holomem_synthesis_templates",
            "uri": "holomem://synthesis/templates.json",
            "description": "Micro-templates by SRO tags and platform",
            "mimeType": "application/json",
            "uriOnly": True,
        },
        {
            "name": "holomem_synthesis_rules",
            "uri": "holomem://synthesis/rules.json",
            "description": "Composition rules, conflict resolution policies, verification hooks",
            "mimeType": "application/json",
            "uriOnly": True,
        },
        {
            "name": "holomem_implications_rules",
            "uri": "holomem://implications/rules.json",
            "description": "Rule chaining for implications with bounds",
            "mimeType": "application/json",
            "uriOnly": True,
        },
        {
            "name": "holomem_overlays_sro_ontology",
            "uri": "holomem://overlays/sro/ontology.json",
            "description": "Overlay SRO additions/overrides (optional)",
            "mimeType": "application/json",
            "uriOnly": True,
        },
        # Canonical templates (kept inline for immediacy)
        {
            "name": "holomem_reasoning_template",
            "uri": "holomem://templates/reasoning.json",
            "description": "Canonical template for first-class reasoning objects",
            "mimeType": "application/json",
            "content": {
                "$schema": "https://holomem.dev/templates/reasoning.schema.json",
                "roles": {
                    "problem_type": "real_time_classification_system",
                    "domain": "fraud_detection",
                    "constraints": {"budget": "30000_usd_month", "latency": "100ms", "platform": "aws", "team_size": 5},
                    "goals": ["scale_10x", "reduce_false_positives", "improve_accuracy"],
                    "decisions": [
                        {"decision": "processing_model", "alternatives": ["streaming", "batch", "micro_batch", "hybrid"], "rationale": "Streaming chosen for sub-100ms decisioning.", "confidence": 0.85, "assumptions": ["traffic_is_continuous", "latency_is_critical"]}
                    ],
                    "final_architecture": {"layers": ["rules_engine", "ml_ensemble"], "storage": ["redis", "postgres", "s3"]},
                    "success_metrics": {"false_positive_rate_target": 0.05, "detection_rate_target": 0.9, "throughput_target_per_hour": 100000}
                }
            }
        },
        {
            "name": "holomem_meta_reasoning_template",
            "uri": "holomem://templates/meta_reasoning.json",
            "description": "Template for meta-reasoning/transfer summaries",
            "mimeType": "application/json",
            "content": {
                "$schema": "https://holomem.dev/templates/meta_reasoning.schema.json",
                "roles": {
                    "derived_from": "cot_fraud_detection_arch",
                    "similarity_probe": {"problem_type": "real_time_classification_system", "goals": ["reduce_false_positives", "scale_10x"], "constraints": {"budget": "40000_usd_month", "latency": "1s", "platform": "gcp"}},
                    "pattern_transfer_summary": {
                        "transferred": [{"pattern": "two_layer_architecture", "confidence": 0.9}, {"pattern": "polyglot_storage", "confidence": 0.85}],
                        "adapted": [
                            {"pattern": "processing_model", "from": "hybrid", "to": "async_heavy", "reason": "relaxed_latency", "confidence": 0.8},
                            {"pattern": "platform_mapping", "from": "aws", "to": "gcp", "reason": "org_standard", "confidence": 0.85}
                        ],
                        "departures": [{"pattern": "multimodal_pipelines", "reason": "text_and_images", "confidence": 0.85}]
                    },
                    "decision_quality": {"avg_confidence": 0.84, "assumptions_coverage": 0.9},
                    "synthesis_confidence": 0.82,
                    "counterfactuals_explored": ["2x_budget", "ml_heavy_team", "latency_1s"],
                    "explanations": {"mode": "pattern_transfer", "notes": "GCP mapping of AWS components verified."}
                }
            }
        }
    ]
    return entries


def read_resource(uri: str) -> Tuple[str, Dict[str, Any]]:
    path = _path_for_uri(uri)
    if not path.exists():
        raise FileNotFoundError(f"resource not found: {uri}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return "application/json", data


def batch_read(uris: List[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for u in uris:
        try:
            mime, content = read_resource(u)
            out.append({"uri": u, "mimeType": mime, "content": content})
        except Exception as e:
            out.append({"uri": u, "error": str(e)})
    return out


def list_overlays() -> List[Dict[str, Any]]:
    overlays: List[Dict[str, Any]] = []
    base = ROOT / "overlays"
    if not base.exists():
        return overlays
    for p in base.rglob("*.json"):
        # Build URIs relative to resources/ to be resolvable by read_resource.
        try:
            rel = p.relative_to(ROOT)
        except Exception:
            try:
                rel = p.relative_to(ROOT.parent)
            except Exception:
                rel = p
        rel_posix = rel.as_posix()
        if rel_posix.startswith("resources/"):
            rel_posix = rel_posix[len("resources/"):]
        overlays.append({
            "uri": f"holomem://{rel_posix}",
            "kind": "sro" if "/sro/" in rel_posix else "generic",
            "precedence": 100  # simple default precedence
        })
    return overlays
