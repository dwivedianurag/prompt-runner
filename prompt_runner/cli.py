from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from prompt_runner import CLI_NAMESPACE_DEFAULT

from prompt_runner.openai_session import (
    DEFAULT_HEARTBEAT_SECONDS,
    DEFAULT_TOOL_TIMEOUT,
    OpenAISession,
    build_system_prompt,
)
from prompt_runner.prompt_manifest import load_manifest
from prompt_runner.tool_catalog import ToolSpec, load_tool_catalog
from prompt_runner.mcp_client import MCPClient

HANDSHAKE_PROMPT = """You must ensure Holomem namespace "{namespace}" is active for subsequent tasks.
1. Call holomem_switch_to_namespace with name="{namespace}" and create_if_missing=True.
2. Verify via holomem_get_current_namespace.
Once confirmed, respond exactly once with {{"final_summary": "Namespace {namespace} ready"}}."""


def _default_preflight_specs(namespace: str) -> List[str]:
    switch_args = json.dumps({"name": namespace, "create_if_missing": True})
    return [
        f"holomem_switch_to_namespace={switch_args}",
        "holomem_get_current_namespace",
    ]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prompt-runner",
        description="LLM-driven MCP prompt runner (Holomem-first).",
    )
    parser.add_argument("--namespace", default=CLI_NAMESPACE_DEFAULT, help="Target namespace (default: ns-dra-llm-v3-prompt-cli)")
    parser.add_argument("--prompt-id", action="append", required=False, help="Prompt identifier (repeatable for multiple prompts)")
    parser.add_argument("--verbose", action="store_true", help="Print progress messages while running prompts")
    parser.add_argument("--output-dir", default="prompt_runs", help="Directory to store run artifacts")
    parser.add_argument("--checkpoint-a", dest="checkpoint_a", help="Baseline checkpoint id (drift prompt)")
    parser.add_argument("--checkpoint-b", dest="checkpoint_b", help="Current checkpoint id (drift prompt)")
    parser.add_argument("--project-name", dest="project_name", help="Supply-chain project name")
    parser.add_argument("--code-namespace", dest="code_namespace", help="Namespace with manifests/source")
    parser.add_argument("--vuln-namespace", dest="vuln_namespace", help="Namespace containing vulnerability data")
    parser.add_argument("--manifest-concept", dest="manifest_concept", help="Manifest concept name (e.g., manifest.current)")
    parser.add_argument(
        "--tool-timeout",
        type=float,
        help="Seconds to wait for each MCP call before failing (default PROMPT_RUNNER_TOOL_TIMEOUT or 45).",
    )
    parser.add_argument(
        "--heartbeat-interval",
        type=float,
        help="Seconds between heartbeat logs while waiting on MCP tools (default PROMPT_RUNNER_HEARTBEAT or 5).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output (status is still written to per-run log files).",
    )
    parser.add_argument(
        "--preflight-tool",
        action="append",
        dest="preflight_tools",
        help="Require an MCP tool to run before the main prompt (format: tool or tool=<JSON args>). Repeatable.",
    )
    parser.add_argument(
        "--no-preflight",
        action="store_true",
        help="Disable automatic preflight tool instructions.",
    )
    parser.add_argument(
        "--no-truncate-responses",
        action="store_true",
        help="Disable automatic truncation of large tool responses (enabled by default to prevent context overflow).",
    )
    return parser


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_list(name: str) -> List[str]:
    raw = os.getenv(name)
    if not raw:
        return []
    return [token.strip() for token in raw.split(",") if token.strip()]


def _parse_preflight_spec(entry: str) -> Tuple[str, Dict[str, Any]]:
    if not entry:
        raise ValueError("empty preflight spec")
    if "=" in entry:
        name, payload = entry.split("=", 1)
    elif ":" in entry and entry.count(":") == 1:
        name, payload = entry.split(":", 1)
    else:
        name, payload = entry, ""
    name = name.strip()
    if not name:
        raise ValueError("preflight tool name cannot be empty")
    args: Dict[str, Any] = {}
    payload = payload.strip()
    if payload:
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise ValueError(f"invalid JSON for preflight tool '{name}': {exc}") from exc
        if not isinstance(parsed, dict):
            raise ValueError(f"preflight tool '{name}' args must be a JSON object")
        args = parsed
    return name, args


