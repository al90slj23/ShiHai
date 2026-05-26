# ShiHai MCP Protocol Draft

ShiHai MCP is the agent-facing bridge over the local ShiHai File Protocol. The
first implementation is a dependency-light stdio server:

```bash
python3 tools/shihai_mcp_server.py --root /path/to/ShiHai
```

Hermes native MCP configuration example:

```yaml
mcp_servers:
  shihai:
    command: "python3"
    args:
      - "/path/to/ShiHai/tools/shihai_mcp_server.py"
      - "--root"
      - "/path/to/ShiHai"
```

After restart, Hermes should expose tools with the `mcp_shihai_` prefix, such as
`mcp_shihai_shihai_get_context`.

## Current tools

### `shihai_get_context`

Return a Markdown context pack for a self.

Required arguments:

```json
{
  "self": "LikeHeng"
}
```

### `shihai_add_event`

Append a canonical event record under:

```text
selves/<SelfName>/03_Canonical/events/YYYY/YYYY-MM.jsonl
```

Required arguments:

```json
{
  "self": "LikeHeng",
  "type": "conversation",
  "summary": "...",
  "source_agent": "hermes",
  "source_ref": "session-or-message-id"
}
```

Optional arguments:

```json
{
  "title": "...",
  "created_at": "2026-05-26T09:00:00+08:00",
  "content_ref": "...",
  "participants": ["..."],
  "entities": ["..."],
  "topics": ["..."],
  "importance": 0.5,
  "privacy": "private",
  "confidence": 0.9
}
```

### `shihai_propose_memory`

Append a pending memory proposal under:

```text
selves/<SelfName>/03_Canonical/review_queue/pending_memory.jsonl
```

Required arguments:

```json
{
  "self": "LikeHeng",
  "claim": "...",
  "claim_type": "preference",
  "source_agent": "hermes",
  "source_ref": "session-or-message-id"
}
```

Optional arguments:

```json
{
  "created_at": "2026-05-26T09:05:00+08:00",
  "confidence": 0.9
}
```

## Future tools

- `shihai_search_memory`
- `shihai_get_person`
- `shihai_list_pending_reviews`
- `shihai_approve_memory`
- `shihai_export_context_pack`

## Security and write policy

MCP should enforce per-agent read/write scopes and log all writes. The current
minimal server delegates writes to `tools/shihai_memory.py`, which appends agent
write records under:

```text
selves/<SelfName>/_system/logs/agent_writes/<agent>.jsonl
```

Identity-shaping, sensitive, or uncertain memories should use
`shihai_propose_memory` first instead of being written directly as canonical
facts.
