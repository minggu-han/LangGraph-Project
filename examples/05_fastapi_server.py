"""
示例 5：LangGraph + FastAPI 服务器

核心概念：
- 将 LangGraph 图封装为 HTTP API
- 使用 FastAPI + uvicorn 提供服务
- 支持 streaming（流式输出）和非 streaming 两种模式

启动方式：
    uv run uvicorn examples.05_fastapi_server:app --reload --port 8000

    # 或者直接用 python
    # python examples/05_fastapi_server.py

API 端点：
    POST /chat          — 非流式对话
    POST /chat/stream   — 流式对话
    GET  /health        — 健康检查

测试：
    curl -X POST http://localhost:8000/chat \
      -H "Content-Type: application/json" \
      -d '{"message": "你好！请用中文介绍你自己"}'

    curl -X POST http://localhost:8000/chat/stream \
      -H "Content-Type: application/json" \
      -d '{"message": "1+1等于几？"}'
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import TypedDict
from pydantic import BaseModel

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

from src.config import get_model


# ============================================================
# 1. 构建 LangGraph 图
# ============================================================

class ChatState(TypedDict):
    messages: list


llm = get_model(temperature=0.7)


def chat_node(state: ChatState) -> dict:
    """对话节点：调用 LLM"""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


builder = StateGraph(ChatState)
builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

graph = builder.compile()
# 将生成的图片保存到文件
graph_png = graph.get_graph().draw_mermaid_png()
with open("05_fastapi_server.png", "wb") as f:
    f.write(graph_png)


# ============================================================
# 2. FastAPI 应用
# ============================================================

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
import asyncio

app = FastAPI(
    title="LangGraph Chat API",
    description="基于 LangGraph 和 OpenAI 的对话 API",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "langgraph-chat"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    非流式对话：一次性返回完整回复。

    LangGraph 的 invoke 会同步运行整个图，返回最终 State。
    """
    result = graph.invoke({"messages": [HumanMessage(content=req.message)]})
    last_message = result["messages"][-1]
    reply = last_message.content if isinstance(last_message, AIMessage) else str(last_message)
    return ChatResponse(reply=reply)


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    流式对话：使用 Server-Sent Events (SSE) 逐 token 返回。

    LangGraph 的 astream_events 可以监听图内的事件。
    这里用 LLM 的 streaming 能力逐 token 输出。
    """

    async def generate():
        messages = [HumanMessage(content=req.message)]

        # 使用 astream_events 获取流式事件
        async for event in graph.astream_events(
            {"messages": messages},
            version="v2",
        ):
            kind = event["event"]
            # 只处理聊天模型生成的 token 流
            if kind == "on_chat_model_stream":
                token = event["data"]["chunk"].content
                if token:
                    yield f"data: {json.dumps({'token': token})}\n\n"

        # 发送结束信号
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ============================================================
# 3. 作为模块被 uvicorn 加载时直接使用上面的 app
#    直接运行本文件时启动 uvicorn
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
