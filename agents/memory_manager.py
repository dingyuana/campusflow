"""
Day 6: 记忆管理模块
实现短期记忆和长期记忆
"""

from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()


class ShortTermMemory:
    """短期记忆管理器（基于 State）"""

    def __init__(self, max_messages: int = 10):
        """
        初始化短期记忆

        Args:
            max_messages: 最多保留的消息数量
        """
        self.max_messages = max_messages

    def add_message(self, messages: List[BaseMessage], new_message: BaseMessage) -> List[BaseMessage]:
        """
        添加新消息到短期记忆

        Args:
            messages: 当前消息列表
            new_message: 新消息

        Returns:
            更新后的消息列表
        """
        updated_messages = messages + [new_message]

        # 保留最近的消息
        if len(updated_messages) > self.max_messages:
            updated_messages = updated_messages[-self.max_messages:]

        return updated_messages

    def get_recent_context(self, messages: List[BaseMessage], limit: int = 5) -> str:
        """
        获取最近的对话上下文

        Args:
            messages: 消息列表
            limit: 返回的消息数量

        Returns:
            格式化的上下文字符串
        """
        recent_messages = messages[-limit:] if messages else []

        context = ""
        for msg in recent_messages:
            role = "用户" if msg.type == "human" else "助手"
            context += f"{role}: {msg.content}\n"

        return context


class LongTermMemory:
    """长期记忆管理器（基于 Chroma 向量库）"""

    def __init__(self, persist_directory: str = "./db/experience_memory"):
        """
        初始化长期记忆

        Args:
            persist_directory: 持久化目录
        """
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-m3",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vector_store = None

    def initialize(self):
        """初始化或加载长期记忆向量库"""
        from pathlib import Path

        if Path(self.persist_directory).exists():
            print(f"✅ 加载长期记忆: {self.persist_directory}")
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="experience_memory"
            )
        else:
            print(f"✅ 创建长期记忆: {self.persist_directory}")
            # 创建空向量库（添加一个虚拟文档）
            from langchain_core.documents import Document
            dummy_doc = Document(page_content="初始化", metadata={"type": "init"})
            self.vector_store = Chroma.from_documents(
                documents=[dummy_doc],
                embedding=self.embeddings,
                persist_directory=self.persist_directory,
                collection_name="experience_memory"
            )

    def add_experience(self, query: str, answer: str, context: Dict[str, Any] = None):
        """
        添加经验到长期记忆

        Args:
            query: 用户问题
            answer: 系统回答
            context: 附加的上下文信息
        """
        from langchain_core.documents import Document

        # 创建经验文档
        content = f"问题: {query}\n回答: {answer}"
        metadata = {
            "type": "experience",
            "query": query,
            "answer": answer
        }

        if context:
            metadata.update(context)

        document = Document(page_content=content, metadata=metadata)

        # 添加到向量库
        self.vector_store.add_documents([document])
        self.vector_store.persist()

        print(f"✅ 经验已添加到长期记忆: {query[:50]}...")

    def retrieve_relevant_experiences(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        检索相关经验

        Args:
            query: 查询文本
            k: 返回的经验数量

        Returns:
            相关经验列表
        """
        results = self.vector_store.similarity_search(query, k=k)

        experiences = []
        for doc in results:
            experiences.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })

        print(f"✅ 检索到 {len(experiences)} 条相关经验")

        return experiences

    def get_recent_experiences(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的经验（简单实现，返回所有经验）

        Args:
            limit: 返回的经验数量

        Returns:
            经验列表
        """
        # 简单实现：返回所有经验
        # 实际应用中应该按时间排序
        all_docs = self.vector_store.similarity_search("", k=limit)

        experiences = []
        for doc in all_docs:
            if doc.metadata.get("type") == "experience":
                experiences.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })

        return experiences[:limit]


class MemoryManager:
    """记忆管理器（整合短期和长期记忆）"""

    def __init__(self, max_short_term: int = 10, long_term_dir: str = "./db/experience_memory"):
        """
        初始化记忆管理器

        Args:
            max_short_term: 短期记忆最大消息数
            long_term_dir: 长期记忆持久化目录
        """
        self.short_term = ShortTermMemory(max_short_term)
        self.long_term = LongTermMemory(long_term_dir)
        self.long_term.initialize()

    def add_interaction(self, messages: List[BaseMessage], new_message: BaseMessage, query: str, answer: str):
        """
        添加交互到记忆

        Args:
            messages: 短期消息历史
            new_message: 新消息
            query: 用户问题
            answer: 系统回答
        """
        # 添加到短期记忆
        updated_messages = self.short_term.add_message(messages, new_message)

        # 添加到长期记忆（如果是对话的完整回合）
        if new_message.type == "ai":
            self.long_term.add_experience(query, answer)

        return updated_messages

    def get_context(self, messages: List[BaseMessage], query: str) -> Dict[str, Any]:
        """
        获取上下文（短期 + 长期）

        Args:
            messages: 短期消息历史
            query: 当前查询

        Returns:
            上下文字典
        """
        # 短期上下文
        short_term_context = self.short_term.get_recent_context(messages)

        # 长期上下文（相关经验）
        long_term_experiences = self.long_term.retrieve_relevant_experiences(query)

        long_term_context = ""
        if long_term_experiences:
            long_term_context = "相关经验:\n"
            for i, exp in enumerate(long_term_experiences, 1):
                long_term_context += f"{i}. {exp['content']}\n"

        return {
            "short_term": short_term_context,
            "long_term": long_term_context,
            "experiences": long_term_experiences
        }


def test_memory():
    """测试记忆功能"""
    from langchain_core.messages import HumanMessage, AIMessage

    print("=" * 60)
    print("🧪 测试记忆管理功能")
    print("=" * 60)
    print()

    # 创建记忆管理器
    memory_manager = MemoryManager()

    print("1. 测试短期记忆")
    print("-" * 60)

    messages = []
    messages = memory_manager.short_term.add_message(messages, HumanMessage(content="什么是报到？"))
    messages = memory_manager.short_term.add_message(messages, AIMessage(content="报到是指新生入学..."))
    messages = memory_manager.short_term.add_message(messages, HumanMessage(content="需要什么材料？"))

    context = memory_manager.short_term.get_recent_context(messages)
    print(f"最近上下文:\n{context}")
    print()

    print("2. 测试长期记忆")
    print("-" * 60)

    # 添加一些经验
    memory_manager.long_term.add_experience("报到需要什么材料？", "需要录取通知书、身份证等")
    memory_manager.long_term.add_experience("宿舍有什么规定？", "宿舍开放时间是每天 6:00-23:00")
    memory_manager.long_term.add_experience("选课时间是什么时候？", "选课时间一般在每学期第1周")

    # 检索相关经验
    experiences = memory_manager.long_term.retrieve_relevant_experiences("报到材料")
    print(f"相关经验: {len(experiences)} 条")
    for i, exp in enumerate(experiences, 1):
        print(f"  {i}. {exp['content'][:80]}...")
    print()

    print("3. 测试整合记忆")
    print("-" * 60)

    # 获取整合的上下文
    full_context = memory_manager.get_context(messages, "报到材料")
    print("短期上下文:")
    print(full_context["short_term"])
    print()
    print("长期上下文:")
    print(full_context["long_term"])
    print()

    print("=" * 60)
    print("✅ 记忆管理测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_memory()
