# ShiHai / 识海

> **识海**：面向数字自我的开放个人记忆框架。  
> 它不是一个笔记软件，也不是某个 Agent 的附属记忆；它试图成为一个人长期数字化存在的底层记忆工程。

> **ShiHai** — *The ocean of consciousness and memory for digital selves.*  
> An open personal memory substrate that helps AI agents remember a person across time, tools, devices, and models.

---

## English positioning

**ShiHai** is pronounced roughly as **“shih-high”**. It comes from the Chinese word **识海**, literally meaning **“the ocean of consciousness / the sea of knowing.”**

In Chinese, **识** means consciousness, cognition, awareness, memory, and knowing. **海** means ocean. Together, **识海** points to a deep inner ocean where experiences, relationships, knowledge, emotions, decisions, and identity traces are accumulated.

ShiHai is not just a knowledge base. It is a proposed **personal memory substrate** for digital selves:

> **Not a notes app. Not an agent memory plugin. Not a vector database.  
> ShiHai is the long-term memory layer beneath all of them.**

### Suggested slogans

- **ShiHai — The memory ocean for your digital self.**
- **ShiHai — Open memory infrastructure for digital selves.**
- **ShiHai — A personal memory substrate for humans and agents.**
- **ShiHai — Where your digital self begins to remember.**
- **ShiHai — Own your memory. Grow your digital self.**

### One-line description

> **ShiHai is an open, local-first personal memory framework for building digital selves that can be remembered, searched, reasoned over, and shared safely across AI agents.**

---

## 一、项目简介

**ShiHai / 识海** 是一个面向“数字自我（Digital Self）”的个人记忆基础设施项目。

它的目标不是简单保存笔记、文件或聊天记录，而是构建一套长期、开放、可迁移、可被多种智能体调用的个人数字记忆底座，用来沉淀一个人的：

- 原始经历；
- 录音与转写；
- 聊天与对话；
- 文档、网页、图片、PDF；
- 人际关系；
- 项目与决策；
- 偏好、价值观、长期目标；
- 情绪、反思与成长轨迹；
- 可被未来数字人调用的上下文。

名字“识海”取“意识与记忆之海”之意。它既包含知识，也包含经验；既记录事实，也记录一个人如何变化。

---

## 二、为什么要做 ShiHai

今天的 AI Agent 已经越来越强，但大多数智能体仍然有一个根本问题：

> 它们能临时处理任务，却很难真正长期记住一个人。

当前常见方案各有局限：

- 聊天历史是流水账，很难成为结构化记忆；
- Obsidian、Notion 等笔记工具适合人读，但不是天然的 Agent 记忆底座；
- 向量库适合语义检索，但不是记忆本体；
- 图谱适合理解关系，但不应该成为唯一真相源；
- 各个 Agent 自己的 Memory 容易割裂，Hermes 记一套，OpenClaw 记一套，Claude/Codex 又各记一套；
- 平台私有格式容易造成数据锁定，未来迁移困难。

ShiHai 的立项原因就是：

> 我们需要一个不属于任何单一平台、单一模型、单一 Agent 的个人数字记忆底座。

它应该像一个“记忆操作层”一样，站在所有应用和智能体的下面。

Hermes、OpenClaw、Claude、Codex、Obsidian、mem0、Graphiti、向量数据库、知识图谱、未来的数字人应用，都只是它的客户端或可替换组件。

---

## 三、核心理念

### 1. 个人数据主权

原始数据必须归属于个人，而不是归属于某个 App、某个 Agent 或某个云平台。

ShiHai 优先使用开放格式：

- Markdown
- YAML
- JSON / JSONL
- SQLite / Parquet 导出
- 普通文件夹结构

这样即使未来工具全部换掉，个人记忆仍然可以迁移、重建和继续生长。

### 2. 原始证据与 AI 总结分离

AI 摘要可能出错，原始数据才是证据。

因此 ShiHai 区分：

```text
01_Raw/         原始证据
02_Processed/   转写、OCR、摘要等处理结果
03_Canonical/   标准结构化记忆
04_Knowledge/   加工后的知识与画像
```

任何重要的 AI 记忆都应该能追溯到来源。

### 3. Agent-neutral

ShiHai 不属于 Hermes，也不属于 OpenClaw。

它的设计目标是：

```text
ShiHai = 记忆底座
Hermes / OpenClaw / Claude / Codex / 其他 Agent = 客户端
```

不同智能体应该通过统一协议访问同一个个人记忆，而不是各自维护一份互相冲突的记忆。

### 4. 可审查、可修正、可回滚

数字记忆不能让 AI 随意写死。

对于敏感或身份塑造型内容，例如：

