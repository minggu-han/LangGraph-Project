from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime

class State(TypedDict):
    result: str

class MyContext(TypedDict):
    user_id: str  # 运行时传入的配置

def my_node(state: State, runtime: Runtime[MyContext]):
    # 从 runtime 中读取上下文，如 user_id
    user = runtime.context.get("user_id", "Guest")
    return {"result": f"Processed for user: {user}"}

# 构建图，并指定 context_schema
builder = StateGraph(state_schema=State, context_schema=MyContext)
builder.add_node("my_node", my_node)
builder.add_edge(START, "my_node")
builder.add_edge("my_node", END)
graph = builder.compile()

# 在 invoke 时通过 context 参数传入
result = graph.invoke({"result": ""}, context={"user_id": "alice_123"})
print(result)
# 输出: {'result': 'Processed for user: alice_123'}