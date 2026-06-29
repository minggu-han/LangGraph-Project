"""
示例 4：人在回路（Human-in-the-Loop）

核心概念：
- interrupt：在关键节点暂停，等待人工审批
- Command：恢复执行时传入人工决定
- checkpoint：LangGraph 自动保存状态，暂停后可从中断点恢复

这个例子展示：
    START → analyze → [需要审批? 暂停等待人工] → execute → END

运行方式：
    python examples/04_human_in_the_loop.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command


class TaskState(TypedDict):
    task: str
    risk_level: str
    approved: bool
    result: str


def analyze(state: TaskState) -> dict:
    """分析任务风险等级"""
    task = state["task"]
    # 模拟风险分析
    if "删除" in task or "delete" in task.lower():
        risk = "high"
    elif "修改" in task:
        risk = "medium"
    else:
        risk = "low"

    print(f"📊 [分析] 任务: '{task}' → 风险等级: {risk}")
    return {"risk_level": risk}


def human_approval(state: TaskState) -> dict:
    """需要人工审批：使用 interrupt 暂停图执行"""
    if state["risk_level"] in ("high", "medium"):
        print(f"⏸️  [审批暂停] 风险等级 {state['risk_level']}，需要人工审批！")
        print(f"    任务内容: {state['task']}")

        # 🔑 interrupt：暂停图执行，返回提示信息给调用者
        decision = interrupt(f"请审批任务: {state['task']} (风险: {state['risk_level']})")

        # 当用户恢复执行时，decision 就是用户传入的值
        print(f"✅ [审批通过] 人工决定: {decision}")
        return {"approved": True}
    else:
        # 低风险自动通过
        print(f"✅ [自动通过] 风险等级 {state['risk_level']}，无需审批")
        return {"approved": True}


def execute(state: TaskState) -> dict:
    """执行任务"""
    print(f"🚀 [执行] 执行任务: {state['task']}")
    return {"result": f"任务 '{state['task']}' 已完成！"}


# ---- 构建图 ----
builder = StateGraph(TaskState)

builder.add_node("analyze", analyze)
builder.add_node("human_approval", human_approval)
builder.add_node("execute", execute)

builder.add_edge(START, "analyze")
builder.add_edge("analyze", "human_approval")
builder.add_edge("human_approval", "execute")
builder.add_edge("execute", END)

# 🔑 使用 MemorySaver 作为 checkpoint 存储（持久化状态，支持中断恢复）
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)


# ---- 运行 ----
if __name__ == "__main__":
    print("=" * 60)
    print("LangGraph Human-in-the-Loop 示例")
    print("=" * 60)

    # 配置：thread_id 用于标识一次"对话"，checkpoint 按 thread 存储
    config = {"configurable": {"thread_id": "demo-1"}}

    # ---- 第一步：触发中断 ----
    task = "删除所有用户数据"
    print(f"\n👤 提交任务: {task}\n")

    # invoke 会运行到 interrupt 处，然后暂停
    result = graph.invoke(
        {"task": task, "risk_level": "", "approved": False, "result": ""},
        config=config,
    )

    print(f"\n⚠️  图已暂停，等待审批...")
    print(f"当前状态: approved={result.get('approved')}, risk_level={result['risk_level']}")

    # ---- 第二步：恢复执行 ----
    print(f"\n{'─' * 40}")
    print("👤 人工审批: 批准执行")
    print("─" * 40)

    # 使用 Command(resume=...) 恢复执行，传入审批决定
    result = graph.invoke(
        Command(resume="批准：此操作已确认安全"),
        config=config,
    )

    print(f"\n🎉 最终结果: {result['result']}")
    # 将生成的图片保存到文件
    graph_png = graph.get_graph().draw_mermaid_png()
    with open("04_human_in_the_loop.png", "wb") as f:
        f.write(graph_png)
