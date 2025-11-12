from __future__ import annotations

import os
from typing import Any, Dict

from prompt_runner import CLI_NAMESPACE_DEFAULT

import sys
from pathlib import Path
from typing import Iterable


def _candidate_mcp_paths() -> Iterable[Path]:
    root = Path(__file__).resolve()
    yield root.parents[1] / "tools" / "mcp"
    yield root.parent / "tools" / "mcp"


for candidate in _candidate_mcp_paths():
    if candidate.is_dir():
        candidate_str = str(candidate)
        if candidate_str not in sys.path:
            sys.path.append(candidate_str)

try:
    from tools.mcp import mcp_bridge  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("mcp_bridge module is required for prompt runner") from exc


class MCPClient:
    """Lightweight MCP JSON-RPC client for prompt runner."""

    def __init__(self, endpoint: str | None = None) -> None:
        self.endpoint = endpoint or os.getenv("MCP_ENDPOINT") or getattr(
            mcp_bridge, "DEFAULT_ENDPOINT", "http://127.0.0.1:8085/mcp"
        )
        self.default_namespace = CLI_NAMESPACE_DEFAULT

    def call(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        previous = os.environ.get("HOLOMEM_HTTP_ENDPOINT")
        os.environ["HOLOMEM_HTTP_ENDPOINT"] = self.endpoint
        try:
            return mcp_bridge.call_holomem(method, params)
        finally:
            if previous is None:
                os.environ.pop("HOLOMEM_HTTP_ENDPOINT", None)
            else:
                os.environ["HOLOMEM_HTTP_ENDPOINT"] = previous
