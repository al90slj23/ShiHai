# Conversation Memory Protocol

Conversation Memory Protocol 定义 Agent 如何把对话内容沉淀为 ShiHai 记忆。

## Required metadata

```json
{
  "self": "LikeHeng",
  "source_type": "conversation",
  "source_agent": "hermes",
  "source_ref": "session id or transcript path",
  "created_at": "ISO-8601",
  "confidence": 0.9,
  "needs_review": false
}
```

## Write policy

1. 先判断是否有长期价值。
2. 再分类为 event / claim / decision / review item / knowledge note。
3. 敏感推断默认 `needs_review: true`。
4. 所有写入必须能追溯到本次对话或明确来源。
