# MCP 模型上下文协议详解

## 📋 概述

MCP（Model Context Protocol，模型上下文协议）是 Anthropic 推出的开放协议标准，旨在为 AI 模型提供标准化的上下文管理能力。它允许 AI 助手安全地连接本地数据源和远程服务，实现工具调用、资源访问和提示模板等功能。

### 为什么选择 MCP？

| 特性 | 说明 |
|------|------|
| **标准化** | 统一的协议标准，跨模型、跨平台兼容 |
| **安全性** | 细粒度权限控制，用户可批准每个操作 |
| **可扩展** | 模块化架构，易于添加新的数据源和工具 |
| **双向通信** | 支持服务器向客户端发送请求和通知 |
| **本地优先** | 支持本地文件、数据库等敏感数据的安全访问 |

---

## 🏗️ 核心概念

### 1. 架构图

```
┌─────────────────────────────────────────────────────────┐
│                     MCP Host                            │
│                   (AI 应用/IDE)                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ MCP Client  │    │ MCP Client  │    │ MCP Client  │ │
│  │   (工具)     │    │   (文件)    │    │   (数据库)  │ │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘ │
│         │                  │                  │        │
│         └──────────────────┼──────────────────┘        │
│                            │                          │
└────────────────────────────┼──────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       ┌────────────┐ ┌────────────┐ ┌────────────┐
       │ MCP Server │ │ MCP Server │ │ MCP Server │
       │  (工具服务) │ │  (文件系统) │ │ (PostgreSQL)│
       └────────────┘ └────────────┘ └────────────┘
```

### 2. 核心组件

| 组件 | 说明 | 类比 |
|------|------|------|
| **Host** | 运行 AI 的应用程序（如 IDE、聊天工具） | 浏览器 |
| **Client** | Host 内的 MCP 客户端连接 | HTTP 客户端 |
| **Server** | 提供上下文能力的服务 | Web 服务 |

### 3. 协议基础

```python
# MCP 使用 JSON-RPC 2.0 进行通信
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "search_database",
        "arguments": {"query": "学生信息"}
    }
}

# 响应格式
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "content": [{"type": "text", "text": "查询结果..."}]
    }
}
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 MCP Python SDK
pip install mcp

# 或使用 uv（更快）
uv add mcp
```

### 2. 创建 MCP Server

```python
"""
Campus MCP Server
提供校园系统相关的工具和资源
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
    Resource,
    LoggingLevel
)
import json

# 创建服务器
app = Server("campus-server")

# ========== 工具定义 ==========

@app.list_tools()
async def list_tools():
    """列出所有可用工具"""
    return [
        Tool(
            name="query_student",
            description="查询学生信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "学生学号"
                    }
                },
                "required": ["student_id"]
            }
        ),
        Tool(
            name="search_courses",
            description="搜索课程",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词"
                    }
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="get_campus_news",
            description="获取校园新闻",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "返回条数",
                        "default": 5
                    }
                }
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """执行工具调用"""
    
    if name == "query_student":
        student_id = arguments.get("student_id")
        # 模拟查询
        result = {
            "id": student_id,
            "name": "张三",
            "major": "计算机科学",
            "grade": 2024
        }
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    
    elif name == "search_courses":
        keyword = arguments.get("keyword")
        # 模拟搜索
        courses = [
            {"code": "CS101", "name": f"{keyword}基础", "credit": 3},
            {"code": "CS102", "name": f"{keyword}进阶", "credit": 4}
        ]
        return [TextContent(type="text", text=json.dumps(courses, ensure_ascii=False))]
    
    elif name == "get_campus_news":
        limit = arguments.get("limit", 5)
        # 模拟新闻
        news = [
            {"title": "2025校园科技节即将开幕", "date": "2025-03-01"},
            {"title": "图书馆延长开放时间", "date": "2025-03-02"}
        ][:limit]
        return [TextContent(type="text", text=json.dumps(news, ensure_ascii=False))]
    
    else:
        raise ValueError(f"未知工具: {name}")

# ========== 资源定义 ==========

@app.list_resources()
async def list_resources():
    """列出所有可用资源"""
    return [
        Resource(
            uri="campus://students/list",
            name="学生列表",
            mimeType="application/json",
            description="所有学生的基本信息"
        ),
        Resource(
            uri="campus://courses/catalog",
            name="课程目录",
            mimeType="application/json",
            description="本学期所有课程"
        ),
        Resource(
            uri="file:///campus/policies/handbook.pdf",
            name="学生手册",
            mimeType="application/pdf",
            description="校园政策和规定"
        )
    ]

@app.read_resource()
async def read_resource(uri: str):
    """读取资源内容"""
    
    if uri == "campus://students/list":
        students = [
            {"id": "2024001", "name": "张三", "major": "CS"},
            {"id": "2024002", "name": "李四", "major": "AI"}
        ]
        return json.dumps(students, ensure_ascii=False)
    
    elif uri == "campus://courses/catalog":
        courses = [
            {"code": "CS101", "name": "数据结构", "credit": 3},
            {"code": "AI201", "name": "机器学习", "credit": 4}
        ]
        return json.dumps(courses, ensure_ascii=False)
    
    else:
        raise ValueError(f"未知资源: {uri}")

# ========== 启动服务器 ==========

async def main():
    """主函数"""
    # 使用 stdio 传输方式
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 3. 创建 MCP Client

```python
"""
MCP Client 示例
连接到 Campus MCP Server 并使用其工具
"""

