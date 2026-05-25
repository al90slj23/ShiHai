# ShiHai File Protocol

The file protocol is the lowest common denominator for agent compatibility.

## Rules

- Canonical records use JSONL where each line is one immutable-ish record.
- Large raw or processed content should be referenced by path instead of duplicated.
- Writes should be append-first. Destructive edits require a correction record.
- Important memory changes should go through `03_Canonical/review_queue/`.

## Common locations

```text
selves/<SelfName>/03_Canonical/events/YYYY/YYYY-MM.jsonl
selves/<SelfName>/03_Canonical/entities/people.jsonl
selves/<SelfName>/03_Canonical/claims/facts.jsonl
selves/<SelfName>/03_Canonical/review_queue/pending_memory.jsonl
```
