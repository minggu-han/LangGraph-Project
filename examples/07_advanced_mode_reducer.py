from typing import Annotated, TypedDict
from functools import partial
from langgraph.graph import StateGraph, START, END

# 创建一个带状态的计数器 Reducer
def counter_reducer(old: int, new: int, increment: int = 1) -> int:
    # new 被忽略，每次自动增加
    return old + increment

class State(TypedDict):
    # 每次更新自动 +1
    visit_count: Annotated[int, partial(counter_reducer, increment=1)]

def node(state: State):
    # 返回任何值都会被忽略，计数器自动增加
    return {"visit_count": 0}  # 实际不会设为0，而是 old + 1

builder = StateGraph(State)
builder.add_node("node", node)
builder.add_edge(START, "node")
builder.add_edge("node", END)
graph = builder.compile()

result = graph.invoke({"visit_count": 10})
print(result)  # {'visit_count': 11}