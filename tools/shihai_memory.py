#!/usr/bin/env python3
"""ShiHai local memory CLI.

This is the first concrete interface for the ShiHai File Protocol. It writes
portable files under `selves/<SelfName>/` and intentionally avoids runtime
services or databases.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def parse_time(value: str | None) -> datetime:
    raw = value or now_iso()
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def self_root(root: Path, name: str) -> Path:
    return root / "selves" / name


def write_text_if_missing(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def touch_jsonl(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def claims_file_for_type(base: Path, claim_type: str) -> Path:
    if claim_type == "preference":
        return base / "03_Canonical/claims/preferences.jsonl"
    return base / "03_Canonical/claims/facts.jsonl"


def init_self(args: argparse.Namespace) -> int:
    base = self_root(args.root, args.name)
    dirs = [
        "00_Inbox/conversations/hermes",
        "00_Inbox/conversations/openclaw",
        "02_Processed/conversation_summaries",
        "02_Processed/extracted_insights",
        "02_Processed/purified_notes",
        "03_Canonical/events",
        "03_Canonical/entities",
        "03_Canonical/relations",
        "03_Canonical/claims",
        "03_Canonical/decisions",
        "03_Canonical/review_queue",
        "04_Knowledge/Identity",
        "04_Knowledge/Projects",
        "04_Knowledge/People",
        "04_Knowledge/Topics",
        "04_Knowledge/Reflections",
        "05_Obsidian/Vault/01_Daily",
        "05_Obsidian/Vault/10_People",
        "05_Obsidian/Vault/20_Projects",
        "07_Agents/shared_context",
        "07_Agents/hermes",
        "07_Agents/openclaw",
        "09_Exports/agent_context_packs",
        "_identity",
        "_system/logs/agent_writes",
    ]
    for rel in dirs:
        (base / rel).mkdir(parents=True, exist_ok=True)

    touch_jsonl(base / "03_Canonical/claims/facts.jsonl")
    touch_jsonl(base / "03_Canonical/claims/preferences.jsonl")
    touch_jsonl(base / "03_Canonical/decisions/decisions.jsonl")
    touch_jsonl(base / "03_Canonical/review_queue/pending_memory.jsonl")

    write_text_if_missing(
        base / "_identity/profile.yaml",
        f"id: {args.name.lower()}\nname: {args.name}\nframework: ShiHai\nlanguage: zh\nsource_policy: conversation_first\n",
    )
    write_text_if_missing(
        base / "07_Agents/shared_context/conversation_memory_workflow.md",
        "# Conversation-first Memory Workflow\n\n交流 → 提炼 → 纯化 → 写入长期记忆。\n",
    )
    write_text_if_missing(
        base / "09_Exports/agent_context_packs/" / f"{args.name.lower()}_context.md",
        f"# {args.name} Agent Context Pack\n\nCurrent memory mode: conversation-first.\n",
    )
    print(json.dumps({"ok": True, "self": args.name, "path": str(base)}, ensure_ascii=False))
    return 0


def add_event(args: argparse.Namespace) -> int:
    created = parse_time(args.created_at)
    base = self_root(args.root, args.self_name)
    event_id = "evt_" + created.strftime("%Y%m%d_%H%M%S_") + uuid4().hex[:8]
    record = {
        "id": event_id,
        "time_start": args.created_at or created.isoformat(timespec="seconds"),
        "time_end": None,
        "type": args.event_type,
        "source_type": "conversation",
        "source_ref": args.source_ref,
        "title": args.title or args.summary[:40],
        "summary": args.summary,
        "content_ref": args.content_ref,
        "participants": args.participants or [],
        "entities": args.entities or [],
        "topics": args.topics or [],
        "importance": args.importance,
        "privacy": args.privacy,
        "confidence": args.confidence,
        "needs_review": False,
        "created_by": args.source_agent,
        "created_at": args.created_at or created.isoformat(timespec="seconds"),
    }
    events_file = base / "03_Canonical/events" / f"{created.year:04d}" / f"{created.year:04d}-{created.month:02d}.jsonl"
    append_jsonl(events_file, record)
    log_agent_write(base, args.source_agent, "add-event", events_file, args.summary, args.source_ref)
    print(json.dumps({"ok": True, "path": str(events_file), "record": record}, ensure_ascii=False))
    return 0


def propose_memory(args: argparse.Namespace) -> int:
    created = parse_time(args.created_at)
    base = self_root(args.root, args.self_name)
    record = {
        "id": "proposal_" + created.strftime("%Y%m%d_%H%M%S_") + uuid4().hex[:8],
        "claim": args.claim,
        "type": args.claim_type,
        "source_type": "conversation",
        "source_ref": args.source_ref,
        "confidence": args.confidence,
        "status": "pending",
        "needs_review": True,
        "created_by": args.source_agent,
        "created_at": args.created_at or created.isoformat(timespec="seconds"),
    }
    pending_file = base / "03_Canonical/review_queue/pending_memory.jsonl"
    append_jsonl(pending_file, record)
    log_agent_write(base, args.source_agent, "propose-memory", pending_file, args.claim, args.source_ref)
    print(json.dumps({"ok": True, "path": str(pending_file), "record": record}, ensure_ascii=False))
    return 0


def get_context(args: argparse.Namespace) -> int:
    base = self_root(args.root, args.self_name)
    sections = [f"# ShiHai Context for {args.self_name}\n"]
    profile = base / "_identity/profile.yaml"
    if profile.exists():
        sections.append("\n## Identity Profile\n\n```yaml\n" + profile.read_text(encoding="utf-8").strip() + "\n```\n")
    shared_dir = base / "07_Agents/shared_context"
    for path in sorted(shared_dir.glob("*.md")):
        sections.append(f"\n## shared_context/{path.name}\n\n" + path.read_text(encoding="utf-8").strip() + "\n")
    packs_dir = base / "09_Exports/agent_context_packs"
    for path in sorted(packs_dir.glob("*.md")):
        sections.append(f"\n## agent_context_packs/{path.name}\n\n" + path.read_text(encoding="utf-8").strip() + "\n")
    print("\n".join(sections))
    return 0


def list_pending_reviews(args: argparse.Namespace) -> int:
    base = self_root(args.root, args.self_name)
    pending_file = base / "03_Canonical/review_queue/pending_memory.jsonl"
    items = [record for record in read_jsonl(pending_file) if record.get("status") == "pending"]
    print(json.dumps({"ok": True, "count": len(items), "items": items}, ensure_ascii=False))
    return 0


def approve_memory(args: argparse.Namespace) -> int:
    created = parse_time(args.created_at)
    base = self_root(args.root, args.self_name)
    pending_file = base / "03_Canonical/review_queue/pending_memory.jsonl"
    proposals = read_jsonl(pending_file)

    match_index = -1
    proposal = None
    for index, item in enumerate(proposals):
        if item.get("id") == args.proposal_id:
            match_index = index
            proposal = item
            break
    if proposal is None:
        raise SystemExit(f"Proposal not found: {args.proposal_id}")
    if proposal.get("status") != "pending":
        raise SystemExit(f"Proposal is not pending: {args.proposal_id}")

    claim_id = "claim_" + created.strftime("%Y%m%d_%H%M%S_") + uuid4().hex[:8]
    record = {
        "id": claim_id,
        "claim": proposal["claim"],
        "type": proposal["type"],
        "source_type": proposal.get("source_type", "conversation"),
        "source_ref": proposal.get("source_ref"),
        "source_proposal_id": proposal["id"],
        "confidence": proposal.get("confidence", 0.9),
        "status": "active",
        "approved_by": args.approved_by,
        "approved_at": args.created_at or created.isoformat(timespec="seconds"),
        "created_by": proposal.get("created_by"),
        "created_at": args.created_at or created.isoformat(timespec="seconds"),
    }
    target_file = claims_file_for_type(base, proposal["type"])
    append_jsonl(target_file, record)

    proposals[match_index] = {
        **proposal,
        "status": "approved",
        "needs_review": False,
        "approved_by": args.approved_by,
        "approved_at": args.created_at or created.isoformat(timespec="seconds"),
        "claim_ref": record["id"],
    }
    write_jsonl(pending_file, proposals)
    log_agent_write(base, args.approved_by, "approve-memory", target_file, proposal["claim"], proposal.get("source_ref", ""))
    print(json.dumps({"ok": True, "path": str(target_file), "record": record}, ensure_ascii=False))
    return 0


def log_agent_write(base: Path, agent: str, action: str, target: Path, summary: str, source_ref: str) -> None:
    record = {
        "time": now_iso(),
        "agent": agent,
        "action": action,
        "target": str(target),
        "summary": summary,
        "source_ref": source_ref,
        "status": "success",
    }
    append_jsonl(base / "_system/logs/agent_writes" / f"{agent}.jsonl", record)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ShiHai local memory CLI")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="ShiHai root directory")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init-self", help="Create a conversation-first self layout")
    p_init.add_argument("name")
    p_init.set_defaults(func=init_self)

    p_event = sub.add_parser("add-event", help="Append an event record")
    p_event.add_argument("--self", dest="self_name", required=True)
    p_event.add_argument("--type", dest="event_type", required=True)
    p_event.add_argument("--summary", required=True)
    p_event.add_argument("--title")
    p_event.add_argument("--source-agent", required=True)
    p_event.add_argument("--source-ref", required=True)
    p_event.add_argument("--created-at")
    p_event.add_argument("--content-ref")
    p_event.add_argument("--participants", nargs="*", default=[])
    p_event.add_argument("--entities", nargs="*", default=[])
    p_event.add_argument("--topics", nargs="*", default=[])
    p_event.add_argument("--importance", type=float, default=0.5)
    p_event.add_argument("--privacy", default="private")
    p_event.add_argument("--confidence", type=float, default=0.9)
    p_event.set_defaults(func=add_event)

    p_prop = sub.add_parser("propose-memory", help="Append a pending memory proposal")
    p_prop.add_argument("--self", dest="self_name", required=True)
    p_prop.add_argument("--claim", required=True)
    p_prop.add_argument("--claim-type", required=True)
    p_prop.add_argument("--source-agent", required=True)
    p_prop.add_argument("--source-ref", required=True)
    p_prop.add_argument("--created-at")
    p_prop.add_argument("--confidence", type=float, default=0.9)
    p_prop.set_defaults(func=propose_memory)

    p_ctx = sub.add_parser("get-context", help="Print a self context pack for agents")
    p_ctx.add_argument("--self", dest="self_name", required=True)
    p_ctx.set_defaults(func=get_context)

    p_list = sub.add_parser("list-pending-reviews", help="List pending memory proposals")
    p_list.add_argument("--self", dest="self_name", required=True)
    p_list.set_defaults(func=list_pending_reviews)

    p_approve = sub.add_parser("approve-memory", help="Approve a pending memory proposal into canonical claims")
    p_approve.add_argument("--self", dest="self_name", required=True)
    p_approve.add_argument("--proposal-id", required=True)
    p_approve.add_argument("--approved-by", required=True)
    p_approve.add_argument("--created-at")
    p_approve.set_defaults(func=approve_memory)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.root = args.root.resolve()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
