"""
Day 6: 人机协作 HITL 机制

实现 Human-in-the-loop 中断恢复机制
- 中断点设计
- 审核工作台
- 超时处理
"""

from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage


class HITLState(TypedDict):
    """HITL 流程状态"""
    request_id: str
    student_id: str
    request_type: str
    details: dict
    status: str  # pending, approved, rejected, modified
    reviewer_comment: str


def create_hitl_interrupt_point():
    """
    创建 HITL 中断点
    
    在关键节点中断流程，等待人工审核
    """
    print("🛑 HITL 中断点: 流程已暂停，等待人工审核")
    print("   操作选项: approve / reject / modify")
    
    # 这里应该实际调用 langgraph 的 interrupt 机制
    # 为简化示例，使用输入模拟
    return input("请输入审核决策 (approve/reject/modify): ").strip()


def dorm_approval_workflow():
    """
    宿舍申请审核工作流
    
    申请 → 中断 → 审核 → 恢复 → 完成
    """
    print("=" * 60)
    print("🏠 宿舍申请 HITL 流程")
    print("=" * 60)
    print()
    
    # 模拟申请数据
    application = {
        "student_id": "S001",
        "student_name": "张三",
        "preferred_dorm": "东区1号楼",
        "reason": "靠近教学楼"
    }
    
    print(f"📋 收到宿舍申请:")
    for key, value in application.items():
        print(f"   {key}: {value}")
    print()
    
    # 中断等待审核
    decision = create_hitl_interrupt_point()
    
    if decision == "approve":
        print("✅ 申请已通过")
        return {"status": "approved", "dorm_assigned": "东区1号楼302室"}
    elif decision == "reject":
        print("❌ 申请已拒绝")
        return {"status": "rejected"}
    else:
        print("📝 申请已修改")
        return {"status": "modified"}
