# ShiHai Agent Contract

All agents interacting with ShiHai must treat ShiHai as an independent memory substrate.

## Principles

1. Agents are clients, not owners.
2. Raw evidence must not be overwritten.
3. Every durable memory write must include source, author, confidence, and timestamp.
4. Sensitive or identity-shaping memories should be proposed for review before becoming canonical.
5. Vector, graph, and full-text indexes are rebuildable caches.
6. Agents should prefer ShiHai protocols over ad-hoc writes.

## Write classes

### Direct write allowed

- New raw files copied from user-approved inputs
- Processed transcripts or summaries with source refs
- Event records for clearly observed actions
- Agent write logs

### Review required

- Relationship judgments
- Identity/personality summaries
- Values, beliefs, and long-term goals
- Health, finance, legal, or safety conclusions
- Sensitive inferences about third parties

### Never write

- Passwords, API keys, payment secrets
- Unsupported speculation as fact
- Edits to raw evidence that destroy provenance

## Required metadata

```json
{
  "created_by": "hermes|openclaw|other",
  "created_at": "ISO-8601 timestamp",
  "source_ref": "path or external reference",
  "confidence": 0.0,
  "needs_review": true
}
```
