#!/usr/bin/env python3
"""Minimal ShiHai MCP stdio server.

This server exposes the local ShiHai File Protocol through MCP-compatible
JSON-RPC methods. It intentionally keeps runtime dependencies at zero for the
first usable bridge: Hermes/OpenClaw can launch it as a stdio process and call
ShiHai tools without needing a daemon or database.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

# Allow direct execution from tools/ while importing the sibling CLI module.
TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import shihai_memory  # noqa: E402


SERVER_INFO = {"name": "shihai-mcp-server", "version": "0.1.0"}


TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "shihai_get_context",
        "description": "Return a Markdown context pack for a ShiHai self.",
        "inputSchema": {
            "type": "object",
            "properties": {"self": {"type": "string", "description": "Self name, e.g. LikeHeng"}},
            "required": ["self"],
            "additionalProperties": False,
        },
    },
    {
        "name": "shihai_add_event",
        "description": "Append a canonical conversation/event record to a ShiHai self.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "self": {"type": "string"},
                "type": {"type": "string", "description": "Event type, e.g. conversation, decision, milestone"},
                "summary": {"type": "string"},
                "title": {"type": "string"},
                "source_agent": {"type": "string"},
                "source_ref": {"type": "string"},
                "created_at": {"type": "string"},
                "content_ref": {"type": "string"},
                "participants": {"type": "array", "items": {"type": "string"}},
                "entities": {"type": "array", "items": {"type": "string"}},
                "topics": {"type": "array", "items": {"type": "string"}},
                "importance": {"type": "number"},
                "privacy": {"type": "string"},
                "confidence": {"type": "number"},
            },
            "required": ["self", "type", "summary", "source_agent", "source_ref"],
            "additionalProperties": False,
        },
    },
    {
        "name": "shihai_propose_memory",
        "description": "Append a pending memory proposal that requires human review.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "self": {"type": "string"},
                "claim": {"type": "string"},
                "claim_type": {"type": "string"},
                "source_agent": {"type": "string"},
                "source_ref": {"type": "string"},
                "created_at": {"type": "string"},
                "confidence": {"type": "number"},
            },
            "required": ["self", "claim", "claim_type", "source_agent", "source_ref"],
            "additionalProperties": False,
        },
    },
]


class McpError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class ShihaiMcpServer:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.tools: dict[str, Callable[[dict[str, Any]], str]] = {
            "shihai_get_context": self.tool_get_context,
            "shihai_add_event": self.tool_add_event,
            "shihai_propose_memory": self.tool_propose_memory,
        }

    def serve(self) -> int:
        for line in sys.stdin:
            if not line.strip():
                continue
            try:
                request = json.loads(line)
                response = self.handle_request(request)
            except json.JSONDecodeError as exc:
                response = self.error_response(None, -32700, f"Parse error: {exc}")
            except Exception as exc:  # Keep stdio server alive on per-request errors.
                response = self.error_response(None, -32603, f"Internal error: {exc}")
            if response is not None:
                print(json.dumps(response, ensure_ascii=False), flush=True)
        return 0

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any] | None:
        method = request.get("method")
        request_id = request.get("id")

        try:
            if method == "initialize":
                return self.result_response(
                    request_id,
                    {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": SERVER_INFO,
                    },
                )
            if method == "notifications/initialized":
                return None
            if method == "tools/list":
                return self.result_response(request_id, {"tools": TOOL_SCHEMAS})
            if method == "tools/call":
                params = request.get("params") or {}
                return self.result_response(request_id, self.call_tool(params))
            if method == "ping":
                return self.result_response(request_id, {})
            raise McpError(-32601, f"Method not found: {method}")
        except McpError as exc:
            return self.error_response(request_id, exc.code, exc.message)

    def call_tool(self, params: dict[str, Any]) -> dict[str, Any]:
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if name not in self.tools:
            raise McpError(-32602, f"Unknown tool: {name}")
        if not isinstance(arguments, dict):
            raise McpError(-32602, "Tool arguments must be an object")

        try:
            text = self.tools[name](arguments)
            return {"content": [{"type": "text", "text": text}], "isError": False}
        except Exception as exc:
            return {"content": [{"type": "text", "text": str(exc)}], "isError": True}

    def tool_get_context(self, arguments: dict[str, Any]) -> str:
        require(arguments, "self")
        args = SimpleNamespace(root=self.root, self_name=arguments["self"])
        return capture_stdout(shihai_memory.get_context, args)

    def tool_add_event(self, arguments: dict[str, Any]) -> str:
        require(arguments, "self", "type", "summary", "source_agent", "source_ref")
        args = SimpleNamespace(
            root=self.root,
            self_name=arguments["self"],
            event_type=arguments["type"],
            summary=arguments["summary"],
            title=arguments.get("title"),
            source_agent=arguments["source_agent"],
            source_ref=arguments["source_ref"],
            created_at=arguments.get("created_at"),
            content_ref=arguments.get("content_ref"),
            participants=arguments.get("participants", []),
            entities=arguments.get("entities", []),
            topics=arguments.get("topics", []),
            importance=arguments.get("importance", 0.5),
            privacy=arguments.get("privacy", "private"),
            confidence=arguments.get("confidence", 0.9),
        )
        return capture_stdout(shihai_memory.add_event, args).strip()

    def tool_propose_memory(self, arguments: dict[str, Any]) -> str:
        require(arguments, "self", "claim", "claim_type", "source_agent", "source_ref")
        args = SimpleNamespace(
            root=self.root,
            self_name=arguments["self"],
            claim=arguments["claim"],
            claim_type=arguments["claim_type"],
            source_agent=arguments["source_agent"],
            source_ref=arguments["source_ref"],
            created_at=arguments.get("created_at"),
            confidence=arguments.get("confidence", 0.9),
        )
        return capture_stdout(shihai_memory.propose_memory, args).strip()

    @staticmethod
    def result_response(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    @staticmethod
    def error_response(request_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def require(arguments: dict[str, Any], *names: str) -> None:
    missing = [name for name in names if name not in arguments or arguments[name] in (None, "")]
    if missing:
        raise ValueError("Missing required argument(s): " + ", ".join(missing))


def capture_stdout(func: Callable[[Any], int], args: Any) -> str:
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        exit_code = func(args)
    if exit_code != 0:
        raise RuntimeError(f"ShiHai operation failed with exit code {exit_code}")
    return stream.getvalue()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ShiHai MCP stdio server")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="ShiHai root directory")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return ShihaiMcpServer(args.root).serve()


if __name__ == "__main__":
    raise SystemExit(main())
