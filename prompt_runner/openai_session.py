from __future__ import annotations

import json
import os
import textwrap
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from prompt_runner.tool_catalog import ToolSpec


try:
    from openai import OpenAI  # type: ignore
    from openai import BadRequestError  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("openai package is required for prompt runner") from exc


SYSTEM_POLICY = """You are the Prompt Runner LLM orchestrator. \
You must obey Holomem-first policy: every answer must cite data retrieved via the MCP tools provided. \
You may only respond in JSON. Each turn either:
1) Issues a tool call: {"tool": "<tool_name>", "arguments": {...}}
2) Produces the final answer: {"final_summary": "<markdown>"}.
"""

DEFAULT_TOOL_TIMEOUT = 45.0
DEFAULT_HEARTBEAT_SECONDS = 5.0
MIN_HEARTBEAT_SECONDS = 0.5


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


@dataclass
class ToolCallResult:
    name: str
    arguments: Dict[str, Any]
    response: Dict[str, Any]


class InvalidJSONError(RuntimeError):
    def __init__(self, message: str, raw: str) -> None:
        super().__init__(message)
        self.raw = raw


class OpenAISession:
    def __init__(
        self,
        *,
        model: str | None,
        tool_specs: Dict[str, ToolSpec],
        system_prompt: str,
        user_prompt: str,
        namespace: str,
        max_calls: int = 20,
        verbose: bool = False,
        tool_timeout: float | None = None,
        heartbeat_interval: float | None = None,
        status_log: Path | None = None,
        summary_path: Path | None = None,
        quiet: bool = False,
    ) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY must be set to run prompt runner")
        self._client = OpenAI(api_key=api_key)
        self._model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._content_type = _resolve_content_type(self._model)
        self._messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": SYSTEM_POLICY},
            {"role": "user", "content": user_prompt},
        ]
        self._tool_specs = tool_specs
        self._namespace = namespace
        self._max_calls = max_calls
        self._verbose = verbose
        self._quiet = quiet
        timeout = tool_timeout
        if timeout is None:
            timeout = DEFAULT_TOOL_TIMEOUT
        elif timeout <= 0:
            timeout = None
        self._tool_timeout = timeout
        heartbeat = heartbeat_interval if heartbeat_interval is not None else DEFAULT_HEARTBEAT_SECONDS
        self._heartbeat_interval = max(MIN_HEARTBEAT_SECONDS, heartbeat)
        self._status_log = status_log
        self._raw_log: Optional[Path] = None
        if self._status_log is not None:
            self._status_log.parent.mkdir(parents=True, exist_ok=True)
            self._status_log.write_text("", encoding="utf-8")
            self._raw_log = self._status_log.with_name("raw_responses.log")
            self._raw_log.write_text("", encoding="utf-8")
        self.calls: List[ToolCallResult] = []
        self._request_counter = 0
        self._summary_path = summary_path

    def run(self) -> str:
        while True:
            self._request_counter += 1
            self._log(f"LLM request #{self._request_counter}")
            try:
                response = self._client.responses.create(
                    model=self._model,
                    input=[
                        {
                            "role": msg["role"],
                            "content": [{"type": self._content_type, "text": msg["content"]}],
                        }
                        for msg in self._messages
                    ],
                )
                self._log(f"openai_response: {response}", force=True)
            except BadRequestError as err:
                fallback = _maybe_flip_content_type(err)
                if fallback and fallback != self._content_type:
                    self._content_type = fallback
                    continue
                raise
            text = self._extract_text(response).strip()
            self._write_raw_response(text)
            self._log(f"raw_response: {text!r}", force=True)
            try:
                payload = self._parse_json(text)
            except InvalidJSONError as exc:
                self._log(f"✖ invalid JSON from LLM: {exc.raw!r}", force=True)
                raise
            if "tool" in payload:
                if len(self.calls) >= self._max_calls:
                    raise RuntimeError("Tool call budget exhausted")
                tool_name = payload["tool"]
                args = payload.get("arguments") or {}
                self._log(f"→ {tool_name}")
                if args:
                    self._log(f"args: {args}", verbose_only=True)
                return_payload = {"error": f"Unsupported tool '{tool_name}'"}
                spec = self._tool_specs.get(tool_name)
                canonical_name = tool_name
                if spec is None:
                    alias = _find_tool_alias(tool_name, self._tool_specs)
                    if alias is not None:
                        canonical_name = alias
                        spec = self._tool_specs.get(alias)
                if spec is None:
                    self._log(f"✖ {tool_name} failed: tool not allowed")
                    self._messages.append(
                        {
                            "role": "assistant",
                            "content": f"{{\"error\": \"Tool '{tool_name}' not allowed\"}}",
                        }
                    )
                    continue
                missing = [arg for arg in spec.required_args if arg not in args]
                if missing:
                    self._log(f"✖ {tool_name} failed: missing args {missing}")
                    self._messages.append(
                        {
                            "role": "assistant",
                            "content": json.dumps({"error": f"Missing args for {tool_name}: {missing}"}),
                        }
                    )
                    continue
                try:
                    return_payload = self._invoke_tool(spec, args)
                except Exception as exc:
                    self._log(f"✖ {tool_name} failed: {exc}", force=True)
                    error_payload = {"error": str(exc)}
                    self.calls.append(
                        ToolCallResult(
                            name=tool_name,
                            arguments=args,
                            response=error_payload,
                        )
                    )
                    self._messages.append(
                        {
                            "role": "assistant",
                            "content": json.dumps(
                                {"tool": tool_name, "arguments": args, "error": str(exc)}
                            ),
                        }
                    )
                    continue
                status = return_payload.get("status") if isinstance(return_payload, dict) else None
                if status is None:
                    self._log(f"← {canonical_name}")
                else:
                    self._log(f"← {canonical_name} status={status}")
                self.calls.append(
                    ToolCallResult(
                        name=canonical_name,
                        arguments=args,
                        response=return_payload,
                    )
                )
                self._messages.append(
                    {
                        "role": "assistant",
                        "content": json.dumps(
                            {"tool": canonical_name, "arguments": args, "result": return_payload}
                        ),
                    }
                )
            elif "final_summary" in payload:
                self._write_summary(payload["final_summary"])
                return payload["final_summary"]
            else:
                self._log(f"✖ invalid payload from LLM: {payload}", force=True)
                self._messages.append(
                    {
                        "role": "assistant",
                        "content": json.dumps({"error": "Invalid response format; expect tool or final_summary"}),
                    }
                )

    def _log(self, message: str, *, verbose_only: bool = False, force: bool = False) -> None:
        should_print = (not self._quiet or force) and (not verbose_only or self._verbose or force)
        if should_print:
            print(f"[prompt-runner] {message}", flush=True)
        if self._status_log is not None:
            timestamp = datetime.now(timezone.utc).isoformat()
            with self._status_log.open("a", encoding="utf-8") as handle:
                handle.write(f"{timestamp} {message}\n")

    def _write_raw_response(self, text: str) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        print(f"[prompt-runner][raw] {text}", flush=True)
        if self._raw_log is not None:
            with self._raw_log.open("a", encoding="utf-8") as handle:
                handle.write(f"{timestamp} {text}\n")

    def _write_summary(self, summary: str) -> None:
        if self._summary_path is None:
            return
        try:
            self._summary_path.parent.mkdir(parents=True, exist_ok=True)
            self._summary_path.write_text(summary, encoding="utf-8")
        except Exception as exc:  # pragma: no cover - logging only
            self._log(f"✖ unable to write summary file: {exc}", force=True)

    def _invoke_tool(self, spec: ToolSpec, args: Dict[str, Any]) -> Dict[str, Any]:
        from prompt_runner.mcp_client import MCPClient
        from concurrent.futures import ThreadPoolExecutor, TimeoutError

        client = MCPClient()
        merged = spec.merge_args(args, self._namespace)

        heartbeat_interval = self._heartbeat_interval
        start = time.monotonic()

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(client.call, spec.mcp_method, merged)
            while True:
                elapsed = time.monotonic() - start
                wait_for = _next_wait_interval(elapsed, self._tool_timeout, heartbeat_interval)
                if wait_for <= 0:
                    future.cancel()
                    raise RuntimeError(
                        f"MCP call '{spec.name}' timed out after {int(elapsed)}s (timeout={self._tool_timeout or 'disabled'})"
                    )
                try:
                    return future.result(timeout=wait_for)
                except TimeoutError:
                    elapsed_int = int(time.monotonic() - start)
                    self._log(f"… waiting on {spec.name} ({elapsed_int}s elapsed)")

    @staticmethod
    def _extract_text(response: Any) -> str:
        if hasattr(response, "output_text"):
            return response.output_text  # type: ignore[return-value]
        output = getattr(response, "output", None)
        if isinstance(output, list) and output:
            chunk = output[0]
            content = getattr(chunk, "content", None)
            if isinstance(content, list) and content:
                text_container = content[0]
                if isinstance(text_container, dict):
                    text = text_container.get("text")
                    if isinstance(text, str):
                        return text
                    if isinstance(text, dict):
                        return text.get("value") or text.get("text") or ""
        raise RuntimeError("Unable to extract text from OpenAI response")

    @staticmethod
    def _parse_json(text: str) -> Dict[str, Any]:
        candidate = _sanitize_json_text(text)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise InvalidJSONError(f"LLM response is not valid JSON: {exc}", candidate) from exc


