"""
Day 6: HITL 人机回环机制实现
支持在关键节点暂停等待人工确认
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
import time


class HITLState(TypedDict):
    """HITL 状态结构"""
    messages: list
    pending_action: Optional[str]  # 待确认的操作
    pending_data: Optional[dict]   # 操作相关数据
    human_decision: Optional[str]  # 'approved', 'rejected', 'modified'
    final_result: Optional[str]


def process_payment_request(state: HITLState):
    """
    处理缴费请求：需要人工确认金额
    使用 interrupt 暂停流程等待人工输入
    """
    # 模拟计算应缴费用
    tuition = 5000.00
    accommodation = 1200.00
    total = tuition + accommodation
    
    # 准备待确认信息
    action_payload = {
        "action": "charge_payment",
        "amount": total,
        "items": {
            "学费": tuition,
            "住宿费": accommodation
        },
        "student_id": "2024001",
        "timestamp": time.time()
    }
    
    # 中断等待人工确认
    # interrupt 会暂停图执行，等待外部传入 Command(resume=...)
    human_response = interrupt(
        {
            "type": "payment_confirmation",
            "message": f"请确认以下缴费信息：",
            "details": action_payload,
            "options": ["approve", "reject", "modify"]
        }
    )
    
    # 恢复后处理人工输入
    if human_response["decision"] == "approve":
        return {
            "pending_action": "charge_payment",
            "pending_data": action_payload,
            "human_decision": "approved",
            "messages": [AIMessage(content="✅ 缴费申请已批准，正在处理...")]
        }
    elif human_response["decision"] == "reject":
        return {
            "human_decision": "rejected",
            "messages": [AIMessage(content="❌ 缴费申请已被拒绝，请联系财务处。")]
        }
    else:  # modify
        # 修改金额后重新确认（递归或重新进入节点）
        new_amount = human_response.get("modified_amount", total)
        return {
            "pending_data": {**action_payload, "amount": new_amount},
            "messages": [AIMessage(content=f"金额已修改为 {new_amount}，请重新确认。")]
        }


def execute_payment(state: HITLState):
    """执行缴费（仅在被批准后）"""
    if state.get("human_decision") != "approved":
        return {"final_result": "cancelled"}
    
    # 模拟执行
    data = state["pending_data"]
    return {
        "final_result": f"成功扣款 {data['amount']} 元",
        "messages": [AIMessage(content=f"✅ 缴费成功！金额：{data['amount']} 元")]
    }


def material_review_node(state: HITLState):
    """材料审核中断点"""
    return interrupt({
        "type": "document_review",
        "documents": ["身份证.pdf", "录取通知书.pdf"],
        "action": "验证材料真实性"
    })


def dormitory_selection_node(state: HITLState):
    """宿舍选择中断点（人工分配或确认）"""
    return interrupt({
        "type": "dormitory_assignment",
        "options": ["A1-301", "A1-302", "A2-205"],
        "action": "确认宿舍分配"
    })


def check_timeout(state: HITLState):
    """检查审核是否超时（如 24 小时未响应）"""
    created_at = state.get("pending_data", {}).get("timestamp", 0)
    if time.time() - created_at > 86400:  # 24小时
        return {
            "messages": [AIMessage(content="⏰ 审核超时，流程已自动取消，请重新申请。")],
            "final_result": "timeout"
        }
    return None  # 未超时


def route_to_next_step(state: HITLState):
    """路由函数根据状态决定下一个中断点"""
    if state.get("human_decision") == "rejected":
        return "end"
    if not state.get("material_verified"):
        return "material_review"
    if not state.get("payment_confirmed"):
        return "payment"
    if not state.get("dormitory_confirmed"):
        return "dormitory"
    return "completed"


def create_hitl_workflow():
    """创建带 HITL 的工作流"""
    workflow = StateGraph(HITLState)
    
    workflow.add_node("request_payment", process_payment_request)
    workflow.add_node("execute", execute_payment)
    
    workflow.set_entry_point("request_payment")
    workflow.add_edge("request_payment", "execute")
    workflow.add_edge("execute", "__end__")
    
    # 使用检查点保存中断状态
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    
    return app


def run_with_hitl():
    """运行支持 HITL 的 Agent"""
    app = create_hitl_workflow()
    thread_id = "audit_demo_001"
    config = {"configurable": {"thread_id": thread_id}}
    
    print("🚀 启动报到缴费流程...")
    
    # 第一次运行，会执行到 interrupt 处暂停
    for event in app.stream(
        {"messages": [HumanMessage(content="我要交学费")]},
        config,
        stream_mode="values"
    ):
        print(f"状态：{event}")
        
        # 检查是否中断
        if "__interrupt__" in event:
            interrupt_info = event["__interrupt__"][0]
            print(f"\n🔔 中断信息：{interrupt_info.value}")
            print("\n⏳ 等待人工审核...")
            
            # 模拟人工决定
            decision = input("请输入决定（approve/reject/modify）：").strip()
            
            resume_data = {"decision": decision}
            if decision == "modify":
                new_amount = input("请输入修改后的金额：")
                resume_data["modified_amount"] = float(new_amount)
            
            # 恢复执行
            print("🔄 恢复执行...")
            for resume_event in app.stream(
                Command(resume=resume_data),
                config,
                stream_mode="values"
            ):
                if "messages" in resume_event:
                    print(f"🤖：{resume_event['messages'][-1].content}")
                if "final_result" in resume_event:
                    print(f"📊 最终结果：{resume_event['final_result']}")


if __name__ == "__main__":
    run_with_hitl()
