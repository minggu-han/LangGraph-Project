from typing import Annotated, TypedDict, Union, Any
from datetime import datetime
from langgraph.graph import StateGraph, START, END


def smart_reducer(old: Any, new: Any) -> Any:
    """根据数据类型智能选择合并策略"""
    # 列表 → 拼接
    if isinstance(old, list) and isinstance(new, list):
        return old + new

    # 字典 → 递归合并
    if isinstance(old, dict) and isinstance(new, dict):
        merged = old.copy()
        for k, v in new.items():
            if k in old and isinstance(old[k], dict) and isinstance(v, dict):
                merged[k] = smart_reducer(old[k], v)
            else:
                merged[k] = v
        return merged

    # 数字 → 取最大值
    if isinstance(old, (int, float)) and isinstance(new, (int, float)):
        return max(old, new)

    # 其他 → 覆盖
    return new


class State(TypedDict):
    data: Annotated[Any, smart_reducer]


def node1(state: State):
    return {"data": {"user": {"name": "Alice", "score": 80}}}


def node2(state: State):
    return {"data": {"user": {"score": 95, "level": 2}, "timestamp": datetime.now()}}


builder = StateGraph(State)
builder.add_node("node1", node1)
builder.add_node("node2", node2)
builder.add_edge(START, "node1")
builder.add_edge("node1", "node2")
builder.add_edge("node2", END)
graph = builder.compile()

result = graph.invoke({"data": {"session": "abc"}})
print(result)
# {
#     'data': {
#         'session': 'abc',
#         'user': {'name': 'Alice', 'score': 95, 'level': 2},  # score 取最大值
#         'timestamp': datetime(...)
#     }
# }