from mcp.client import Client
from mcp.client.stdio import stdio_client
from mcp.types import TextContent
import asyncio
import json

async def use_mcp_server():
    """使用 MCP Server"""
    
    # 服务器配置
    server_params = {
        "command": "python",
        "args": ["campus_server.py"]
    }
    
    # 建立连接
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with Client(read_stream, write_stream) as client:
            
            # 1. 获取可用工具列表
            tools = await client.list_tools()
            print("可用工具:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # 2. 调用工具
            print("\n查询学生信息:")
            result = await client.call_tool(
                "query_student",
                {"student_id": "2024001"}
            )
            for content in result:
                if isinstance(content, TextContent):
                    print(json.loads(content.text))
            
            # 3. 搜索课程
            print("\n搜索课程:")
            result = await client.call_tool(
                "search_courses",
                {"keyword": "人工智能"}
            )
            for content in result:
                if isinstance(content, TextContent):
                    print(json.loads(content.text))
            
            # 4. 获取资源
            print("\n获取学生列表资源:")
            resource = await client.read_resource("campus://students/list")
            print(json.loads(resource))

if __name__ == "__main__":
    asyncio.run(use_mcp_server())
```

---

## 🎯 核心功能详解

### 1. 工具（Tools）

工具是 MCP 的核心功能，允许 AI 模型执行操作和获取信息。

```python
from mcp.types import Tool

# 工具定义示例
tools = [
    Tool(
        name="query_database",           # 工具名称
        description="查询校园数据库",    # 工具描述（给 AI 看的）
        inputSchema={                    # JSON Schema 定义参数
            "type": "object",
            "properties": {
                "table": {
                    "type": "string",
                    "enum": ["students", "courses", "teachers"],
                    "description": "要查询的表"
                },
                "conditions": {
                    "type": "object",
                    "description": "查询条件"
                },
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "description": "返回条数限制"
                }
            },
            "required": ["table"]
        }
    ),
    Tool(
        name="send_notification",
        description="发送通知给学生",
        inputSchema={
            "type": "object",
            "properties": {
                "student_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "学生 ID 列表"
                },
                "message": {
                    "type": "string",
                    "description": "通知内容"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "normal", "high"],
                    "default": "normal"
                }
            },
            "required": ["student_ids", "message"]
        }
    )
]
```

### 2. 资源（Resources）

资源表示服务器可以提供给 AI 的数据源。

```python
from mcp.types import Resource

# 资源定义示例
resources = [
    Resource(
        uri="campus://data/students.json",    # 资源 URI
        name="学生数据",                       # 资源名称
        mimeType="application/json",          # MIME 类型
        description="所有学生的完整信息",      # 描述
        size=1024000                          # 资源大小（可选）
    ),
    Resource(
        uri="file:///campus/docs/handbook.pdf",
        name="学生手册",
        mimeType="application/pdf",
        description="校园规章制度文档"
    ),
    Resource(
        uri="postgres://localhost/campus/students",
        name="学生数据库",
        mimeType="application/vnd.postgresql",
        description="PostgreSQL 学生表"
    )
]
```

### 3. 提示模板（Prompts）

预定义的提示模板，帮助 AI 更好地完成任务。

```python
from mcp.types import Prompt

# 提示模板定义
prompts = [
    Prompt(
        name="student_query",
        description="查询学生信息",
        arguments=[
            {
                "name": "student_name",
                "description": "学生姓名",
                "required": True
            }
        ]
    ),
    Prompt(
        name="course_recommendation",
        description="课程推荐",
        arguments=[
            {
                "name": "major",
                "description": "专业",
                "required": True
            },
            {
                "name": "grade",
                "description": "年级",
                "required": False
            }
        ]
    )
]

