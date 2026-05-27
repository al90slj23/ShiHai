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
            self.assertTrue((self_root / "00_Inbox" / "conversations" / "hermes").is_dir())
            self.assertTrue((self_root / "01_Raw" / "conversations" / "hermes").is_dir())
            self.assertTrue((self_root / "02_Processed" / "conversation_summaries").is_dir())
            self.assertTrue((self_root / "03_Canonical" / "events").is_dir())
            self.assertTrue((self_root / "03_Canonical" / "claims" / "facts.jsonl").is_file())
            self.assertTrue((self_root / "03_Canonical" / "review_queue" / "pending_memory.jsonl").is_file())
            self.assertTrue((self_root / "07_Agents" / "shared_context" / "conversation_memory_workflow.md").is_file())

    def test_add_conversation_appends_raw_log_with_digest_and_source_ref(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            self.run_cli(tmp_path, "init-self", "TestSelf")

            result = self.run_cli(
                tmp_path,
                "add-conversation",
                "--self", "TestSelf",
                "--source-agent", "hermes",
                "--source-ref", "wechat-session-1",
                "--speaker", "user",
                "--text", "原始对话应该完整保存，同时只把提炼版本写入长期记忆。",
                "--created-at", "2026-05-26T08:00:00+08:00",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["record"]["source_ref"], "wechat-session-1")
            self.assertEqual(payload["record"]["speaker"], "user")
            self.assertEqual(payload["record"]["source_agent"], "hermes")
            self.assertEqual(len(payload["record"]["sha256"]), 64)
            raw_path = Path(payload["path"])
            self.assertTrue(raw_path.name.endswith("wechat-session-1.jsonl"))
            lines = raw_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            record = json.loads(lines[0])
            self.assertEqual(record["text"], "原始对话应该完整保存，同时只把提炼版本写入长期记忆。")

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

    def test_list_pending_reviews_returns_pending_items_only(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            self.run_cli(tmp_path, "init-self", "TestSelf")
            self.run_cli(
                tmp_path,
                "propose-memory",
                "--self", "TestSelf",
                "--claim", "用户希望通过持续对话沉淀个人记忆",
                "--claim-type", "preference",
                "--source-agent", "hermes",
                "--source-ref", "test-session",
                "--created-at", "2026-05-26T08:05:00+08:00",
            )
            pending_file = tmp_path / "selves" / "TestSelf" / "03_Canonical" / "review_queue" / "pending_memory.jsonl"
            approved = {
                "id": "proposal_approved",
                "claim": "已批准的旧记忆",
                "type": "fact",
                "status": "approved",
                "created_at": "2026-05-26T08:01:00+08:00",
            }
            with pending_file.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(approved, ensure_ascii=False) + "\n")

            result = self.run_cli(tmp_path, "list-pending-reviews", "--self", "TestSelf")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["items"][0]["claim"], "用户希望通过持续对话沉淀个人记忆")
            self.assertEqual(payload["items"][0]["status"], "pending")

    def test_search_memory_finds_events_claims_and_pending_by_keyword(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            self.run_cli(tmp_path, "init-self", "TestSelf")
            self.run_cli(
                tmp_path,
                "add-event",
                "--self", "TestSelf",
                "--type", "conversation",
                "--summary", "讨论 ShiHai 的搜索记忆能力",
                "--source-agent", "hermes",
                "--source-ref", "search-session",
                "--created-at", "2026-05-26T08:00:00+08:00",
            )
            proposal = self.run_cli(
                tmp_path,
                "propose-memory",
                "--self", "TestSelf",
                "--claim", "用户希望 ShiHai 支持搜索记忆",
                "--claim-type", "preference",
                "--source-agent", "hermes",
                "--source-ref", "search-session",
                "--created-at", "2026-05-26T08:05:00+08:00",
            )
            proposal_id = json.loads(proposal.stdout)["record"]["id"]
            self.run_cli(
                tmp_path,
                "approve-memory",
                "--self", "TestSelf",
                "--proposal-id", proposal_id,
                "--approved-by", "LikeHeng",
                "--created-at", "2026-05-26T08:10:00+08:00",
            )

            result = self.run_cli(tmp_path, "search-memory", "--self", "TestSelf", "--query", "搜索记忆")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertGreaterEqual(payload["count"], 2)
            kinds = {item["kind"] for item in payload["items"]}
            self.assertIn("event", kinds)
            self.assertIn("claim", kinds)
            texts = "\n".join(item["text"] for item in payload["items"])
            self.assertIn("讨论 ShiHai 的搜索记忆能力", texts)
            self.assertIn("用户希望 ShiHai 支持搜索记忆", texts)

    def test_search_memory_filters_by_kind_and_source_ref(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            self.run_cli(tmp_path, "init-self", "TestSelf")
            self.run_cli(
                tmp_path,
                "add-event",
                "--self", "TestSelf",
                "--type", "conversation",
                "--summary", "目标会话里的搜索事件",
                "--source-agent", "hermes",
                "--source-ref", "target-session",
                "--created-at", "2026-05-26T08:00:00+08:00",
            )
            self.run_cli(
                tmp_path,
                "add-event",
                "--self", "TestSelf",
                "--type", "conversation",
                "--summary", "其他会话里的搜索事件",
                "--source-agent", "hermes",
                "--source-ref", "other-session",
                "--created-at", "2026-05-26T08:01:00+08:00",
            )

            result = self.run_cli(
                tmp_path,
                "search-memory",
                "--self", "TestSelf",
                "--query", "搜索事件",
                "--kind", "event",
                "--source-ref", "target-session",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["items"][0]["source_ref"], "target-session")
            self.assertEqual(payload["items"][0]["text"], "目标会话里的搜索事件")

    def test_approve_memory_moves_pending_item_to_claims_and_marks_approved(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            self.run_cli(tmp_path, "init-self", "TestSelf")
            proposal = self.run_cli(
                tmp_path,
                "propose-memory",
                "--self", "TestSelf",
                "--claim", "用户偏好中文交流",
                "--claim-type", "preference",
                "--source-agent", "hermes",
                "--source-ref", "test-session",
                "--created-at", "2026-05-26T08:05:00+08:00",
            )
            proposal_id = json.loads(proposal.stdout)["record"]["id"]

            result = self.run_cli(
                tmp_path,
                "approve-memory",
                "--self", "TestSelf",
                "--proposal-id", proposal_id,
                "--approved-by", "LikeHeng",
                "--created-at", "2026-05-26T08:10:00+08:00",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["record"]["claim"], "用户偏好中文交流")
            self.assertEqual(payload["record"]["status"], "active")
            self.assertEqual(payload["record"]["approved_by"], "LikeHeng")
            self.assertTrue(Path(payload["path"]).name.endswith("preferences.jsonl"))

            claims_file = tmp_path / "selves" / "TestSelf" / "03_Canonical" / "claims" / "preferences.jsonl"
            claims = [json.loads(line) for line in claims_file.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(claims), 1)
            self.assertEqual(claims[0]["source_proposal_id"], proposal_id)

            pending_file = tmp_path / "selves" / "TestSelf" / "03_Canonical" / "review_queue" / "pending_memory.jsonl"
            proposals = [json.loads(line) for line in pending_file.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(proposals[0]["status"], "approved")
            self.assertFalse(proposals[0]["needs_review"])


if __name__ == "__main__":
    unittest.main()
