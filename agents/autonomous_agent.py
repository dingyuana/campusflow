"""
Day 14: 自主智能体 Deep Agents

实现端到端自动报到流程：
规划 → 执行 → 观察 → 反思
"""

from typing import List, Dict, Any, TypedDict
from langgraph.graph import StateGraph, START, END


class AutonomousState(TypedDict):
    """自主智能体状态"""
    student_id: str
    goal: str
    plan: List[str]
    current_step: int
    completed_steps: List[str]
    failed_steps: List[str]
    final_result: str


def planning_node(state: AutonomousState) -> AutonomousState:
    """
    规划节点
    
    将目标拆解为执行计划
    """
    goal = state["goal"]
    
    # 自动生成计划
    if "报到" in goal or "入学" in goal:
        state["plan"] = [
            "验证身份",
            "检查缴费状态",
            "分配宿舍",
            "办理校园卡",
            "完成报到"
        ]
    else:
        state["plan"] = ["分析需求", "执行任务", "验证结果"]
    
    state["current_step"] = 0
    print(f"📝 生成计划: {state['plan']}")
    
    return state


def execution_node(state: AutonomousState) -> AutonomousState:
    """
    执行节点
    
    执行当前步骤
    """
    if state["current_step"] >= len(state["plan"]):
        return state
    
    step = state["plan"][state["current_step"]]
    print(f"🔧 执行步骤: {step}")
    
    # 模拟执行
    import random
    if random.random() > 0.2:  # 80% 成功率
        state["completed_steps"].append(step)
        print(f"   ✅ 步骤完成: {step}")
    else:
        state["failed_steps"].append(step)
        print(f"   ❌ 步骤失败: {step}")
    
    state["current_step"] += 1
    
    return state


def reflection_node(state: AutonomousState) -> AutonomousState:
    """
    反思节点
    
    检查执行结果，决定是否重试
    """
    if state["failed_steps"] and len(state["failed_steps"]) <= 3:
        # 重试失败的步骤
        print(f"🤔 反思: 发现 {len(state['failed_steps'])} 个失败步骤，尝试重试")
        state["plan"] = state["failed_steps"] + state["plan"][state["current_step"]:]
        state["current_step"] = 0
        state["failed_steps"] = []
    
    return state


def build_autonomous_agent():
    """构建自主智能体"""
    workflow = StateGraph(AutonomousState)
    
    workflow.add_node("plan", planning_node)
    workflow.add_node("execute", execution_node)
    workflow.add_node("reflect", reflection_node)
    
    workflow.add_edge(START, "plan")
    workflow.add_edge("plan", "execute")
    
    # 循环直到完成
    workflow.add_conditional_edges(
        "execute",
        lambda s: "done" if s["current_step"] >= len(s["plan"]) else "continue",
        {"continue": "execute", "done": "reflect"}
    )
    
    workflow.add_edge("reflect", END)
    
    return workflow.compile()