# 实现提示模板
@app.get_prompt()
async def get_prompt(name: str, arguments: dict):
    """获取提示模板内容"""
    
    if name == "student_query":
        student_name = arguments.get("student_name")
        return {
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"请查询学生 {student_name} 的详细信息，包括：\n"
                               f"1. 基本信息（学号、专业、年级）\n"
                               f"2. 已选课程\n"
                               f"3. 成绩情况\n"
                               f"4. 任何特殊情况或备注"
                    }
                }
            ]
        }
    
    elif name == "course_recommendation":
        major = arguments.get("major")
        grade = arguments.get("grade", "all")
        
        return {
            "messages": [
                {
                    "role": "system",
                    "content": {
                        "type": "text",
                        "text": "你是一位专业的课程顾问，熟悉各个专业的课程设置。"
                    }
                },
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"请为 {major} 专业{grade if grade != 'all' else ''}的学生推荐合适的课程，\n"
                               f"并说明推荐理由。"
                    }
                }
            ]
        }
```

---

## 🔌 传输方式

### 1. stdio（标准输入输出）

适用于本地进程间通信。

```python
from mcp.server.stdio import stdio_server
from mcp.client.stdio import stdio_client

# Server
async with stdio_server() as (read_stream, write_stream):
    await app.run(read_stream, write_stream, options)

# Client
server_params = {
    "command": "python",
    "args": ["server.py"],
    "env": {"API_KEY": "secret"}
}

async with stdio_client(server_params) as (read, write):
    async with Client(read, write) as client:
        # 使用 client...
```

### 2. HTTP with SSE

适用于网络服务。

```python
from mcp.server.sse import sse_server

# HTTP Server
app = Server("http-server")

@app.route("/mcp")
async def mcp_endpoint(request):
    """MCP HTTP 端点"""
    # 处理 JSON-RPC 请求
    pass

# 启动 HTTP 服务
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

fastapi_app = FastAPI()

@fastapi_app.post("/mcp")
async def handle_post(request: Request):
    """处理客户端请求"""
    data = await request.json()
    # 处理 JSON-RPC 请求...
    return JSONResponse(result)

@fastapi_app.get("/mcp")
async def handle_get(request: Request):
    """SSE 流"""
    async def event_stream():
        # 发送服务器事件...
        pass
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )
```

---

## 🎓 CampusFlow MCP 实战

### 校园智能体 MCP Server

```python
"""
CampusFlow MCP Server
为校园智能体提供统一的工具和资源接口
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
    Resource,
    Prompt
)
from typing import Any
import json
import asyncio

# 创建服务器
app = Server("campusflow-mcp")

# 模拟数据存储
campus_data = {
    "students": {
        "2024001": {"name": "张三", "major": "CS", "grade": 90},
        "2024002": {"name": "李四", "major": "AI", "grade": 85}
    },
    "courses": {
        "CS101": {"name": "数据结构", "teacher": "王老师", "credit": 3},
        "AI201": {"name": "机器学习", "teacher": "李老师", "credit": 4}
    },
    "news": [
        {"title": "科技节开幕", "date": "2025-03-15"},
        {"title": "选课通知", "date": "2025-03-10"}
    ]
}

# ========== 工具实现 ==========

@app.list_tools()
async def list_tools():
    """列出可用工具"""
    return [
        Tool(
            name="campus_query",
            description="通用校园信息查询",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["student", "course", "news"],
                        "description": "查询类型"
                    },
                    "id": {
                        "type": "string",
                        "description": "对象 ID"
                    }
                },
                "required": ["type"]
            }
        ),
        Tool(
            name="knowledge_search",
            description="搜索校园知识库",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询"
                    },
                    "source": {
                        "type": "string",
                        "enum": ["rag", "graph", "all"],
                        "default": "all"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="calculate_grade",
            description="计算绩点",
            inputSchema={
                "type": "object",
                "properties": {
                    "scores": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "成绩列表"
                    },
                    "credits": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "学分列表"
                    }
                },
                "required": ["scores", "credits"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    """执行工具调用"""
    
    if name == "campus_query":
        query_type = arguments.get("type")
        obj_id = arguments.get("id")
        
        if query_type == "student" and obj_id:
            result = campus_data["students"].get(obj_id, {})
        elif query_type == "course" and obj_id:
            result = campus_data["courses"].get(obj_id, {})
        elif query_type == "news":
            result = campus_data["news"]
        else:
            result = {"error": "无效的查询参数"}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False)
        )]
    
    elif name == "knowledge_search":
        query = arguments.get("query", "")
        source = arguments.get("source", "all")
        
        # 模拟搜索
        results = []
        if source in ["rag", "all"]:
            results.append({"source": "知识库", "content": f"关于'{query}'的政策信息..."})
        if source in ["graph", "all"]:
            results.append({"source": "知识图谱", "content": f"关于'{query}'的关系信息..."})
        
        return [TextContent(
            type="text",
            text=json.dumps(results, ensure_ascii=False)
        )]
    
    elif name == "calculate_grade":
        scores = arguments.get("scores", [])
        credits = arguments.get("credits", [])
        
        if len(scores) != len(credits):
            return [TextContent(
                type="text",
                text=json.dumps({"error": "成绩和学分数量不匹配"}, ensure_ascii=False)
            )]
        
        # 计算加权平均绩点
        total_score = sum(s * c for s, c in zip(scores, credits))
        total_credit = sum(credits)
        gpa = total_score / total_credit if total_credit > 0 else 0
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "gpa": round(gpa, 2),
                "total_credits": total_credit
            }, ensure_ascii=False)
        )]
    
    else:
        raise ValueError(f"未知工具: {name}")

# ========== 资源实现 ==========

@app.list_resources()
async def list_resources():
    """列出可用资源"""
    return [
        Resource(
            uri="campusflow://students/all",
            name="全部学生",
            mimeType="application/json",
            description="所有学生信息"
        ),
        Resource(
            uri="campusflow://courses/all",
            name="全部课程",
            mimeType="application/json",
            description="所有课程信息"
        ),
        Resource(
            uri="campusflow://policies/handbook",
            name="学生手册",
            mimeType="text/markdown",
            description="校园规章制度"
        )
    ]

@app.read_resource()
async def read_resource(uri: str) -> str:
    """读取资源"""
    
    if uri == "campusflow://students/all":
        return json.dumps(campus_data["students"], ensure_ascii=False)
    
    elif uri == "campusflow://courses/all":
        return json.dumps(campus_data["courses"], ensure_ascii=False)
    
    elif uri == "campusflow://policies/handbook":
        return """# 校园规章制度

