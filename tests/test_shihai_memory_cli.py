import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "shihai_memory.py"


class ShihaiMemoryCliTest(unittest.TestCase):
    def run_cli(self, tmp_root, *args):
        return subprocess.run(
            [sys.executable, str(CLI), "--root", str(tmp_root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_init_self_creates_conversation_first_layout(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            result = self.run_cli(tmp_path, "init-self", "TestSelf")

            self.assertEqual(result.returncode, 0, result.stderr)
            self_root = tmp_path / "selves" / "TestSelf"
            self.assertTrue((self_root / "03_Canonical" / "events").is_dir())
            self.assertTrue((self_root / "03_Canonical" / "claims" / "facts.jsonl").is_file())
            self.assertTrue((self_root / "03_Canonical" / "review_queue" / "pending_memory.jsonl").is_file())
            self.assertTrue((self_root / "07_Agents" / "shared_context" / "conversation_memory_workflow.md").is_file())

    def test_add_event_appends_monthly_jsonl_with_required_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            self.run_cli(tmp_path, "init-self", "TestSelf")

            result = self.run_cli(
                tmp_path,
                "add-event",
                "--self", "TestSelf",
                "--type", "conversation",
                "--summary", "讨论 ShiHai 的对话记忆框架",
                "--source-agent", "hermes",
                "--source-ref", "test-session",
                "--created-at", "2026-05-26T08:00:00+08:00",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["record"]["created_by"], "hermes")
            self.assertEqual(payload["record"]["source_ref"], "test-session")
            events_file = tmp_path / "selves" / "TestSelf" / "03_Canonical" / "events" / "2026" / "2026-05.jsonl"
            lines = events_file.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            record = json.loads(lines[0])
            self.assertEqual(record["type"], "conversation")
            self.assertEqual(record["summary"], "讨论 ShiHai 的对话记忆框架")
            self.assertFalse(record["needs_review"])

    def test_propose_memory_appends_pending_review_item(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            self.run_cli(tmp_path, "init-self", "TestSelf")

            result = self.run_cli(
                tmp_path,
                "propose-memory",
                "--self", "TestSelf",
                "--claim", "用户希望通过持续对话沉淀个人记忆",
                "--claim-type", "preference",
                "--source-agent", "hermes",
                "--source-ref", "test-session",
                "--created-at", "2026-05-26T08:05:00+08:00",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            pending_file = tmp_path / "selves" / "TestSelf" / "03_Canonical" / "review_queue" / "pending_memory.jsonl"
            lines = pending_file.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            record = json.loads(lines[0])
            self.assertEqual(record["claim"], "用户希望通过持续对话沉淀个人记忆")
            self.assertTrue(record["needs_review"])
            self.assertEqual(record["created_by"], "hermes")

    def test_get_context_reads_identity_and_context_pack(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            self.run_cli(tmp_path, "init-self", "TestSelf")
            self_root = tmp_path / "selves" / "TestSelf"
            (self_root / "_identity" / "profile.yaml").write_text("name: TestSelf\nlanguage: zh\n", encoding="utf-8")
            pack = self_root / "09_Exports" / "agent_context_packs" / "testself_context.md"
            pack.parent.mkdir(parents=True, exist_ok=True)
            pack.write_text("# TestSelf Context\n\nconversation-first memory", encoding="utf-8")

            result = self.run_cli(tmp_path, "get-context", "--self", "TestSelf")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("# ShiHai Context for TestSelf", result.stdout)
            self.assertIn("name: TestSelf", result.stdout)
            self.assertIn("conversation-first memory", result.stdout)


if __name__ == "__main__":
    unittest.main()
