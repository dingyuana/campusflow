"""
报到流程状态机
Day 4: StateGraph 工作流编排

构建新生报到流程：
Start → Verify Identity → Check Payment → Assign Dorm → Complete
              ↓ (错误3次)        ↓ (未缴费)       ↓ (需审核)
           Manual Review    Payment Guide   Manual Review
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class CheckInState(TypedDict):
    """报到流程状态"""
    student_id: str
    student_name: str
    current_step: str
    messages: Annotated[Sequence[BaseMessage], "add_messages"]
    identity_verified: bool
    payment_completed: bool
    dorm_assigned: bool
    error_count: int
    needs_manual_review: bool


def verify_identity_node(state: CheckInState) -> CheckInState:
    """身份验证节点"""
    print(f"🔍 验证学生身份: {state['student_name']} ({state['student_id']})")
    
    # 模拟身份验证（实际应查询数据库）
    if state['error_count'] >= 3:
        state['needs_manual_review'] = True
        state['messages'].append(AIMessage(
            content="⚠️ 身份验证失败超过3次，已转人工审核"
        ))
    else:
        # 模拟验证成功
        state['identity_verified'] = True
        state['current_step'] = "check_payment"
        state['messages'].append(AIMessage(
            content=f"✅ 身份验证通过: {state['student_name']}"
        ))
    
    return state


def check_payment_node(state: CheckInState) -> CheckInState:
    """缴费检查节点"""
    print(f"💰 检查缴费状态: {state['student_id']}")
    
    if state['payment_completed']:
        state['current_step'] = "assign_dorm"
        state['messages'].append(AIMessage(
            content="✅ 缴费检查通过"
        ))
    else:
        state['current_step'] = "payment_guide"
        state['messages'].append(AIMessage(
            content="⚠️ 尚未完成缴费，请前往财务处或在线支付"
        ))
    
    return state


def assign_dorm_node(state: CheckInState) -> CheckInState:
    """宿舍分配节点"""
    print(f"🏠 分配宿舍: {state['student_id']}")
    
    # 模拟宿舍分配
    state['dorm_assigned'] = True
    state['current_step'] = "complete"
    state['messages'].append(AIMessage(
        content="✅ 宿舍分配完成: 东区1号楼 302室"
    ))
    
    return state


def manual_review_node(state: CheckInState) -> CheckInState:
    """人工审核节点"""
    print(f"👤 人工审核: {state['student_id']}")
    
    state['messages'].append(AIMessage(
        content="📋 您的申请已提交人工审核，请等待辅导员处理"
    ))
    
    return state


def route_verify(state: CheckInState) -> str:
    """身份验证路由决策"""
    if state.get('needs_manual_review'):
        return "manual_review"
    return "check_payment"


def route_payment(state: CheckInState) -> str:
    """缴费检查路由决策"""
    if state['current_step'] == "payment_guide":
        return "manual_review"
    return "assign_dorm"


def build_checkin_workflow():
    """构建报到流程工作流"""
    workflow = StateGraph(CheckInState)
    
    # 添加节点
    workflow.add_node("verify_identity", verify_identity_node)
    workflow.add_node("check_payment", check_payment_node)
    workflow.add_node("assign_dorm", assign_dorm_node)
    workflow.add_node("manual_review", manual_review_node)
    
    # 添加边
    workflow.add_edge(START, "verify_identity")
    
    # 条件路由
    workflow.add_conditional_edges(
        "verify_identity",
        route_verify,
        {
            "check_payment": "check_payment",
            "manual_review": "manual_review"
        }
    )
    
    workflow.add_conditional_edges(
        "check_payment",
        route_payment,
        {
            "assign_dorm": "assign_dorm",
            "manual_review": "manual_review"
        }
    )
    
    workflow.add_edge("assign_dorm", END)
    workflow.add_edge("manual_review", END)
    
    return workflow.compile()