## 1. 报到规定
新生需在规定时间内完成报到注册...

## 2. 选课规定
学生应在每学期初完成选课...

## 3. 宿舍规定
宿舍门禁时间为晚上11点...
"""
    
    else:
        raise ValueError(f"未知资源: {uri}")

# ========== 提示模板实现 ==========

@app.list_prompts()
async def list_prompts():
    """列出提示模板"""
    return [
        Prompt(
            name="student_helper",
            description="学生助手对话模板",
            arguments=[
                {
                    "name": "student_name",
                    "description": "学生姓名",
                    "required": True
                },
                {
                    "name": "context",
                    "description": "对话上下文",
                    "required": False
                }
            ]
        ),
        Prompt(
            name="course_advisor",
            description="课程顾问模板",
            arguments=[
                {
                    "name": "major",
                    "description": "专业",
                    "required": True
                }
            ]
        )
    ]

@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> dict:
    """获取提示模板"""
    
    if name == "student_helper":
        student_name = arguments.get("student_name")
        context = arguments.get("context", "")
        
        messages = [
            {
                "role": "system",
                "content": {
                    "type": "text",
                    "text": "你是 CampusFlow 智慧校园助手，专门帮助学生解决校园生活中的各种问题。"
                }
            }
        ]
        
        if context:
            messages.append({
                "role": "assistant",
                "content": {"type": "text", "text": context}
            })
        
        messages.append({
            "role": "user",
            "content": {
                "type": "text",
                "text": f"你好，我是 {student_name}，有一些问题想咨询..."
            }
        })
        
        return {"messages": messages}
    
    elif name == "course_advisor":
        major = arguments.get("major")
        
        return {
            "messages": [
                {
                    "role": "system",
                    "content": {
                        "type": "text",
                        "text": "你是一位专业的课程顾问，熟悉各个专业的培养方案和课程设置。"
                    }
                },
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"我是 {major} 专业的学生，请为我推荐合适的课程。"
                    }
                }
            ]
        }

# ========== 启动 ==========

async def main():
    """启动 MCP Server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    print("🚀 启动 CampusFlow MCP Server")
    asyncio.run(main())
```

---

## 📚 学习资源

### 官方资源
- MCP 官方文档：https://modelcontextprotocol.io/
- MCP 规范：https://modelcontextprotocol.io/specification
- MCP Python SDK：https://github.com/modelcontextprotocol/python-sdk

### 推荐阅读
- 《MCP 协议详解》
- 《AI 助手架构设计》
- 《LLM 工具调用最佳实践》

---

**文档创建时间**：2026-01-30
**文档维护者**：CampusFlow 项目组
