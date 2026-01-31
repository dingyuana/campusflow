"""
Day 7: 长期记忆存储系统
学生画像存储与跨会话记忆管理
"""

from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from typing import Dict, Any, Optional
import json
import time


class StudentProfileStore:
    """学生画像存储（长期记忆）"""
    
    def __init__(self):
        # 生产环境应使用 PostgresStore 或 RedisStore
        self.store = InMemoryStore()
    
    def update_profile(self, user_id: str, key: str, value: Any):
        """
        更新学生画像字段
        
        Args:
            user_id: 用户ID
            key: 字段名
            value: 字段值
        """
        namespace = (user_id, "profile")
        
        # 获取现有资料
        existing = self.store.get(namespace, key)
        if existing:
            data = existing.value
            if isinstance(data, dict) and isinstance(value, dict):
                data.update(value)  # 合并字典
            else:
                data = value  # 覆盖
        else:
            data = value
        
        # 保存
        self.store.put(namespace, key, data)
    
    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """
        获取完整学生画像
        
        Args:
            user_id: 用户ID
            
        Returns:
            学生画像字典
        """
        namespace = (user_id, "profile")
        items = self.store.search(namespace)
        
        profile = {}
        for item in items:
            profile[item.key] = item.value
        
        return profile
    
    def add_memory(self, user_id: str, memory: str, importance: int = 1):
        """
        添加自然语言记忆
        
        Args:
            user_id: 用户ID
            memory: 记忆内容
            importance: 重要性等级
        """
        namespace = (user_id, "memories")
        memories = self.store.get(namespace, "facts")
        
        if not memories:
            memories = {"facts": []}
        else:
            memories = memories.value
        
        memories["facts"].append({
            "content": memory,
            "importance": importance,
            "timestamp": time.time()
        })
        
        self.store.put(namespace, "facts", memories)
    
    def get_memories(self, user_id: str, limit: int = 10) -> list:
        """
        获取用户记忆
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            记忆列表
        """
        namespace = (user_id, "memories")
        memories = self.store.get(namespace, "facts")
        
        if not memories:
            return []
        
        facts = memories.value.get("facts", [])
        # 按重要性排序
        facts.sort(key=lambda x: x["importance"], reverse=True)
        return facts[:limit]


# 全局实例
profile_store = StudentProfileStore()


if __name__ == "__main__":
    # 测试
    user_id = "student_2024001"
    
    # 更新画像
    profile_store.update_profile(user_id, "major", "计算机科学")
    profile_store.update_profile(user_id, "dormitory", "A1-301")
    profile_store.update_profile(user_id, "preferences", {"library": "东馆", "payment": "支付宝"})
    
    # 添加记忆
    profile_store.add_memory(user_id, "询问过奖学金政策", importance=2)
    profile_store.add_memory(user_id, "偏好图书馆东馆", importance=1)
    
    # 查看画像
    profile = profile_store.get_profile(user_id)
    print(f"👤 学生 {user_id} 画像：")
    print(json.dumps(profile, ensure_ascii=False, indent=2))
    
    # 查看记忆
    memories = profile_store.get_memories(user_id)
    print(f"\n📝 记忆：")
    for m in memories:
        print(f"  - {m['content']} (重要性: {m['importance']})")
