"""
Day 9: MCP 集成 Agent
结合 MCP 工具与现有工具的综合 Agent
"""

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os


# 加载 MCP 工具
from agents.mcp_bridge import create_sync_tools
from agents.tools.campus_info import query_campus_library_status


# MCP 工具
mcp_tools = create_sync_tools("mcp_servers/campus_service.py")

# 本地工具
local_tools = [query_campus_library_status]

# 合并工具
all_tools = local_tools + mcp_tools

# 初始化模型
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)

# 创建 Agent
mcp_agent = create_react_agent(
    model=model,
    tools=all_tools,
    system_prompt="""你是校园助手，可以访问以下系统：
- 财务系统：查询缴费状态
- 宿管系统：分配宿舍
- 教务系统：查询选课情况
- 校园信息：图书馆等

请根据学生需求调用相应工具。"""
)


def handle_registration_with_mcp(student_input: str):
    """
    处理包含外部系统调用的报到请求
    
    Args:
        student_input: 学生输入
        
    Returns:
        Agent 回复
    """
    result = mcp_agent.invoke({
        "messages": [HumanMessage(content=student_input)]
    })
    return result["messages"][-1].content


if __name__ == "__main__":
    # 测试
    print("🧪 测试 MCP 集成 Agent\n")
    
    test_cases = [
        "查询我的缴费状态，学号2024001",
        "给我分配A1楼的宿舍",
        "CS101课程还有名额吗？",
        "图书馆现在开放吗？"
    ]
    
    for question in test_cases:
        print(f"👤 学生：{question}")
        # 注意：实际运行需要连接真实的 MCP Server
        # response = handle_registration_with_mcp(question)
        print(f"🤖 Agent：[需要连接 MCP Server 才能获取真实结果]")
        print()
