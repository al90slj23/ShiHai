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
                    "shihai_add_conversation",
                    "shihai_add_event",
                    "shihai_propose_memory",
                    "shihai_list_pending_reviews",
                    "shihai_approve_memory",
                    "shihai_search_memory",
                },
                tool_names,
            )

    def test_tool_call_add_conversation_writes_raw_log(self):
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
                            "name": "shihai_add_conversation",
                            "arguments": {
                                "self": "TestSelf",
                                "source_agent": "hermes",
                                "source_ref": "mcp-raw-session",
                                "speaker": "user",
                                "text": "每条对话先进入 raw log，再周期性纯化。",
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
            self.assertEqual(payload["record"]["source_ref"], "mcp-raw-session")
            self.assertEqual(payload["record"]["text"], "每条对话先进入 raw log，再周期性纯化。")
            self.assertTrue(Path(payload["path"]).is_file())

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

    def test_tool_call_list_pending_reviews_and_approve_memory(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_root = Path(td)
            subprocess.run(
                [sys.executable, str(ROOT / "tools" / "shihai_memory.py"), "--root", str(tmp_root), "init-self", "TestSelf"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            proposal = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "shihai_memory.py"),
                    "--root", str(tmp_root),
                    "propose-memory",
                    "--self", "TestSelf",
                    "--claim", "用户偏好中文交流",
                    "--claim-type", "preference",
                    "--source-agent", "hermes",
                    "--source-ref", "mcp-review-test",
                    "--created-at", "2026-05-26T08:05:00+08:00",
                ],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            proposal_id = json.loads(proposal.stdout)["record"]["id"]

            result = self.run_mcp_session(
                tmp_root,
                [
                    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/call",
                        "params": {"name": "shihai_list_pending_reviews", "arguments": {"self": "TestSelf"}},
                    },
                    {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "shihai_approve_memory",
                            "arguments": {
                                "self": "TestSelf",
                                "proposal_id": proposal_id,
                                "approved_by": "LikeHeng",
                                "created_at": "2026-05-26T08:10:00+08:00",
                            },
                        },
                    },
                ],
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            responses = self.read_json_lines(result.stdout)
            list_response = next(item for item in responses if item.get("id") == 2)
            listed = json.loads(list_response["result"]["content"][0]["text"])
            self.assertEqual(listed["count"], 1)
            self.assertEqual(listed["items"][0]["id"], proposal_id)

            approve_response = next(item for item in responses if item.get("id") == 3)
            approved = json.loads(approve_response["result"]["content"][0]["text"])
            self.assertTrue(approved["ok"])
            self.assertEqual(approved["record"]["source_proposal_id"], proposal_id)
            self.assertEqual(approved["record"]["approved_by"], "LikeHeng")

    def test_tool_call_search_memory_returns_matching_records(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_root = Path(td)
            subprocess.run(
                [sys.executable, str(ROOT / "tools" / "shihai_memory.py"), "--root", str(tmp_root), "init-self", "TestSelf"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "shihai_memory.py"),
                    "--root", str(tmp_root),
                    "add-event",
                    "--self", "TestSelf",
                    "--type", "conversation",
                    "--summary", "MCP 搜索记忆事件",
                    "--source-agent", "hermes",
                    "--source-ref", "mcp-search-test",
                    "--created-at", "2026-05-26T08:00:00+08:00",
                ],
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
                            "name": "shihai_search_memory",
                            "arguments": {"self": "TestSelf", "query": "搜索记忆", "kind": "event"},
                        },
                    },
                ],
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            responses = self.read_json_lines(result.stdout)
            call_response = next(item for item in responses if item.get("id") == 2)
            payload = json.loads(call_response["result"]["content"][0]["text"])
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["items"][0]["kind"], "event")
            self.assertEqual(payload["items"][0]["source_ref"], "mcp-search-test")


if __name__ == "__main__":
    unittest.main()
