"""
Day 9: LangGraph 与 MCP 桥接层
将 MCP Tool 转为 LangChain Tool
"""

from langchain_core.tools import Tool
from typing import List
import asyncio


class MCPClient:
    """MCP 客户端封装（简化版）"""
    
    def __init__(self):
        self.tools = []
        self.connected = False
    
    async def connect(self, server_script_path: str):
        """
        连接到 MCP Server（Stdio 模式）
        实际应用中应使用 mcp.ClientSession
        """
        print(f"🔄 连接到 MCP Server: {server_script_path}")
        # 模拟连接成功
        self.connected = True
        
        # 模拟加载工具
        self.tools = [
            {
                "name": "check_tuition_status",
                "description": "查询学生缴费状态",
                "args": ["student_id"]
            },
            {
                "name": "assign_dormitory",
                "description": "分配宿舍",
                "args": ["student_id", "building", "room"]
            },
            {
                "name": "query_course_enrollment",
                "description": "查询课程选课人数",
                "args": ["course_id"]
            }
        ]
        
        print(f"✅ 已加载 {len(self.tools)} 个 MCP 工具")
        return self.tools
    
    async def call_tool(self, tool_name: str, arguments: dict):
        """调用特定工具（模拟实现）"""
        if not self.connected:
            raise RuntimeError("未连接到 MCP Server")
        
        # 模拟工具调用
        if tool_name == "check_tuition_status":
            student_id = arguments.get("student_id", "")
            # 简单模拟
            if student_id in ["2024001", "2024002"]:
                return {"student_id": student_id, "tuition_status": "已缴费"}
            return {"error": "学生不存在"}
        
        elif tool_name == "assign_dormitory":
            return {
                "success": True,
                "student_id": arguments.get("student_id"),
                "dormitory": f"{arguments.get('building')}-{arguments.get('room')}"
            }
        
        elif tool_name == "query_course_enrollment":
            course_id = arguments.get("course_id", "")
            return {
                "course_id": course_id,
                "course_name": "Python编程" if course_id == "CS101" else "数据结构",
                "enrolled": 85,
                "capacity": 100,
                "status": "可选课"
            }
        
        return {"error": "未知工具"}


def create_sync_tools(server_path: str) -> List[Tool]:
    """
    将异步 MCP 工具转为同步 LangChain Tools
    
    Args:
        server_path: MCP Server 脚本路径
        
    Returns:
        LangChain Tool 列表
    """
    client = MCPClient()
    
    # 模拟连接（实际应使用 asyncio.run(client.connect(server_path))）
    tools_info = [
        {
            "name": "check_tuition_status",
            "description": "查询学生缴费状态，输入学号如'2024001'",
        },
        {
            "name": "assign_dormitory",
            "description": "分配宿舍，需要学号、楼栋和房间号",
        },
        {
            "name": "query_course_enrollment",
            "description": "查询课程选课情况，输入课程代码如'CS101'",
        }
    ]
    
    # 包装为 LangChain Tool
    langchain_tools = []
    
    def make_tool_func(tool_name):
        def tool_func(args):
            # 模拟异步调用
            return f"模拟调用 {tool_name}，参数: {args}"
        return tool_func
    
    for tool_info in tools_info:
        langchain_tools.append(
            Tool(
                name=tool_info["name"],
                description=tool_info["description"],
                func=make_tool_func(tool_info["name"]),
            )
        )
    
    return langchain_tools


if __name__ == "__main__":
    # 测试
    print("🧪 测试 MCP 桥接")
    tools = create_sync_tools("mcp_servers/campus_service.py")
    print(f"✅ 已加载 {len(tools)} 个工具")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