- 人际关系判断；
- 价值观总结；
- 长期目标；
- 健康、财务、法律相关结论；
- 对第三方的推断；

应该先进入 review queue，由用户或可信流程确认后，再进入正式记忆。

### 5. 索引不是记忆本体

向量库、知识图谱、全文索引都很重要，但它们只是检索和推理层。

ShiHai 的真相源应该是：

```text
原始文件 + 处理文本 + canonical JSONL + 人类可读 Markdown
```

索引应该可以被删除并重建。

---

## 四、项目结构

ShiHai 分为两层：

```text
ShiHai/                  # 通用框架层
└── selves/<SelfName>/   # 具体数字自我实例
```

当前规划中的个人实例是：

```text
selves/LikeHeng/
```

**LikeHeng 是 ShiHai 的第一个原型实验 self。**  
ShiHai 不是先在抽象中闭门设计完再交给用户使用，而是以 LikeHeng 的真实长期数字记忆建设过程作为第一现场：在录音、聊天、人物关系、项目决策、Agent 协作、Obsidian、人类复盘和隐私边界的真实使用中，不断验证、修正和抽象出可复用的框架规范。

换句话说：

```text
LikeHeng = 原型实验场 / reference self / dogfood instance
ShiHai   = 从 LikeHeng 实践中持续抽象出来的通用框架
```

但该目录默认被 `.gitignore` 忽略，不会上传到开源仓库。未来公开仓库只保留从 LikeHeng 实践中提炼出的通用 schema、protocol、workflow、template、agent adapter 和脱敏 example。

### 通用框架层

```text
ShiHai/
├── .ai/          # AI 记忆与项目规范，六层架构
├── agents/       # Hermes、OpenClaw、MCP 等 Agent 适配规则
├── docs/         # 项目文档
├── protocols/    # File / MCP / HTTP API 协议
├── schemas/      # Canonical memory JSON schemas
├── templates/    # self、人物、事件、复盘等模板
├── tools/        # 导入、处理、导出工具
├── workflows/    # 录音、聊天、文档、复盘等工作流
├── examples/     # 脱敏示例
└── selves/       # 私有数字自我实例集合，默认不提交
```

### 个人 self 实例层

每个 self 是一个具体人的数字记忆实例：

```text
selves/<SelfName>/
├── 00_Inbox/       # 未处理输入
├── 01_Raw/         # 原始证据，录音/聊天/图片/PDF 等
├── 02_Processed/   # 转写、OCR、清洗文本、摘要
├── 03_Canonical/   # events/entities/relations/claims/review_queue
├── 04_Knowledge/   # 人物、项目、关系、身份、时间线等加工知识
├── 05_Obsidian/    # 人类可读 Obsidian Vault
├── 06_Index/       # 可重建的向量/图谱/全文索引
├── 07_Agents/      # Hermes/OpenClaw 等个性化上下文
├── 08_Workflows/   # self 级自动化流程
├── 09_Exports/     # 上下文包、迁移包、脱敏导出
├── 10_Backups/     # 快照与校验
├── 90_Archive/     # 冷归档
├── _identity/      # 基础人类信息、价值观、目标、偏好
└── _system/        # 日志、manifest、本地配置
```

---

## 五、与 Hermes / OpenClaw 的关系

当前 ShiHai 优先考虑兼容：

- **Hermes**：来源标记 `.h`
- **OpenClaw**：来源标记 `.c`

但它们不是 ShiHai 的中心。

当前已经提供两个本地接口层：

```bash
# File Protocol CLI：直接读写 selves/<SelfName>/ 文件
python3 tools/shihai_memory.py --root /path/to/ShiHai get-context --self LikeHeng

# MCP stdio server：给 Hermes / OpenClaw 等 Agent 暴露工具
python3 tools/shihai_mcp_server.py --root /path/to/ShiHai
```

当前 MCP server 暴露的第一批工具：

```text
shihai_get_context
shihai_add_conversation
shihai_add_event
shihai_propose_memory
shihai_list_pending_reviews
shihai_approve_memory
shihai_search_memory
```

未来的理想关系是：

```text
                 ┌──────────────┐
                 │   Hermes     │
                 └──────┬───────┘
                        │ MCP / File / Context Pack
                 ┌──────▼───────┐
                 │    ShiHai     │
                 │ Memory Layer  │
                 └──────▲───────┘
                        │ MCP / File / Context Pack
                 ┌──────┴───────┐
                 │  OpenClaw    │
                 └──────────────┘
```

ShiHai 将提供多种兼容方式：

