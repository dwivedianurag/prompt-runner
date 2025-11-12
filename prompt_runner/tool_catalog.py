from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Mapping


@dataclass(frozen=True)
class ToolSpec:
    name: str
    mcp_method: str
    description: str
    required_args: tuple[str, ...]
    optional_args: tuple[str, ...]
    default_args: Mapping[str, object]

    def merge_args(self, provided: Mapping[str, object], namespace: str) -> Dict[str, object]:
        args = dict(self.default_args)
        args.update(provided)
        if (
            "namespace" in self.optional_args
            or "namespace" in self.required_args
            or "namespace" not in args
        ):
            args.setdefault("namespace", namespace)
        return args


def load_tool_catalog(config_path: Path) -> Dict[str, ToolSpec]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    reference_path = config_path.parent / config["reference"]
    blocked_names = set(config.get("blocked_tool_names", []))
    blocked_substrings = tuple(config.get("blocked_substrings", []))

    table_rows = _parse_markdown_table(reference_path.read_text(encoding="utf-8"))
    catalog: Dict[str, ToolSpec] = {}
    for row in table_rows:
        tool_name = row["tool"]
        if _is_blocked(tool_name, blocked_names, blocked_substrings):
            continue
        catalog[tool_name] = ToolSpec(
            name=tool_name,
            mcp_method=row["method"],
            description=row["description"],
            required_args=row["required"],
            optional_args=row["optional"],
            default_args={},
        )
    return catalog


def _is_blocked(name: str, blocked_names: Iterable[str], blocked_substrings: Iterable[str]) -> bool:
    lowered = name.lower()
    if name in blocked_names:
        return True
    return any(token.lower() in lowered for token in blocked_substrings)


def _parse_markdown_table(text: str) -> Iterable[Dict[str, object]]:
    rows: list[Dict[str, object]] = []
    for line in text.splitlines():
        if not line.startswith("| `"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) < 5:
            continue
        tool = parts[0].strip("`")
        method = parts[1].strip("`")
        required = _parse_arg_list(parts[2])
        optional = _parse_arg_list(parts[3])
        description = parts[4]
        rows.append(
            {
                "tool": tool,
                "method": method,
                "required": tuple(required),
                "optional": tuple(optional),
                "description": description,
            }
        )
    return rows


def _parse_arg_list(cell: str) -> list[str]:
    if not cell or cell in {"—", "-"}:
        return []
    args: list[str] = []
    for entry in cell.split("<br>"):
        token = entry.strip()
        if not token:
            continue
        match = re.match(r"`([^`]+)`", token)
        if match:
            name = match.group(1)
        else:
            name = token.split(":", 1)[0]
        name = name.strip()
        if name:
            args.append(name)
    return args
