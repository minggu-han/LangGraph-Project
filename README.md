# LangGraph 学习项目 🦜🕸️

从零开始学习 [LangGraph](https://langchain-ai.github.io/langgraph/) — LLM Agent 编排框架。

## 项目结构

```
LangGraph-Study/
├── src/
│   └── config.py              # 统一配置：模型、API Key
├── examples/                   # 渐进式学习示例
│   ├── 01_basic_graph.py       # 基础图：节点、边、状态
│   ├── 02_conditional_edges.py # 条件边：动态路由
│   ├── 03_chatbot_with_tools.py# Agent：LLM + 工具调用
│   ├── 04_human_in_the_loop.py # 人在回路：中断与审批
│   └── 05_fastapi_server.py    # FastAPI 集成：HTTP API
├── pyproject.toml
└── .env.example
```

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 安装 dev 依赖（需要运行测试时）
uv sync --group dev
```

### 2. 配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入你的 OpenAI API Key
# OPENAI_API_KEY=sk-your-key-here
#
# 如果你用 DeepSeek 等兼容服务，也可以设置：
# OPENAI_API_BASE=https://api.deepseek.com/v1
```

### 3. 运行示例

```bash
# 示例 1：最基础的图（不需要 API Key）
uv run python examples/01_basic_graph.py

# 示例 2：条件路由（不需要 API Key）
uv run python examples/02_conditional_edges.py

# 示例 3：Agent + 工具调用（需要 API Key）
uv run python examples/03_chatbot_with_tools.py

# 示例 4：人在回路（不需要 API Key）
uv run python examples/04_human_in_the_loop.py

# 示例 5：FastAPI 服务器（需要 API Key）
uv run uvicorn examples.05_fastapi_server:app --reload --port 8000
```

## 学习路线

| 步骤 | 示例 | 核心概念 |
|------|------|----------|
| 1 | `01_basic_graph.py` | State, Node, Edge, Graph — 图的基本元素 |
| 2 | `02_conditional_edges.py` | 条件边 — 根据状态动态路由 |
| 3 | `03_chatbot_with_tools.py` | Tool, Agent, ReAct 模式 — LLM 自主决策 |
| 4 | `04_human_in_the_loop.py` | interrupt, Command, checkpoint — 人工审批 |
| 5 | `05_fastapi_server.py` | FastAPI 集成, SSE 流式输出 |

## LangGraph 核心概念速览

```
┌──────────────────────────────────────────────┐
│                  LangGraph                    │
│                                              │
│   State  ◄── 图的状态，节点间共享数据          │
│   Node   ◄── 处理函数，输入 State 返回部分 State │
│   Edge   ◄── 连接节点的边                      │
│     ├── 普通边：固定连接 A → B                 │
│     └── 条件边：根据 State 动态选择下一节点      │
│   Graph  ◄── State + Nodes + Edges            │
│                                              │
│   高级特性：                                   │
│   ├── Checkpoint：状态持久化，支持中断恢复       │
│   ├── interrupt：暂停执行，等待人工输入          │
│   ├── Stream：流式输出（SSE / token-by-token）  │
│   └── Subgraph：图的嵌套与复用                  │
└──────────────────────────────────────────────┘
```

## 常用命令

```bash
# 运行所有不需要 API Key 的示例
uv run python examples/01_basic_graph.py
uv run python examples/02_conditional_edges.py
uv run python examples/04_human_in_the_loop.py

# 启动 FastAPI 开发服务器
uv run uvicorn examples.05_fastapi_server:app --reload --port 8000

# 测试 API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好！"}'
```
