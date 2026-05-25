# ShiHai Architecture

ShiHai separates the reusable framework from individual digital-self instances.

```text
ShiHai/
├── schemas/       shared data contracts
├── protocols/     file/MCP/API contracts
├── agents/        agent compatibility rules
├── tools/         import/process/export tools
├── workflows/     repeatable memory workflows
└── selves/        private individual memory instances
```

A `self` is a concrete personal memory instance. It contains raw evidence, processed artifacts, canonical structured memory, human-readable knowledge, agent context, exports, and backups.

## Recommended self layout

```text
selves/<SelfName>/
├── 00_Inbox/       unprocessed inputs
├── 01_Raw/         original evidence, append-only
├── 02_Processed/   transcripts, OCR, cleaned text, summaries
├── 03_Canonical/   events, entities, relations, claims, review queue
├── 04_Knowledge/   curated people/projects/identity/timeline knowledge
├── 05_Obsidian/    human-readable vault
├── 06_Index/       rebuildable vector/graph/full-text indexes
├── 07_Agents/      per-agent context and permissions
├── 08_Workflows/   self-specific automation
├── 09_Exports/     context packs and portable exports
├── 10_Backups/     local snapshots/checksums
├── 90_Archive/     cold archive
├── _identity/      profile, values, goals, privacy policy
└── _system/        logs, manifests, local config
```

## Source of truth

The source of truth is open, portable data:

- `01_Raw/`
- `02_Processed/`
- `03_Canonical/`
- `04_Knowledge/`
- `05_Obsidian/`

Indexes and runtime databases are rebuildable caches.
