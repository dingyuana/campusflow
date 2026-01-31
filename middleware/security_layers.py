"""
Day 5: 四层安全中间件实现
预算控制 → 消息截断 → 敏感词过滤 → PII 检测
"""

import re
import tiktoken
from typing import Dict
from .base import BaseMiddleware, RequestContext, MiddlewareResponse


class BudgetControlMiddleware(BaseMiddleware):
    """预算控制中间件：限制 Token 消耗"""
    
    def __init__(self, max_input_tokens: int = 2000, max_daily_cost: float = 10.0):
        super().__init__()
        self.max_input_tokens = max_input_tokens
        self.max_daily_cost = max_daily_cost
        self.user_daily_usage: Dict[str, float] = {}  # 简化版，实际应用 Redis
        
        # 初始化 tiktoken
        try:
            self.encoding = tiktoken.encoding_for_model("gpt-4")
        except:
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def handle(self, context: RequestContext) -> MiddlewareResponse:
        user_id = context.user_id
        message = context.message
        
        # 1. 检查输入长度
        token_count = len(self.encoding.encode(message))
        if token_count > self.max_input_tokens:
            return MiddlewareResponse(
                allowed=False,
                message=message,
                reason=f"输入过长（{token_count} tokens），超过限制 {self.max_input_tokens}"
            )
        
        # 2. 检查日预算（模拟成本计算：$0.002 / 1K tokens）
        cost = (token_count / 1000) * 0.002
        current_usage = self.user_daily_usage.get(user_id, 0)
        
        if current_usage + cost > self.max_daily_cost:
            return MiddlewareResponse(
                allowed=False,
                message=message,
                reason=f"超出日预算（当前: ${current_usage:.4f}, 限制: ${self.max_daily_cost}）"
            )
        
        self.user_daily_usage[user_id] = current_usage + cost
        
        return MiddlewareResponse(
            allowed=True,
            message=message,
            metadata={"input_tokens": token_count, "estimated_cost": cost}
        )


class TruncationMiddleware(BaseMiddleware):
    """消息截断中间件：防止上下文窗口溢出"""
    
    def __init__(self, max_messages: int = 10, max_chars_per_msg: int = 1000):
        super().__init__()
        self.max_messages = max_messages
        self.max_chars_per_msg = max_chars_per_msg
    
    def handle(self, context: RequestContext) -> MiddlewareResponse:
        message = context.message
        
        # 策略：如果消息列表过长，保留系统提示和最近 N 条
        # 简化处理：直接截断单条消息长度
        if len(message) > self.max_chars_per_msg:
            truncated = message[:self.max_chars_per_msg] + "...[截断]"
            return MiddlewareResponse(
                allowed=True,
                message=truncated,
                metadata={"truncated": True, "original_length": len(message)}
            )
        
        return MiddlewareResponse(allowed=True, message=message)


class SensitiveWordMiddleware(BaseMiddleware):
    """敏感词过滤中间件"""
    
    def __init__(self):
        super().__init__()
        # 校园场景敏感词库（示例）
        self.sensitive_patterns = [
            r'\b代考\b', r'\b替考\b', r'\b枪手\b',
            r'\b办证\b', r'\b假证\b',
            r'\b辱骂教师\b', r'\b攻击学校\b',
            r'\b(反动|色情|暴力)\b',  # 正则示例
        ]
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.sensitive_patterns]
    
    def handle(self, context: RequestContext) -> MiddlewareResponse:
        message = context.message
        
        for pattern in self.compiled_patterns:
            if pattern.search(message):
                matched = pattern.findall(message)
                return MiddlewareResponse(
                    allowed=False,
                    message=message,
                    reason=f"检测到敏感词：{matched}",
                    metadata={"violation_type": "sensitive_word", "matched": matched}
                )
        
        return MiddlewareResponse(allowed=True, message=message)


class PIIDetectionMiddleware(BaseMiddleware):
    """PII 检测与脱敏中间件"""
    
    def __init__(self, mask_char: str = "*"):
        super().__init__()
        self.mask_char = mask_char
        # PII 正则模式
        self.pii_patterns = {
            "phone": (re.compile(r'\b1[3-9]\d{9}\b'), "手机号"),
            "id_card": (re.compile(r'\b\d{17}[\dXx]|\d{15}\b'), "身份证号"),
            "student_id": (re.compile(r'\b20\d{8}\b'), "学号"),  # 如 20240001
            "bank_card": (re.compile(r'\b\d{16}|\d{19}\b'), "银行卡号"),
            "email": (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), "邮箱")
        }
    
    def handle(self, context: RequestContext) -> MiddlewareResponse:
        message = context.message
        detected_pii = []
        
        for pii_type, (pattern, label) in self.pii_patterns.items():
            matches = pattern.findall(message)
            for match in matches:
                # 脱敏处理
                if pii_type == "phone":
                    masked = match[:3] + self.mask_char * 4 + match[-4:]
                elif pii_type == "id_card":
                    masked = match[:6] + self.mask_char * 8 + match[-4:]
                else:
                    masked = self.mask_char * len(match)
                
                message = message.replace(match, masked)
                detected_pii.append({"type": label, "original": match, "masked": masked})
        
        if detected_pii:
            return MiddlewareResponse(
                allowed=True,  # PII 可以脱敏后继续，也可以改为 False 拦截
                message=message,
                metadata={"pii_detected": True, "pii_items": detected_pii}
            )
        
        return MiddlewareResponse(allowed=True, message=message)
