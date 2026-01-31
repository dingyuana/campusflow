"""
Day 6: 自定义中间件
实现预算控制、消息截断、敏感词过滤
"""

from typing import Callable, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import re
import tiktoken


class BudgetMiddleware:
    """预算控制中间件"""

    def __init__(self, max_tokens: int = 10000, model_name: str = "gpt-3.5-turbo"):
        """
        初始化预算控制中间件

        Args:
            max_tokens: 最大 Token 数
            model_name: 使用的模型名称
        """
        self.max_tokens = max_tokens
        self.used_tokens = 0
        self.model_name = model_name

        # 初始化 Token 计数器
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """
        计算 Token 数量

        Args:
            text: 输入文本

        Returns:
            Token 数量
        """
        return len(self.encoding.encode(text))

    def check_budget(self, messages: List[BaseMessage]) -> bool:
        """
        检查预算是否足够

        Args:
            messages: 消息列表

        Returns:
            是否有足够预算
        """
        # 计算消息的总 Token 数
        total_tokens = 0
        for msg in messages:
            total_tokens += self.count_tokens(msg.content)

        # 计算预估输出 Token 数（假设输出长度与输入相同）
        estimated_output = total_tokens

        # 检查是否超出预算
        if total_tokens + estimated_output > self.max_tokens:
            print(f"⚠️  预算不足: {total_tokens} + {estimated_output} > {self.max_tokens}")
            return False

        print(f"✅ 预算检查通过: {total_tokens} tokens")
        return True

    def update_used_tokens(self, tokens: int):
        """
        更新已使用的 Token 数

        Args:
            tokens: 新使用的 Token 数
        """
        self.used_tokens += tokens
        print(f"💰 已使用 Token: {self.used_tokens}/{self.max_tokens}")