1. **File Protocol**：最低层、最稳定，任何 Agent 都能读写文件；
2. **MCP Protocol**：面向智能体的标准工具接口；
3. **Context Pack**：为不支持 MCP 的 Agent 生成上下文包；
4. **HTTP API**：未来中台化后提供跨设备、跨服务访问。

---

## 六、`.ai` 六层记忆体系

ShiHai 采用来自 ZERO 的六层 `.ai` 规范，用于让 AI 更好地理解项目。

```text
.ai/
├── L0#Execution/   # 工作执行：specs、hooks、skills、workflows
├── L1#Overview/    # 项目概览：AI 首读入口
├── L2#Index/       # 规范索引：导航和标题大纲
├── L3#Standards/   # 完整规范：当前唯一规范主版本
├── L4#Changelog/   # 操作日志：历史变更和决策过程
└── L5#Knowledge/   # 知识图谱：长期沉淀和语义关系
```

AI 推荐读取顺序：

```text
L1#项目概览 (Overview)
  → L2#规范索引 (Index)
  → 按需读取 L3#完整规范 (Standards)
  → 需要背景时读取 L5#知识图谱 (Knowledge)
  → 需要历史时读取 L4#操作日志 (Changelog)
```

---

## 七、最终形态畅想

ShiHai 的最终形态，不只是一个文件夹模板，也不只是一个开源仓库。

它更像是一个人的数字记忆底座：

### 1. 个人经历自动进入记忆

未来可以接入：

- 随身录音笔；
- 手机语音备忘；
- 微信、Telegram、邮件、会议记录；
- 网页、PDF、图片、截图；
- 项目代码与决策记录；
- 每日、每周、每月复盘。

这些输入会经过：

```text
导入 → 转写/OCR/解析 → 摘要 → 实体识别 → 事件化 → 结构化记忆 → 检索索引 → 周期性复盘
```

### 2. 每个人拥有自己的数字 self

未来一个 ShiHai 框架下可以有多个 self：

```text
selves/
├── LikeHeng/
├── Alice/
├── Bob/
└── ExamplePerson/
```

每个 self 都是一个独立的数字记忆实例，拥有自己的原始证据、身份画像、关系图谱、知识档案和 Agent 上下文。

### 3. 多智能体共享同一个记忆底座

Hermes、OpenClaw、Claude、Codex、ChatGPT、Cursor、手机助手、语音助手，都可以通过 ShiHai 读取同一个人的长期记忆。

这意味着：

> 不是每个 Agent 都重新认识你，而是所有 Agent 都可以在权限允许的范围内访问同一个“你”。

### 4. 数字人从记忆中生长

当一个系统长期记录你的经历、语言、偏好、关系、价值观、决策过程和反思方式时，它就不再只是知识库。

它会成为未来数字人的基础：

- 能记得你说过什么；
- 能理解你长期在意什么；
- 能知道你和谁关系重要；
- 能追溯你为什么做过某个决定；
- 能总结你阶段性的成长；
- 能在不同 Agent 和设备上保持一致的长期上下文。

### 5. 开放、可迁移、可继承

ShiHai 的长期目标不是制造另一个封闭平台，而是定义一套开放的个人记忆工程范式。

理想中，一个人的 ShiHai 记忆可以：

- 本地保存；
- iCloud / NAS / 对象存储 / 备份软件多重备份；
- 被不同 Agent 调用；
- 被不同数据库重建索引；
- 被导出为 Markdown、JSONL、SQLite、Parquet；
- 在十年后仍然可以被新技术重新理解。

---

## 八、当前状态

当前仓库仍处于早期 scaffold 阶段，已经包含：

- 基础 README；
- 项目 manifest；
- `.ai` 六层记忆体系；
- canonical memory JSON schema 草案；
- Hermes / OpenClaw 初步兼容说明；
- File / MCP 协议草案；
- 开源与私有 self 的隔离规则。

当前本地个人实例规划为：

```text
selves/LikeHeng/
```

它是私有目录，默认不会被提交到 GitHub。

---

## 九、开源边界

可以开源：

- 框架文档；
- schema；
- 模板；
- 工具；
- 协议；
- Agent 适配规则；
- 脱敏示例。

不应开源：

- 真实个人录音；
- 聊天记录；
- 人物关系；
- 身份档案；
- 价值观、健康、财务等敏感记忆；
- `selves/LikeHeng/` 下的真实数据。

---

## 十、一句话愿景

> **ShiHai 希望成为每个人拥有自己数字记忆主权的基础设施。**

它不是替你记几条偏好的 Memory，也不是把资料丢进向量库。  
它是一个面向未来数字自我的长期记忆工程：开放、可迁移、可追溯、可被多智能体调用，并能随着一个人的生命经验持续生长。
