"""
Day 11: 监督者架构 Supervisor

多 Agent 协同：
- 咨询 Agent ( campus_tools )
- RAG Agent ( rag_utils )
- 后勤 Agent ( mcp_server )
"""

from typing import List, Any
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from tools.campus_tools import get_campus_tools
from utils.rag_utils import RAGUtils
from mcp_server.campus_server import get_mcp_tools


class SupervisorAgent:
    """监督者 Agent - 路由到子 Agent"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        
        # 创建子 Agent
        self.consult_agent = self._create_consult_agent()
        self.rag_agent = self._create_rag_agent()
        self.service_agent = self._create_service_agent()
        
        # 意图映射
        self.intent_map = {
            "location": self.consult_agent,
            "contact": self.consult_agent,
            "policy": self.rag_agent,
            "academic": self.service_agent,
            "payment": self.service_agent,
            "dorm": self.service_agent,
        }
    
    def _create_consult_agent(self):
        """创建咨询 Agent"""
        return create_react_agent(
            model=self.llm,
            tools=get_campus_tools(),
            prompt="你是校园咨询助手，回答地点和联系方式相关问题"
        )
    
    def _create_rag_agent(self):
        """创建 RAG Agent"""
        return create_react_agent(
            model=self.llm,
            tools=[],  # RAG 通过检索器实现
            prompt="你是校园政策专家，基于文档回答政策问题"
        )
    
    def _create_service_agent(self):
        """创建服务 Agent"""
        return create_react_agent(
            model=self.llm,
            tools=get_mcp_tools(),
            prompt="你是校务助手，处理教务/财务/宿管相关业务"
        )
    
    def route(self, query: str) -> str:
        """路由决策"""
        # 简单关键词路由
        if any(kw in query for kw in ["哪里", "在哪", "怎么走", "位置"]):
            return "location"
        elif any(kw in query for kw in ["电话", "联系", "邮箱", "办公室"]):
            return "contact"
        elif any(kw in query for kw in ["规定", "政策", "手册", "制度"]):
            return "policy"
        elif any(kw in query for kw in ["成绩", "学分", "选课", "学籍"]):
            return "academic"
        elif any(kw in query for kw in ["缴费", "学费", "欠费", "钱"]):
            return "payment"
        elif any(kw in query for kw in ["宿舍", "住宿", "室友", "房间"]):
            return "dorm"
        else:
            return "consult"
    
    def invoke(self, query: str):
        """执行查询"""
        intent = self.route(query)
        agent = self.intent_map.get(intent, self.consult_agent)
        
        return agent.invoke({"messages": [{"role": "user", "content": query}]})