class MessageTruncationMiddleware:
    """消息截断中间件"""

    def __init__(self, max_tokens: int = 4000, model_name: str = "gpt-3.5-turbo"):
        """
        初始化消息截断中间件

        Args:
            max_tokens: 最大 Token 数
            model_name: 使用的模型名称
        """
        self.max_tokens = max_tokens
        self.model_name = model_name

        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def truncate_messages(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        截断消息以适应 Token 限制

        Args:
            messages: 原始消息列表

        Returns:
            截断后的消息列表
        """
        total_tokens = 0
        truncated_messages = []

        # 从最旧的消息开始，逐步添加直到达到限制
        for msg in reversed(messages):
            msg_tokens = self.count_tokens(msg.content)

            if total_tokens + msg_tokens > self.max_tokens:
                # 截断当前消息
                remaining_tokens = self.max_tokens - total_tokens
                truncated_content = self.truncate_text(msg.content, remaining_tokens)

                truncated_msg = msg.__class__(content=truncated_content)
                truncated_messages.insert(0, truncated_msg)
                break

            truncated_messages.insert(0, msg)
            total_tokens += msg_tokens

        print(f"✅ 消息截断: {len(messages)} -> {len(truncated_messages)} 条消息")

        return truncated_messages

    def count_tokens(self, text: str) -> int:
        """计算 Token 数量"""
        return len(self.encoding.encode(text))

    def truncate_text(self, text: str, max_tokens: int) -> str:
        """
        截断文本以适应 Token 限制

        Args:
            text: 原始文本
            max_tokens: 最大 Token 数

        Returns:
            截断后的文本
        """
        tokens = self.encoding.encode(text)
        truncated_tokens = tokens[:max_tokens]
        return self.encoding.decode(truncated_tokens)


class PIIFilterMiddleware:
    """敏感词/PII 过滤中间件"""

    def __init__(self):
        """初始化 PII 过滤中间件"""
        # 定义敏感词模式（示例）
        self.sensitive_patterns = {
            # 手机号（中国大陆）
            'phone': r'\b1[3-9]\d{9}\b',
            # 身份证号
            'id_card': r'\b[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])\d{2}[0-9Xx]\b',
            # 银行卡号
            'bank_card': r'\b\d{16,19}\b',
            # 邮箱
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        }

        # 定义需要脱敏的字段
        self.sensitive_fields = ['phone', 'id_card', 'bank_card', 'email', 'password']

    def filter_message(self, message: str) -> str:
        """
        过滤消息中的敏感信息

        Args:
            message: 原始消息

        Returns:
            过滤后的消息
        """
        filtered_message = message

        # 应用敏感词模式
        for pattern_type, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, filtered_message)
            if matches:
                print(f"⚠️  检测到敏感信息 ({pattern_type}): {len(matches)} 处")
                # 脱敏处理
                for match in matches:
                    masked = self.mask_sensitive_data(match, pattern_type)
                    filtered_message = filtered_message.replace(match, masked)

        return filtered_message

    def mask_sensitive_data(self, data: str, data_type: str) -> str:
        """
        脱敏处理

        Args:
            data: 敏感数据
            data_type: 数据类型

        Returns:
            脱敏后的数据
        """
        if data_type == 'phone':
            # 手机号：保留前3位和后4位
            if len(data) == 11:
                return f"{data[:3]}****{data[7:]}"

        elif data_type == 'id_card':
            # 身份证：只显示前6位和后4位
            if len(data) == 18:
                return f"{data[:6]}********{data[14:]}"

        elif data_type == 'email':
            # 邮箱：只显示前3个字符
            parts = data.split('@')
            if len(parts) == 2:
                return f"{parts[0][:3]}***@{parts[1]}"

        elif data_type == 'bank_card':
            # 银行卡：只显示后4位
            return f"****{data[-4:]}"

        return f"***{data[-2:]}"


class MiddlewareChain:
    """中间件链"""

    def __init__(
        self,
        budget: BudgetMiddleware = None,
        truncation: MessageTruncationMiddleware = None,
        pii_filter: PIIFilterMiddleware = None
    ):
        """
        初始化中间件链

        Args:
            budget: 预算控制中间件
            truncation: 消息截断中间件
            pii_filter: PII 过滤中间件
        """
        self.budget = budget or BudgetMiddleware()
        self.truncation = truncation or MessageTruncationMiddleware()
        self.pii_filter = pii_filter or PIIFilterMiddleware()

    def process_input(self, messages: List[BaseMessage], user_input: str) -> tuple:
        """
        处理输入消息

        Args:
            messages: 消息历史
            user_input: 用户输入

        Returns:
            (处理后的消息, 是否允许继续）
        """
        print("=" * 60)
        print("🔧 中间件处理输入")
        print("=" * 60)
        print()

        # 1. PII 过滤
        print("1. PII 过滤")
        print("-" * 60)
        filtered_input = self.pii_filter.filter_message(user_input)
        if filtered_input != user_input:
            print(f"   原始输入: {user_input}")
            print(f"   过滤后: {filtered_input}")
        else:
            print("   ✅ 无敏感信息")
        print()

        # 2. 添加用户消息
        messages.append(HumanMessage(content=filtered_input))

        # 3. 消息截断
        print("2. 消息截断")
        print("-" * 60)
        messages = self.truncation.truncate_messages(messages)
        print()

        # 4. 预算检查
        print("3. 预算检查")
        print("-" * 60)
        if not self.budget.check_budget(messages):
            print("   ❌ 预算不足，请求被拒绝")
            return (messages, False)

        print("   ✅ 预算充足")
        print()

        return (messages, True)

    def process_output(self, output: str, tokens_used: int = 0) -> str:
        """
        处理输出

        Args:
            output: 原始输出
            tokens_used: 使用的 Token 数

        Returns:
            处理后的输出
        """
        print("4. 输出处理")
        print("-" * 60)

        # 更新预算
        if tokens_used > 0:
            self.budget.update_used_tokens(tokens_used)

        # PII 过滤（输出中也可能有敏感信息）
        filtered_output = self.pii_filter.filter_message(output)

        print("   ✅ 输出处理完成")
        print()

        return filtered_output


def test_middleware():
    """测试中间件功能"""
    print("=" * 60)
    print("🧪 测试中间件功能")
    print("=" * 60)
    print()

    # 创建中间件链
    middleware_chain = MiddlewareChain()

    # 测试输入
    test_messages = [
        AIMessage(content="你好，有什么可以帮助你的？"),
        HumanMessage(content="我的手机号是 13800138000，想查询报到信息"),
    ]

    print("=" * 60)
    print("📝 测试场景 1: 敏感信息过滤")
    print("=" * 60)

    # 处理输入
    processed_messages, allowed = middleware_chain.process_input(
        test_messages,
        "我的身份证号是 310115199001011234，需要提供什么材料？"
    )

    if allowed:
        print(f"✅ 允许继续，处理后的消息: {len(processed_messages)} 条")
    else:
        print("❌ 被拒绝")
    print()

    print("=" * 60)
    print("📝 测试场景 2: 消息截断")
    print("=" * 60)

    # 创建长消息列表
    long_messages = []
    for i in range(10):
        long_messages.append(AIMessage(content=f"这是第{i+1}条消息。" * 100))
    long_messages.append(HumanMessage(content=f"用户消息{i+1}。" * 100))

    # 处理长消息
    truncated_messages, _ = middleware_chain.process_input(
        long_messages,
        "测试消息"
    )

    print(f"原始消息: {len(long_messages)} 条")
    print(f"截断后: {len(truncated_messages)} 条")
    print()

    print("=" * 60)
    print("✅ 中间件测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_middleware()
