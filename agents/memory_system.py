"""
Day 7: 记忆系统架构

实现：
- 短期记忆 (Thread 级 Checkpointer)
- 长期记忆 (User 级 Store)
- 学生画像自动构建
"""

import os
from typing import Dict, Any, List, Optional
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage


class StudentProfile:
    """学生画像"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.profile = {
            "major": None,
            "hometown": None,
            "preferences": [],
            "interaction_count": 0
        }
    
    def update(self, key: str, value: Any):
        """更新画像"""
        self.profile[key] = value
    
    def add_preference(self, pref: str):
        """添加偏好"""
        if pref not in self.profile["preferences"]:
            self.profile["preferences"].append(pref)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            **self.profile
        }


class MemoryManager:
    """记忆管理器"""
    
    def __init__(self):
        # 短期记忆：Checkpointer
        self.short_term = MemorySaver()
        
        # 长期记忆：用户画像存储
        self.long_term: Dict[str, StudentProfile] = {}
    
    def get_profile(self, user_id: str) -> StudentProfile:
        """获取用户画像"""
        if user_id not in self.long_term:
            self.long_term[user_id] = StudentProfile(user_id)
        return self.long_term[user_id]
    
    def extract_profile_from_message(self, user_id: str, message: str) -> bool:
        """从消息中提取画像信息"""
        profile = self.get_profile(user_id)
        
        # 简单的关键词提取
        if "来自" in message or "家乡" in message:
            # 提取家乡信息
            pass
        
        if "专业" in message or "学院" in message:
            # 提取专业信息
            pass
        
        profile.profile["interaction_count"] += 1
        return True
    
    def get_personalized_greeting(self, user_id: str) -> str:
        """生成个性化问候"""
        profile = self.get_profile(user_id)
        
        greeting = "欢迎回来"
        
        if profile.profile["hometown"]:
            greeting += f"，来自{profile.profile['hometown']}的同学"
        
        if profile.profile["major"]:
            greeting += f"，{profile.profile['major']}专业"
        
        return greeting
