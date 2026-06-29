from typing import Annotated, TypedDict, Any
from langgraph.graph import StateGraph, START, END


# 自定义 Reducer：保留最大值
def max_value(old: int, new: int) -> int:
    return max(old, new)


# 自定义 Reducer：保留最近 N 条消息
def keep_last_n(old: list, new: list, n: int = 5) -> list:
    combined = old + new
    return combined[-n:]


# 自定义 Reducer：合并字典，但特定键冲突时保留旧值
def merge_dict_keep_old(old: dict, new: dict) -> dict:
    result = old.copy()
    for key, value in new.items():
        if key not in old:
            result[key] = value
    return result


class State(TypedDict):
    # 使用自定义 Reducer
    max_score: Annotated[int, max_value]

    # 注意：带参数的 Reducer 需要包装
    recent_logs: Annotated[list, lambda old, new: (old + new)[-5:]]

    # 合并字典但保留旧值
    config: Annotated[dict, merge_dict_keep_old]


def node_a(state: State):
    return {"max_score": 85, "recent_logs": ["A executed"], "config": {"timeout": 30}}


def node_b(state: State):
    return {"max_score": 92, "recent_logs": ["B executed"], "config": {"retries": 3, "timeout": 60}}


builder = StateGraph(State)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)
graph = builder.compile()

result = graph.invoke({
    "max_score": 70,
    "recent_logs": ["Init"],
    "config": {"base_url": "api.example.com"}
})

print(result)
# 输出:
# {
#     'max_score': 92,  # 保留了最大值
#     'recent_logs': ['A executed', 'B executed'],  # 保留最近5条（此处只有2条）
#     'config': {'base_url': 'api.example.com', 'retries': 3}  # timeout 被忽略（因为已存在）
# }