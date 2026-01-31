"""
Day 5: 中间件基类
定义安全中间件的责任链架构
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
import time


@dataclass
class RequestContext:
    """请求上下文"""
    user_id: str
    thread_id: str
    message: str
    timestamp: float = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class MiddlewareResponse:
    """中间件处理结果"""
    allowed: bool
    message: str  # 可能已被修改（如脱敏后）
    reason: Optional[str] = None  # 拦截原因
    metadata: Dict[str, Any] = None


class BaseMiddleware(ABC):
    """中间件基类"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.next_middleware: Optional[BaseMiddleware] = None
    
    def set_next(self, middleware: 'BaseMiddleware'):
        """设置下一个中间件（支持链式调用）"""
        self.next_middleware = middleware
        return middleware  # 支持链式调用
    
    def process(self, context: RequestContext) -> MiddlewareResponse:
        """处理请求"""
        if not self.enabled:
            if self.next_middleware:
                return self.next_middleware.process(context)
            return MiddlewareResponse(True, context.message)
        
        # 执行当前中间件逻辑
        result = self.handle(context)
        
        # 如果被拦截或没有下一个，直接返回
        if not result.allowed or not self.next_middleware:
            return result
        
        # 传递到下一个中间件（可能修改了 message）
        new_context = RequestContext(
            user_id=context.user_id,
            thread_id=context.thread_id,
            message=result.message,
            metadata={**(context.metadata or {}), **(result.metadata or {})}
        )
        return self.next_middleware.process(new_context)
    
    @abstractmethod
    def handle(self, context: RequestContext) -> MiddlewareResponse:
        """具体处理逻辑，子类实现"""
        pass
