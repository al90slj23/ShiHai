# OpenClaw Adapter Notes

OpenClaw should access ShiHai through the same neutral memory interfaces as Hermes:

1. ShiHai MCP server when available
2. ShiHai file protocol and schemas
3. Agent context packs exported from a self instance

For the LikeHeng self, OpenClaw-specific context lives under:

```text
selves/LikeHeng/07_Agents/openclaw/
```

User-facing OpenClaw replies may use `.c` as the source marker when configured by the self profile.
