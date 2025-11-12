from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Mapping


@dataclass(frozen=True)
class PromptMetadata:
    prompt_id: str
    template_path: Path
    description: str
    required_vars: Iterable[str]
    optional_vars: Mapping[str, str | None]
    tool_allowlist: Iterable[str]
    run_directory: str


def load_manifest(manifest_path: Path) -> Dict[str, PromptMetadata]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest: Dict[str, PromptMetadata] = {}
    for prompt_id, entry in data.items():
        template = manifest_path.parent / entry["template"]
        manifest[prompt_id] = PromptMetadata(
            prompt_id=prompt_id,
            template_path=template,
            description=entry.get("description", ""),
            required_vars=tuple(entry.get("required_vars", [])),
            optional_vars=dict(entry.get("optional_vars", {})),
            tool_allowlist=tuple(entry.get("tool_allowlist", [])),
            run_directory=entry.get("run_directory", prompt_id),
        )
    return manifest
