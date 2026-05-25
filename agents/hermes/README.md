# Hermes Adapter Notes

Hermes should access ShiHai through, in order of preference:

1. ShiHai MCP server when available
2. ShiHai file protocol and schemas
3. Agent context packs exported from a self instance

For the LikeHeng self, Hermes-specific context lives under:

```text
selves/LikeHeng/07_Agents/hermes/
```

User-facing Hermes replies may use `.h` as the source marker when configured by the self profile.
