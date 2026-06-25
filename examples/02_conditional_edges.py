"""
示例 2：条件边（Conditional Edges）

核心概念：
- 条件边允许根据当前 State 动态决定下一步走哪个节点
- 这是实现 Agent 路由/分支逻辑的基础

这个例子展示：
    START → router → 分支A / 分支B → combiner → END

运行方式：
    python examples/02_conditional_edges.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END


class MyState(TypedDict):
    value: int
    path: str
    log: list[str]


# ---- 节点函数 ----

def router(state: MyState) -> dict:
    """路由节点：判断 value 的奇偶性，决定走哪条路"""
    parity = "even" if state["value"] % 2 == 0 else "odd"
    return {"path": parity, "log": state["log"] + [f"Router: value={state['value']} → {parity}"]}


# 条件函数：返回下一个要去的节点名称
def decide_path(state: MyState) -> Literal["even_handler", "odd_handler"]:
    """根据 path 字段决定走哪个节点"""
    if state["path"] == "even":
        return "even_handler"
    return "odd_handler"


def even_handler(state: MyState) -> dict:
    """处理偶数"""
    return {
        "value": state["value"] * 2,
        "log": state["log"] + [f"Even handler: {state['value']} → {state['value'] * 2}"],
    }


def odd_handler(state: MyState) -> dict:
    """处理奇数"""
    return {
        "value": state["value"] + 1,
        "log": state["log"] + [f"Odd handler: {state['value']} → {state['value'] + 1}"],
    }


def combiner(state: MyState) -> dict:
    """合并节点：两条路在这里汇合"""
    return {
        "log": state["log"] + [f"Combiner: 最终 value = {state['value']}"],
    }


# ---- 构建图 ----

builder = StateGraph(MyState)

builder.add_node("router", router)
builder.add_node("even_handler", even_handler)
builder.add_node("odd_handler", odd_handler)
builder.add_node("combiner", combiner)

builder.add_edge(START, "router")

# 🔑 关键：条件边 — 根据 decide_path 的返回值选择下一个节点
builder.add_conditional_edges(
    source="router",           # 从哪个节点出发
    path=decide_path,           # 条件函数
    path_map={                 # 条件函数返回值 → 目标节点
        "even_handler": "even_handler",
        "odd_handler": "odd_handler",
    },
)

# 两个分支都汇入 combiner
builder.add_edge("even_handler", "combiner")
builder.add_edge("odd_handler", "combiner")
builder.add_edge("combiner", END)

graph = builder.compile()


# ---- 运行 ----
if __name__ == "__main__":
    for test_value in [4, 7]:
        print(f"\n{'=' * 60}")
        print(f"测试 value = {test_value}")
        print("=" * 60)
        result = graph.invoke({"value": test_value, "path": "", "log": []})
        for line in result["log"]:
            print(f"  {line}")
