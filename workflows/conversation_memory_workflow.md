# Conversation-first Memory Workflow

> 通用工作流：把用户与 Agent 的持续交流沉淀为长期个人记忆。

## 适用场景

当一个 self 主要通过与 Agent 交流来建立记忆，而不是优先通过录音、文件或外部导入时，使用本工作流。

## Pipeline

```text
conversation
  → session summary
  → extracted insights
  → memory classification
  → review queue or canonical write
  → knowledge note update
  → agent context pack refresh
```

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