def build_system_prompt(api_reference: str, tool_reference: str, tool_specs: Iterable[ToolSpec]) -> str:
    catalog_lines = []
    for spec in tool_specs:
        catalog_lines.append(
            f"- {spec.name}: {spec.description} (required: {', '.join(spec.required_args) or 'none'})"
        )
    catalog = "\n".join(catalog_lines)
    return textwrap.dedent(
        f"""
        You are an MCP planner operating under Holomem-first rules.
        Reference:
        {api_reference.strip()}

        Tools (allowed set):
        {catalog}

        Additional reference:
        {tool_reference.strip()}
        """
    ).strip()


def _sanitize_json_text(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        without_fence = text.split("```", 2)
        if len(without_fence) >= 3:
            text_block = without_fence[1]
            if text_block.lstrip().startswith("json"):
                text_block = text_block.lstrip()[4:]
            text = text_block.strip()
    try:
        json.loads(text)
        return text
    except Exception:
        block = _extract_json_block(text)
        if block:
            return block
    return text


def _extract_json_block(text: str) -> Optional[str]:
    depth = 0
    start = None
    in_string = False
    escape = False
    for idx, char in enumerate(text):
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char == "{":
            if depth == 0:
                start = idx
            depth += 1
        elif char == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    return text[start : idx + 1]
    return None


def _resolve_content_type(model_name: str) -> str:
    override = os.getenv("OPENAI_CONTENT_TYPE")
    if override in {"input_text", "output_text"}:
        return override
    lowered = model_name.lower()
    if "gpt-5" in lowered:
        return "output_text"
    return "input_text"


def _maybe_flip_content_type(error: BadRequestError) -> Optional[str]:
    message = ""
    try:
        payload = error.response.json()
        message = payload.get("error", {}).get("message") or ""
    except Exception:
        message = str(error)
    if "Supported values are: 'input_text'" in message:
        return "input_text"
    if "Supported values are: 'output_text'" in message:
        return "output_text"
    return None


def _next_wait_interval(elapsed: float, timeout: Optional[float], heartbeat: float) -> float:
    heartbeat = max(MIN_HEARTBEAT_SECONDS, heartbeat)
    if timeout is None:
        return heartbeat
    remaining = timeout - elapsed
    if remaining <= 0:
        return 0.0
    return min(heartbeat, remaining)


def _find_tool_alias(name: str, catalog: Dict[str, ToolSpec]) -> Optional[str]:
    normalized = name.replace("_", "").lower()
    for candidate in catalog.keys():
        candidate_norm = candidate.replace("_", "").lower()
        if candidate_norm == normalized:
            return candidate
    return None
