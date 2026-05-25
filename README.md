# ShiHai / 识海

**ShiHai** is an open personal memory framework for digital selves.

“ShiHai / 识海” means the ocean of consciousness and memory. The project is designed to preserve, process, and retrieve a person's raw experiences, conversations, recordings, documents, relationships, preferences, decisions, and growth trajectory in portable open formats.

## Core idea

ShiHai is not tied to any single agent, app, or database. Hermes, OpenClaw, Claude, Codex, Obsidian, vector databases, and knowledge graphs are clients or replaceable components around the same personal memory substrate.

```text
ShiHai/                  # framework, schemas, protocols, tools, agent adapters
└── selves/<SelfName>/   # one digital-self memory instance
```

For this repository, personal/private memory instances under `selves/` are ignored by git by default. Use `examples/` and `templates/` for shareable samples.

## Initial goals

- Local-first and backup-friendly
- Agent-neutral: Hermes and OpenClaw are first-class clients, not owners
- Open formats: Markdown, YAML, JSONL, SQLite/Parquet exports
- Source-traceable memory: AI summaries must link back to evidence
- Review-first for sensitive identity, relationship, health, finance, and value judgments
- Rebuildable indexes: vector/graph/full-text indexes are caches, not the source of truth

## Repository layout

```text
docs/          project documentation
schemas/       JSON schemas for canonical memory records
templates/     reusable templates for selves and notes
tools/         scripts and future CLI/MCP tools
workflows/     ingestion, processing, review, backup workflows
protocols/     file, MCP, and future HTTP API protocols
agents/        common, Hermes, OpenClaw, and MCP adapter rules
examples/      safe example memory instances
selves/        private digital-self instances; gitignored by default
```

## Status

Early scaffold. The first concrete self instance is expected at:

```text
selves/LikeHeng/
```

but it is intentionally excluded from git to protect private data.
