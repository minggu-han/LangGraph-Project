"""
示例 1：最基础的 LangGraph 图

核心概念：
- State：图的状态，节点之间传递的数据
- Node：图的节点，处理逻辑
- Edge：图的边，连接节点
- Graph：组合节点、边和状态

这个例子展示了一个最简单的图：
    START → node_a → node_b → END

运行方式：
    python examples/01_basic_graph.py
"""

import sys
from pathlib import Path

# 把项目根目录加到 sys.path，方便 import src
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# ============================================================
# 1. 定义 State（状态）
# ============================================================
# State 是图中各个节点之间传递的"共享数据"。
# 每个节点可以读取 State，也可以更新 State。
class MyState(TypedDict):
    messages: list[str]
    counter: int


# ============================================================
# 2. 定义 Node（节点函数）
# ============================================================
# 每个节点就是一个普通的 Python 函数。
# 输入是当前 State，返回的是要更新的字段（部分 State）。

def node_a(state: MyState) -> dict:
    """节点 A：打印当前状态，追加一条消息，计数器 +1"""
    print(f"[Node A] 进入时的状态: {state}")
    return {
        "messages": state["messages"] + ["来自 Node A 的问候 👋"],
        "counter": state["counter"] + 1,
    }


def node_b(state: MyState) -> dict:
    """节点 B：打印当前状态，追加一条消息，计数器 +1"""
    print(f"[Node B] 进入时的状态: {state}")
    return {
        "messages": state["messages"] + ["来自 Node B 的问候 🎉"],
        "counter": state["counter"] + 1,
    }


# ============================================================
# 3. 构建 Graph（图）
# ============================================================
builder = StateGraph(MyState)

# 添加节点
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

# 添加边：START → node_a → node_b → END
builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)

# 编译图（将 builder "编译"成可运行的图）
graph = builder.compile()


# ============================================================
# 4. 运行 Graph
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("LangGraph 基础示例：START → node_a → node_b → END")
    print("=" * 60)

    # invoke：同步运行图，传入初始状态，返回最终状态
    result = graph.invoke({"messages": [], "counter": 0})

    print("\n" + "=" * 60)
    print("最终结果:")
    print("=" * 60)
    for msg in result["messages"]:
        print(f"  📝 {msg}")
    print(f"  🔢 counter = {result['counter']}")
