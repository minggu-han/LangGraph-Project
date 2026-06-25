"""
示例 3：带工具的聊天机器人（ReAct Agent 模式）

核心概念：
- Tool：给 LLM 绑定的工具函数，LLM 可以"调用"它们
- Agent：LLM + 工具 = 能自主决策和行动的 Agent
- ReAct 模式：思考(Reasoning) → 行动(Action) → 观察(Observation) → 循环

这个例子展示一个完整的 Agent 循环：
    START → agent（调用 LLM） → 需要工具? → tools → agent → ... → END

需要设置环境变量 OPENAI_API_KEY：
    export OPENAI_API_KEY=sk-your-key
    # 或创建 .env 文件写入 OPENAI_API_KEY=sk-your-key

运行方式：
    python examples/03_chatbot_with_tools.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import TypedDict, Literal, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

from src.config import get_model


# ============================================================
# 1. 定义工具
# ============================================================
# 使用 @tool 装饰器定义工具。LLM 会自动理解参数并决定何时调用。

@tool
def add(a: float, b: float) -> float:
    """将两个数字相加。用于任何加法计算。"""
    return a + b


@tool
def multiply(a: float, b: float) -> float:
    """将两个数字相乘。用于任何乘法计算。"""
    return a * b


@tool
def get_current_temperature(city: str) -> str:
    """获取指定城市的当前温度（模拟数据）。"""
    # 模拟数据
    temps = {
        "北京": "32°C，晴朗 ☀️",
        "上海": "28°C，多云 ⛅",
        "东京": "25°C，小雨 🌧️",
        "纽约": "22°C，晴 ☀️",
    }
    return temps.get(city, f"暂无 {city} 的温度数据，默认 20°C")


# 工具列表
tools = [add, multiply, get_current_temperature]

# ============================================================
# 2. 定义 State
# ============================================================
class AgentState(TypedDict):
    # 🔑 add_messages reducer：新消息会追加到列表，而不是覆盖
    # 这样 LLM 在每一轮都能看到完整的对话历史
    messages: Annotated[list, add_messages]


# ============================================================
# 3. 定义节点
# ============================================================

# 获取 LLM 实例
llm = get_model().bind_tools(tools)


def agent_node(state: AgentState) -> dict:
    """Agent 节点：调用 LLM，LLM 决定是回复文本还是调用工具"""
    print(f"\n🤖 [Agent] 当前对话共 {len(state['messages'])} 条消息")
    response = llm.invoke(state["messages"])
    if response.content:
        print(f"🤖 [Agent] 文本回复: {response.content[:150]}...")
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tc in response.tool_calls:
            print(f"  🔧 调用了工具: {tc['name']}({tc.get('args', {})})")
    return {"messages": [response]}


# ToolNode 是 LangGraph 内置的节点，自动执行工具调用
tool_node = ToolNode(tools)


# 条件函数：判断 LLM 返回的是普通消息还是工具调用
def should_continue(state: AgentState) -> Literal["tools", END]:
    """检查最后一条 AI 消息是否有 tool_calls"""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# ============================================================
# 4. 构建图
# ============================================================
builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges(
    source="agent",
    path=should_continue,
    path_map={"tools": "tools", END: END},
)
builder.add_edge("tools", "agent")  # 工具执行完，回到 agent 继续

graph = builder.compile()


# ============================================================
# 5. 运行
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("LangGraph Agent 示例：带工具的聊天机器人")
    print("=" * 60)

    # 试试问一个问题，让 LLM 自动调用工具
    questions = [
        # "北京现在多少度？",
        "先计算 23 乘以 4，然后把结果加上 100",
    ]

    for q in questions:
        print(f"\n{'─' * 60}")
        print(f"👤 用户: {q}")
        print("─" * 60)

        result = graph.invoke({"messages": [HumanMessage(content=q)]})

        # 打印完整对话链
        print(f"\n{'─' * 40}")
        print("📋 完整对话链：")
        for i, msg in enumerate(result["messages"]):
            role = type(msg).__name__
            if isinstance(msg, HumanMessage):
                print(f"  [{i}] 👤 Human: {msg.content}")
            elif isinstance(msg, AIMessage):
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    tools_info = ", ".join(tc["name"] for tc in msg.tool_calls)
                    print(f"  [{i}] 🤖 AI → 调用工具: {tools_info}")
                elif msg.content:
                    print(f"  [{i}] 🤖 AI: {msg.content}")
            elif isinstance(msg, ToolMessage):
                print(f"  [{i}] 🔧 Tool({msg.name}): {msg.content}")
