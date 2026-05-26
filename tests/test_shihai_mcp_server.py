import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MCP_SERVER = ROOT / "tools" / "shihai_mcp_server.py"


class ShihaiMcpServerTest(unittest.TestCase):
    def run_mcp_session(self, tmp_root, messages):
        wire = "".join(json.dumps(msg, ensure_ascii=False) + "\n" for msg in messages)
        return subprocess.run(
            [sys.executable, str(MCP_SERVER), "--root", str(tmp_root)],
            input=wire,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )

    def read_json_lines(self, stdout):
        return [json.loads(line) for line in stdout.splitlines() if line.strip()]

    def test_tools_list_exposes_shihai_memory_tools(self):
        with tempfile.TemporaryDirectory() as td:
            result = self.run_mcp_session(
                Path(td),
                [
                    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                    {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
                ],
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            responses = self.read_json_lines(result.stdout)
            tool_response = next(item for item in responses if item.get("id") == 2)
            tool_names = {tool["name"] for tool in tool_response["result"]["tools"]}
            self.assertEqual(
                {
                    "shihai_get_context",
                    "shihai_add_event",
                    "shihai_propose_memory",
                },
                tool_names,
            )

    def test_tool_call_add_event_writes_canonical_event_and_returns_payload(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_root = Path(td)
            # The MCP server should be able to initialize the self through the
            # same file protocol assumptions used by the CLI.
            subprocess.run(
                [sys.executable, str(ROOT / "tools" / "shihai_memory.py"), "--root", str(tmp_root), "init-self", "TestSelf"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            result = self.run_mcp_session(
                tmp_root,
                [
                    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/call",
                        "params": {
                            "name": "shihai_add_event",
                            "arguments": {
                                "self": "TestSelf",
                                "type": "conversation",
                                "summary": "通过 MCP 写入 ShiHai 事件",
                                "source_agent": "hermes",
                                "source_ref": "mcp-test-session",
                                "created_at": "2026-05-26T09:00:00+08:00",
                            },
                        },
                    },
                ],
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            responses = self.read_json_lines(result.stdout)
            call_response = next(item for item in responses if item.get("id") == 2)
            self.assertFalse(call_response["result"].get("isError", False))
            payload = json.loads(call_response["result"]["content"][0]["text"])
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["record"]["source_ref"], "mcp-test-session")

            events_file = tmp_root / "selves" / "TestSelf" / "03_Canonical" / "events" / "2026" / "2026-05.jsonl"
            records = [json.loads(line) for line in events_file.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["summary"], "通过 MCP 写入 ShiHai 事件")

    def test_tool_call_get_context_returns_markdown_text(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_root = Path(td)
            subprocess.run(
                [sys.executable, str(ROOT / "tools" / "shihai_memory.py"), "--root", str(tmp_root), "init-self", "TestSelf"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            result = self.run_mcp_session(
                tmp_root,
                [
                    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/call",
                        "params": {
                            "name": "shihai_get_context",
                            "arguments": {"self": "TestSelf"},
                        },
                    },
                ],
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            responses = self.read_json_lines(result.stdout)
            call_response = next(item for item in responses if item.get("id") == 2)
            text = call_response["result"]["content"][0]["text"]
            self.assertIn("# ShiHai Context for TestSelf", text)
            self.assertIn("conversation-first", text)


if __name__ == "__main__":
    unittest.main()
