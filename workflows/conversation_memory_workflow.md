# Conversation-first Memory Workflow

> 通用工作流：把用户与 Agent 的持续交流沉淀为长期个人记忆。

## 适用场景

当一个 self 主要通过与 Agent 交流来建立记忆，而不是优先通过录音、文件或外部导入时，使用本工作流。

## Pipeline

```text
raw conversation capture
  → session summary
  → extracted insights
  → memory classification
  → review queue or canonical write
  → knowledge note update
  → agent context pack refresh
```

## Capture and consolidation rhythm

ShiHai uses a hybrid rhythm:

1. **实时轻量捕获**：每条对话先写入 `01_Raw/conversations/<source_agent>/<source_ref>.jsonl`，作为可回溯证据。
2. **即时候选提炼**：明显长期有价值的偏好、决策、项目原则可立即进入 `pending_memory.jsonl`。
3. **周期性纯化**：会话结束、每 N 分钟、每日或每周批处理，对 raw log 生成 summary、insight 和 canonical proposal。

## Memory classification

| 类型 | 目标位置 |
|---|---|
| event | `03_Canonical/events/` |
| claim | `03_Canonical/claims/` |
| decision | `03_Canonical/decisions/` |
| sensitive inference | `03_Canonical/review_queue/` |
| curated note | `04_Knowledge/` or `05_Obsidian/Vault/` |
| agent-facing summary | `09_Exports/agent_context_packs/` |

## Purification principle

不要把聊天流水直接当记忆。先提炼、分类、去重、加来源，再写入长期层。

Raw conversation 和 purified memory 同时保留：raw 用于溯源和重新提炼，purified 用于检索、上下文注入和跨 Agent 共享。