def _resolve_preflight_specs(args: argparse.Namespace, namespace: str) -> List[Tuple[str, Dict[str, Any]]]:
    if args.no_preflight:
        return []
    raw_specs: List[str] = []
    if args.preflight_tools:
        raw_specs = list(args.preflight_tools)
    else:
        env_specs = _env_list("PROMPT_RUNNER_PREFLIGHT_TOOLS")
        if env_specs:
            raw_specs = env_specs
    if not raw_specs:
        raw_specs = _default_preflight_specs(namespace)
    parsed: List[Tuple[str, Dict[str, Any]]] = []
    for entry in raw_specs:
        try:
            parsed.append(_parse_preflight_spec(entry))
        except ValueError as exc:
            raise SystemExit(f"Invalid preflight tool '{entry}': {exc}")
    return parsed


def _normalize_tool_allowlist(entries: Iterable[str]) -> List[str]:
    normalized: List[str] = []
    for entry in entries:
        value = entry.strip() if entry else ""
        if value:
            normalized.append(value)
    return normalized


def _allowlist_allows_all(allowlist: Sequence[str]) -> bool:
    if not allowlist:
        return True
    return any(entry == "*" for entry in allowlist)


def _build_session_tools(
    tool_catalog: Dict[str, ToolSpec],
    allowlist: Sequence[str],
    preflight_specs: Sequence[Tuple[str, Dict[str, Any]]],
) -> Dict[str, ToolSpec]:
    session_tools: Dict[str, ToolSpec] = tool_catalog
    if not _allowlist_allows_all(allowlist):
        session_tools = {
            name: spec for name, spec in tool_catalog.items() if name in allowlist
        }
    if preflight_specs:
        if session_tools is tool_catalog:
            session_tools = dict(session_tools)
        for tool_name, _ in preflight_specs:
            if tool_name not in session_tools:
                spec = tool_catalog.get(tool_name)
                if spec is not None:
                    session_tools[tool_name] = spec
    return session_tools


def _summarize_preflight(specs: Sequence[Tuple[str, Dict[str, Any]]]) -> str:
    return ", ".join(
        f"{name}{' with args' if args else ''}"
        for name, args in specs
    )


