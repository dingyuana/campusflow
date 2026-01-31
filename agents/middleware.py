"""
Day 5: 安全防护中间件体系

四层防护：
1. 预算控制 (Budget Control)
2. 消息截断 (Context Truncation)
3. 敏感词过滤 (Sensitive Word Filter)
4. PII 检测 (个人身份信息)
"""

import tiktoken
import re
from typing import List, Dict, Any, Callable
from langchain_core.messages import BaseMessage


class BudgetMiddleware:
    """预算控制中间件"""
    
    def __init__(self, max_tokens: int = 4000, max_cost: float = 0.01):
        self.max_tokens = max_tokens
        self.max_cost = max_cost
        self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def check_budget(self, messages: List[BaseMessage]) -> tuple[bool, str]:
        """检查预算是否超限"""
        total_tokens = 0
        for msg in messages:
            total_tokens += len(self.encoder.encode(msg.content))
        
        if total_tokens > self.max_tokens:
            return False, f"❌ Token 超限: {total_tokens} > {self.max_tokens}"
        
        # 估算成本 (gpt-4o-mini: $0.15/1M input tokens)
        estimated_cost = (total_tokens / 1_000_000) * 0.15
        if estimated_cost > self.max_cost:
            return False, f"❌ 成本超限: ${estimated_cost:.4f} > ${self.max_cost}"
        
        return True, f"✅ 预算检查通过: {total_tokens} tokens, ${estimated_cost:.4f}"


class TruncationMiddleware:
    """消息截断中间件"""
    
    def __init__(self, max_messages: int = 10, keep_system: bool = True):
        self.max_messages = max_messages
        self.keep_system = keep_system
    
    def truncate(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """截断消息历史"""
        if len(messages) <= self.max_messages:
            return messages
        
        # 保留最近的 max_messages 条
        return messages[-self.max_messages:]


class SensitiveFilterMiddleware:
    """敏感词过滤中间件"""
    
    def __init__(self, level: str = "normal"):
        self.level = level
        # 基础敏感词列表
        self.sensitive_words = {
            "strict": ["暴力", "色情", "赌博", "毒品", "恐怖"],
            "normal": ["脏话", "辱骂", "歧视"],
            "loose": []
        }
    
    def filter(self, text: str) -> tuple[str, bool]:
        """过滤敏感词"""
        words = self.sensitive_words.get(self.level, [])
        filtered = text
        
        for word in words:
            if word in filtered:
                filtered = filtered.replace(word, "*" * len(word))
        
        is_clean = filtered == text
        return filtered, is_clean


class PIIMiddleware:
    """PII 检测中间件"""
    
    def __init__(self):
        # 正则模式
        self.patterns = {
            "phone": r"1[3-9]\d{9}",
            "id_card": r"\d{17}[\dXx]",
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "student_id": r"\d{8,12}",
        }
    
    def detect(self, text: str) -> Dict[str, List[str]]:
        """检测 PII"""
        found = {}
        for pii_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                found[pii_type] = matches
        return found
    
    def mask(self, text: str) -> str:
        """脱敏处理"""
        # 手机号脱敏: 138****1234
        text = re.sub(r"(1[3-9]\d)(\d{4})(\d{4})", r"\1****\3", text)
        # 身份证号脱敏
        text = re.sub(r"(\d{6})(\d{8})(\d{4})", r"\1********\3", text)
        return text


class SecurityPipeline:
    """安全中间件管道"""
    
    def __init__(self):
        self.budget = BudgetMiddleware()
        self.truncation = TruncationMiddleware()
        self.sensitive = SensitiveFilterMiddleware()
        self.pii = PIIMiddleware()
    
    def process(self, messages: List[BaseMessage]) -> tuple[bool, str]:
        """按序执行安全中间件"""
        # 1. 预算检查
        ok, msg = self.budget.check_budget(messages)
        if not ok:
            return False, msg
        print(f"   {msg}")
        
        # 2. 消息截断
        messages = self.truncation.truncate(messages)
        print(f"   ✅ 消息截断: 保留 {len(messages)} 条")
        
        # 3. 敏感词过滤
        for msg in messages:
            if hasattr(msg, 'content'):
                filtered, is_clean = self.sensitive.filter(msg.content)
                if not is_clean:
                    print(f"   ⚠️  敏感词已过滤")
        
        # 4. PII 检测
        for msg in messages:
            if hasattr(msg, 'content'):
                pii_found = self.pii.detect(msg.content)
                if pii_found:
                    print(f"   ⚠️  检测到 PII: {list(pii_found.keys())}")
        
        return True, "✅ 所有安全检查通过"
