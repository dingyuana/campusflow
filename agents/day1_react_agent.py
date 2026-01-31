"""
Day 1: ReAct Agent 实现
基于 LangGraph prebuilt 构建校园咨询 Agent
"""

import os
from typing import TypedDict, Annotated, Sequence
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END
from agents.tools.campus_info import (
    query_campus_library_status, 
    query_tuition_payment, 
    query_dormitory_info
)

# 工具集合
tools = [query_campus_library_status, query_tuition_payment, query_dormitory_info]

# 初始化模型（使用兼容 OpenAI 的 API）
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)

# 使用 LangGraph Prebuilt 创建 ReAct Agent
agent_executor = create_react_agent(model, tools)

def run_agent():
    print("🏫 校园咨询 Agent 已启动（输入 'exit' 退出）")
    print("示例问题：'图书馆现在开放吗？'、'我想用支付宝交学费'、'A1宿舍怎么样？'\n")
    
    while True:
        user_input = input("👤 学生：")
        if user_input.lower() == 'exit':
            break
            
        # 调用 Agent
        response = agent_executor.invoke({
            "messages": [HumanMessage(content=user_input)]
        })
        
        # 输出最后一条 AI 消息
        ai_message = response["messages"][-1]
        print(f"🤖 Agent：{ai_message.content}\n")
        
        # 打印中间步骤（用于理解 ReAct 流程）
        print("🔍 [调试信息] 执行步骤：")
        for msg in response["messages"]:
            if msg.type == "ai" and hasattr(msg, "tool_calls") and msg.tool_calls:
                print(f"  Thought: 需要调用工具 {msg.tool_calls[0]['name']}")
            elif msg.type == "tool":
                print(f"  Observation: {msg.content[:50]}...")

if __name__ == "__main__":
    run_agent()
