from typing import Annotated, TypedDict
from operator import add, or_
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    # 使用 operator.add 拼接列表
    messages: Annotated[list, add]

    # 使用 operator.or_ 合并字典（Python 3.9+）
    metadata: Annotated[dict, or_]

    # 无 Reducer → 默认覆盖
    current_step: str


def node1(state: State):
    return {
        "messages": ["Hello"],
        "metadata": {"user": "Alice"},
        "current_step": "Step 1"
    }


def node2(state: State):
    return {
        "messages": ["World"],
        "metadata": {"role": "admin"},
        "current_step": "Step 2"
    }


builder = StateGraph(State)
builder.add_node("node1", node1)
builder.add_node("node2", node2)
builder.add_edge(START, "node1")
builder.add_edge("node1", "node2")
builder.add_edge("node2", END)
graph = builder.compile()

result = graph.invoke({
    "messages": ["Start"],
    "metadata": {"session": "123"},
    "current_step": "Init"
})

print(result)
# 输出:
# {
#     'messages': ['Start', 'Hello', 'World'],          # add 拼接
#     'metadata': {'session': '123', 'user': 'Alice', 'role': 'admin'},  # or_ 合并
#     'current_step': 'Step 2'                          # 覆盖
# }