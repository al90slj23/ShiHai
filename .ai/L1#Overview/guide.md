# ShiHai / 识海 项目指南

> **定位**：面向数字自我的开放个人记忆框架  
> **核心隐喻**：识海，即意识与记忆之海  
> **版本**：v0.1.0  
> **最后更新**：2026-05-26

---

## 1. 项目定位

ShiHai 是一个 Agent-neutral 的个人数字记忆框架。它不属于 Hermes、OpenClaw、Obsidian、mem0、Graphiti 或任何单一平台。所有 Agent、数据库、索引和笔记软件都只是 ShiHai 的客户端或可替换组件。

核心结构：

```text
ShiHai/                  # 通用框架、协议、规范、模板、工具
└── selves/<SelfName>/   # 具体数字自我实例
```

当前实例：

```text
selves/LikeHeng/
```

**LikeHeng 是 ShiHai 的第一个原型实验 self / reference self / dogfood instance。** ShiHai 的框架规范不是脱离真实使用闭门设计，而是在 LikeHeng 的个人数字记忆建设过程中持续验证、迭代和抽象：录音、聊天、人物关系、Agent 协作、Obsidian、人类复盘、隐私边界、备份迁移等真实场景都优先在 LikeHeng 中试验，再将稳定部分沉淀为通用 schema、protocol、workflow、template 和 agent adapter。

该实例包含 LikeHeng 的原始经历、处理文本、结构化记忆、知识档案、Obsidian、人际关系、偏好、决策和 Agent 上下文。私有 self 数据默认不进入开源仓库。

---

## 2. 零容忍规则

1. **Agent 是客户端，不是记忆所有者**：Hermes 和 OpenClaw 只能通过 ShiHai 协议读写记忆。
2. **原始证据不可覆盖**：`01_Raw/` 只追加，不破坏来源。
3. **AI 总结必须可溯源**：所有摘要、断言、关系判断必须有 `source_ref` 或证据事件。
4. **敏感记忆先进入 review queue**：身份、关系、价值观、健康、财务、第三方敏感推断不得直接固化。
5. **索引可重建**：向量库、图谱库、全文索引不是唯一真相源。
6. **开源仓库不得上传个人实例数据**：`selves/LikeHeng/` 默认 gitignored。
7. **文件夹物理命名遵守六层 `.ai/L#English/` 格式**。

---

## 3. 通用目录结构

```text
ShiHai/
├── .ai/          # AI 记忆与项目规范，六层架构
├── agents/       # Hermes/OpenClaw/MCP 等通用适配规则
├── docs/         # 项目文档
├── protocols/    # File/MCP/HTTP 协议草案
├── schemas/      # Canonical memory JSON schemas
├── templates/    # 模板
├── tools/        # 工具脚本
├── workflows/    # 通用工作流
├── examples/     # 安全示例
└── selves/       # 私有数字自我实例集合
```

---

## 4. LikeHeng self 目录

```text
selves/LikeHeng/
├── 00_Inbox/       # 未处理输入
├── 01_Raw/         # 原始证据
├── 02_Processed/   # 转写/OCR/摘要
├── 03_Canonical/   # events/entities/relations/claims/review_queue
├── 04_Knowledge/   # 人物、项目、身份、时间线等加工知识
├── 05_Obsidian/    # 人类可读 vault
├── 06_Index/       # 可重建索引
├── 07_Agents/      # Hermes/OpenClaw 个性化上下文
├── 08_Workflows/   # self 级工作流
├── 09_Exports/     # 上下文包和导出
├── 10_Backups/     # 快照/校验
├── 90_Archive/     # 冷归档
├── _identity/      # 基础人类信息
└── _system/        # logs/manifests/config
```

---

## 5. Agent 兼容原则

ShiHai 第一阶段主要兼容：

- Hermes：`.h`
- OpenClaw：`.c`

兼容层级：

1. File protocol：所有 Agent 都能读写的最低层协议。
2. MCP protocol：优先的工具接口，未来提供 `shihai_search_memory`、`shihai_propose_memory` 等工具。
3. Context packs：兼容不支持 MCP 的 Agent。
4. HTTP API：第二阶段中台接口。

所有 Agent 必须遵守 `agents/common/agent_contract.md`。

---

## 6. AI 读取顺序

```text
.ai/L1#Overview/guide.md
  → .ai/L2#Index/toc.md
  → 按需读取 .ai/L3#Standards/standards/*.md
  → 需要背景时读取 .ai/L5#Knowledge/
  → 需要历史时读取 .ai/L4#Changelog/
```

L3 是当前规范唯一主版本，L2 只做导航。
