"""
Day 6: 人工审核控制台
模拟人工审核工作台（实际应为 Web 界面）
"""

import time
from typing import Dict, Any


class AuditConsole:
    """模拟人工审核工作台"""
    
    def __init__(self):
        self.pending_tasks: Dict[str, Any] = {}  # thread_id -> task
    
    def register_task(self, thread_id: str, interrupt_payload: dict):
        """注册待审核任务"""
        self.pending_tasks[thread_id] = {
            "payload": interrupt_payload,
            "status": "pending",
            "created_at": time.time()
        }
        print(f"\n🔔 新审核任务（Thread: {thread_id}）")
        print(f"类型：{interrupt_payload['type']}")
        print(f"详情：{interrupt_payload.get('details', interrupt_payload)}")
        print("选项：approve | reject | modify")
    
    def make_decision(self, thread_id: str, decision: str, **kwargs):
        """人工做出决定"""
        if thread_id not in self.pending_tasks:
            print(f"❌ 任务 {thread_id} 不存在")
            return None
        
        task = self.pending_tasks[thread_id]
        task["status"] = "processed"
        task["decision"] = decision
        
        # 构建 resume 数据
        resume_data = {
            "decision": decision,
            **kwargs
        }
        
        print(f"✅ 已处理任务 {thread_id}：{decision}")
        return resume_data
    
    def list_pending_tasks(self):
        """列出所有待审核任务"""
        pending = {k: v for k, v in self.pending_tasks.items() if v["status"] == "pending"}
        print(f"\n📋 待审核任务数：{len(pending)}")
        for thread_id, task in pending.items():
            wait_time = time.time() - task["created_at"]
            print(f"  - {thread_id}: {task['payload']['type']} (等待 {wait_time:.0f} 秒)")
        return pending


# 全局审核台
audit_console = AuditConsole()


if __name__ == "__main__":
    # 测试
    audit_console.register_task("thread_001", {
        "type": "payment_confirmation",
        "details": {"amount": 6200, "student_id": "2024001"}
    })
    
    # 列出任务
    audit_console.list_pending_tasks()
    
    # 做出决定
    result = audit_console.make_decision("thread_001", "approve")
    print(f"Resume 数据：{result}")