def _run_direct_preflight(
    client: MCPClient,
    specs: Sequence[Tuple[str, Dict[str, Any]]],
    *,
    verbose: bool,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    if not specs:
        return results
    for name, arguments in specs:
        payload = dict(arguments)
        if verbose:
            print(f"[prompt-runner] [preflight] → {name} {payload}", flush=True)
        response = client.call(name, payload)
        if verbose:
            print(f"[prompt-runner] [preflight] ← {name}", flush=True)
        results.append({"tool": name, "arguments": payload, "response": response})
    return results


def _run_namespace_handshake(
    args: argparse.Namespace,
    tool_catalog: Dict[str, ToolSpec],
    system_prompt: str,
    tool_timeout: float | None,
    heartbeat_interval: float | None,
    preflight_specs: Sequence[Tuple[str, Dict[str, Any]]],
    mcp_client: MCPClient,
) -> None:
    handshake_tools = {
        name: spec
        for name, spec in tool_catalog.items()
        if name in {"holomem_switch_to_namespace", "holomem_get_current_namespace"}
    }
    if not handshake_tools:
        raise SystemExit("Handshake requires holomem_switch_to_namespace and holomem_get_current_namespace tools")
    timestamped = _timestamp_dir()
    run_dir = Path(args.output_dir) / "handshake" / timestamped
    run_dir.mkdir(parents=True, exist_ok=True)
    status_path = run_dir / f"status.handshake.{timestamped}.log"
    user_prompt = HANDSHAKE_PROMPT.format(namespace=args.namespace)
    if args.verbose:
        print("[prompt-runner] Starting namespace handshake via LLM", flush=True)
        if preflight_specs:
            print(f"[prompt-runner] Preflight tools: {_summarize_preflight(preflight_specs)}", flush=True)
    _run_direct_preflight(mcp_client, preflight_specs, verbose=args.verbose)
    session = OpenAISession(
        model=None,
        tool_specs=handshake_tools,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        namespace=args.namespace,
        verbose=args.verbose,
        tool_timeout=tool_timeout,
        heartbeat_interval=heartbeat_interval,
        status_log=status_path,
        summary_path=None,
        quiet=args.quiet,
        handshake_namespace=args.namespace,
        enable_truncation=not args.no_truncate_responses,
    )
    summary = session.run()
    print(f"[prompt-runner] Handshake result: {summary}")


def _print_available_tools(tool_catalog: Dict[str, ToolSpec]) -> None:
    print("[prompt-runner] Tools available for further tasks:")
    for name in sorted(tool_catalog.keys()):
        print(f" - {name}")


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _timestamp_dir() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def main(argv: List[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    tool_timeout = args.tool_timeout
    if tool_timeout is None:
        tool_timeout = _env_float("PROMPT_RUNNER_TOOL_TIMEOUT", DEFAULT_TOOL_TIMEOUT)
    heartbeat_interval = args.heartbeat_interval
    if heartbeat_interval is None:
        heartbeat_interval = _env_float("PROMPT_RUNNER_HEARTBEAT", DEFAULT_HEARTBEAT_SECONDS)
    preflight_specs = _resolve_preflight_specs(args, args.namespace)

    root = Path(__file__).resolve().parent
    manifest = load_manifest(root / "prompts" / "manifest.json")
    tool_catalog = load_tool_catalog(root / "toolspecs.json")
    api_reference = _load_text(root / "prompts" / "Holomem-API-reference.md")
    mcp_reference = _load_text(root / "prompts" / "mcp_tools_reference.md")

    # Build minimal handshake tools (only 4 tools needed)
    handshake_tools = {
        name: spec
        for name, spec in tool_catalog.items()
        if name in ["holomem_switch_to_namespace", "holomem_switchToNamespace",
                    "holomem_get_current_namespace", "holomem_getCurrentNamespace"]
    }
    handshake_system_prompt = build_system_prompt(api_reference, mcp_reference, handshake_tools.values())

    mcp_client = MCPClient()
    mcp_client.default_namespace = args.namespace
    _ensure_namespace_ready(args.namespace, mcp_client)

    _run_namespace_handshake(args, handshake_tools, handshake_system_prompt, tool_timeout, heartbeat_interval, preflight_specs, mcp_client)
    _print_available_tools(tool_catalog)

    # If no prompt IDs specified, exit after handshake
    if not args.prompt_id:
        parser.exit(0, "Namespace handshake complete. Ready for further tasks.\n")

    # Execute each specified prompt
    for prompt_id in args.prompt_id:
        if prompt_id not in manifest:
            parser.exit(1, f"Unknown prompt ID: {prompt_id}\n")

        metadata = manifest[prompt_id]
        variables = _build_variables(args, metadata.required_vars, metadata.optional_vars)

        # Filter tool catalog based on prompt's allowlist
        if "*" in metadata.tool_allowlist:
            filtered_tools = tool_catalog
            print(f"[prompt-runner] Using all {len(tool_catalog)} tools")
        else:
            filtered_tools = {
                name: spec
                for name, spec in tool_catalog.items()
                if name in metadata.tool_allowlist
            }
            print(f"[prompt-runner] Using {len(filtered_tools)} tools (filtered from {len(tool_catalog)})")

        # Create timestamped run directory
        timestamped = _timestamp_dir()
        run_dir = Path(args.output_dir) / metadata.run_directory / timestamped
        run_dir.mkdir(parents=True, exist_ok=True)

        # Set up file paths
        status_path = run_dir / f"status.{prompt_id}.{timestamped}.log"
        summary_path = run_dir / f"summary.{prompt_id}.{timestamped}.md"
        prompt_log_path = run_dir / f"prompt.{prompt_id}.{timestamped}.log"

        # Load and substitute prompt template
        prompt_template_path = root / "prompts" / f"{prompt_id}.md"
        user_prompt = _load_text(prompt_template_path)
        for key, value in variables.items():
            placeholder = "{" + key + "}"
            user_prompt = user_prompt.replace(placeholder, value)

        # Rebuild system prompt with filtered tools for this specific prompt
        prompt_system_prompt = build_system_prompt(api_reference, mcp_reference, filtered_tools.values())

        # Run the prompt
        print(f"[prompt-runner] Running prompt: {prompt_id}")
        session = OpenAISession(
            model=None,  # Uses OPENAI_MODEL env var
            tool_specs=filtered_tools,  # Use filtered tools
            system_prompt=prompt_system_prompt,  # Use rebuilt system prompt
            user_prompt=user_prompt,
            namespace=args.namespace,
            max_calls=20,  # Default max tool calls
            verbose=args.verbose,
            tool_timeout=tool_timeout,
            heartbeat_interval=heartbeat_interval,
            status_log=status_path,
            summary_path=summary_path,
            quiet=args.quiet,
            handshake_namespace=None,  # Already completed handshake
            enable_truncation=not args.no_truncate_responses,
        )

        # Execute and get summary
        summary = session.run()

        # Write tool call log
        with prompt_log_path.open("w", encoding="utf-8") as f:
            for call in session.calls:
                f.write(json.dumps({
                    "tool": call.name,
                    "arguments": call.arguments,
                    "response": call.response
                }) + "\n")

        print(f"[prompt-runner] ✓ {prompt_id} complete")
        print(f"[prompt-runner]   Summary: {summary_path}")
        print(f"[prompt-runner]   Logs: {status_path}")

    return 0


def _build_variables(
    args: argparse.Namespace,
    required: Iterable[str],
    optional: Dict[str, str | None],
) -> Dict[str, str]:
    vars_map = {
        "namespace": args.namespace,
        "checkpoint_a": args.checkpoint_a,
        "checkpoint_b": args.checkpoint_b,
        "project_name": args.project_name,
        "code_namespace": args.code_namespace or args.namespace,
        "vuln_namespace": args.vuln_namespace,
        "manifest_concept": args.manifest_concept,
    }
    missing = [name for name in required if not vars_map.get(name)]
    if missing:
        raise SystemExit(f"Missing required variables for prompt: {missing}")
    for key, default in optional.items():
        if vars_map.get(key) is None and default is not None:
            vars_map[key] = default
    return {key: str(value) for key, value in vars_map.items() if value is not None}


def _ensure_namespace_ready(namespace: str, client: MCPClient) -> None:
    client.call("holomem_switch_to_namespace", {"name": namespace, "create_if_missing": True})
    proposal_query = {
        "namespace": namespace,
        "query": {"has": {"is_a": "proposal"}},
        "topk": 1,
    }
    response = client.call("holomem_find_by_query", proposal_query)
    if not _extract_results(response):
        concept_name = f"proposal.prompt_runner.{namespace}.{_timestamp_dir()}"
        properties = {
            "is_a": "proposal",
            "goals": ["Prompt runner Holomem session"],
            "constraints": ["LLM tool planning via MCP"],
            "namespace": namespace,
        }
        client.call(
            "holomem_store_concept",
            {"namespace": namespace, "concept_name": concept_name, "properties": properties},
        )


def _extract_results(payload: Dict[str, object]) -> List[object]:
    if isinstance(payload.get("results"), list):
        return payload["results"]  # type: ignore[return-value]
    result = payload.get("result")
    if isinstance(result, dict) and isinstance(result.get("results"), list):
        return result["results"]  # type: ignore[return-value]
    return []


if __name__ == "__main__":  # pragma: no cover
    main()
