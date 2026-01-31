"""
Day 5: 安全中间件责任链
组装四层安全中间件
"""

from .base import BaseMiddleware, RequestContext, MiddlewareResponse
from .security_layers import (
    BudgetControlMiddleware,
    TruncationMiddleware,
    SensitiveWordMiddleware,
    PIIDetectionMiddleware
)


class SecurityMiddlewareChain:
    """安全中间件链管理器"""
    
    def __init__(self):
        # 按顺序初始化：预算 → 截断 → 敏感词 → PII
        self.budget = BudgetControlMiddleware(max_input_tokens=2000)
        self.truncation = TruncationMiddleware(max_chars_per_msg=1500)
        self.sensitive = SensitiveWordMiddleware()
        self.pii = PIIDetectionMiddleware()
        
        # 组装链
        self.budget.set_next(self.truncation).set_next(self.sensitive).set_next(self.pii)
        
        self.entry_point = self.budget
    
    def process(self, user_id: str, thread_id: str, message: str) -> MiddlewareResponse:
        """
        处理用户输入
        
        Args:
            user_id: 用户 ID
            thread_id: 对话线程 ID
            message: 用户消息
            
        Returns:
            中间件处理结果
        """
        context = RequestContext(
            user_id=user_id,
            thread_id=thread_id,
            message=message
        )
        return self.entry_point.process(context)
    
    def get_audit_log(self, response: MiddlewareResponse) -> dict:
        """
        生成审计日志
        
        Args:
            response: 中间件响应
            
        Returns:
            审计日志字典
        """
        return {
            "allowed": response.allowed,
            "reason": response.reason,
            "metadata": response.metadata,
            "processed_message": response.message if response.allowed else None
        }


# 全局实例
security_chain = SecurityMiddlewareChain()
