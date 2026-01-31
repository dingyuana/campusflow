"""
CampusFlow 校园咨询智能体
Day 1: ReAct Agent 基础实现

基于 LangGraph Prebuilt 的 create_react_agent 构建：
- 使用 ReAct（Reasoning + Acting）范式
- 工具调用机制
- 流式输出支持
- 边界情况处理

教学要点：
1. 工具描述决定 Agent 智商
2. 系统提示词配置（身份+约束）
3. 流式输出实现打字机效果
4. recursion_limit 防止无限循环
"""

import os
import sys
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from tools.campus_tools import get_campus_tools

# 加载环境变量
load_dotenv()


# -----------------------------------------------------------------------------
# ReAct Agent 配置
# -----------------------------------------------------------------------------

SYSTEM_PROMPT = """你是 CampusFlow 智慧校园助手，专门为新生和在校生提供校园咨询服务。

## 你的身份
- 名称：CampusFlow 助手
- 身份：校园智能向导
- 职责：回答校园相关问题，提供准确的校园信息

## 核心能力
1. **校园地图查询**：查询建筑物位置、开放时间、服务设施
2. **部门联系方式**：查询各部门电话、邮箱、办公时间、业务范围

## 工作原则
1. **准确性优先**：只使用工具查询到的信息回答，不编造内容
2. **友好专业**：使用礼貌、清晰的语气，适合学生群体
3. **主动引导**：当用户需求不明确时，主动询问澄清
4. **工具调用**：必须使用工具获取信息，不能直接回答

## 边界情况处理
- 如果工具返回错误或信息不足，诚实告知用户
- 如果查询到多个相关地点，列出所有选项供用户选择
- 如果用户问题与校园无关，礼貌引导回校园话题

## 示例交互
用户：图书馆在哪里？
助手：（调用 query_campus_map 工具）
助手：根据查询，图书馆位于校园中心，主楼北侧...

用户：怎么联系教务处？
助手：（调用 query_contact 工具）
助手：教务处联系方式如下：电话 021-12345678...
"""


def create_campus_agent(
    model_name: str = "gpt-4o-mini",
    temperature: float = 0.7,
    recursion_limit: int = 10
) -> Any:
    """
    创建校园咨询 ReAct Agent
    
    Args:
        model_name: LLM 模型名称
        temperature: 生成温度（创造性 vs 确定性）
        recursion_limit: 最大循环次数，防止无限循环
        
    Returns:
        编译后的 Agent 应用
    """
    print("=" * 60)
    print("🤖 创建 CampusFlow ReAct Agent")
    print("=" * 60)
    print()
    
    # 1. 获取 LLM 配置
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    
    if not api_key:
        raise ValueError("❌ 环境变量 OPENAI_API_KEY 未设置，请检查 .env 文件")
    
    # 2. 初始化 LLM
    llm_kwargs = {
        "model": model_name,
        "temperature": temperature,
        "api_key": api_key,
    }
    
    # 如果配置了代理 URL，则使用
    if base_url:
        llm_kwargs["base_url"] = base_url
        print(f"🔗 使用自定义 API 端点: {base_url}")
    
    try:
        llm = ChatOpenAI(**llm_kwargs)
        print(f"✅ LLM 初始化成功: {model_name}")
    except Exception as e:
        raise RuntimeError(f"❌ LLM 初始化失败: {e}")
    
    # 3. 获取工具列表
    tools = get_campus_tools()
    print(f"🔧 加载了 {len(tools)} 个工具:")
    for tool in tools:
        print(f"   - {tool.name}: {tool.description[:50]}...")
    
    print()
    
    # 4. 创建 ReAct Agent
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT,
    )
    
    print("✅ ReAct Agent 创建成功")
    print(f"   模型: {model_name}")
    print(f"   工具数: {len(tools)}")
    print(f"   循环限制: {recursion_limit} 次")
    print()
    
    # 5. 编译配置
    app = agent
    
    return app


def run_agent_query(
    agent: Any,
    query: str,
    thread_id: str = "default",
    stream: bool = True
) -> str:
    """
    运行 Agent 查询
    
    Args:
        agent: Agent 应用实例
        query: 用户查询文本
        thread_id: 会话 ID（用于多轮对话隔离）
        stream: 是否使用流式输出
        
    Returns:
        Agent 的完整回答
    """
    # 准备输入
    inputs = {"messages": [HumanMessage(content=query)]}
    config = {"configurable": {"thread_id": thread_id}}
    
    if stream:
        # 流式输出 - 打字机效果
        print(f"📝 用户: {query}")
        print()
        print("🤖 助手: ", end="", flush=True)
        
        full_response = ""
        try:
            for chunk in agent.stream(inputs, config, stream_mode="messages"):
                if chunk[1]["langgraph_node"] == "agent":
                    message = chunk[0]
                    if hasattr(message, "content") and message.content:
                        content = message.content
                        print(content, end="", flush=True)
                        full_response += content
            
            print()  # 换行
            print()
            
        except Exception as e:
            print(f"\n❌ 流式输出出错: {e}")
            return f"抱歉，处理您的请求时出错: {e}"
        
        return full_response
    else:
        # 非流式输出
        print(f"📝 用户: {query}")
        print()
        print("🤖 助手正在思考...")
        print()
        
        try:
            result = agent.invoke(inputs, config)
            
            # 提取最后一条 AI 消息
            messages = result["messages"]
            for msg in reversed(messages):
                if isinstance(msg, AIMessage):
                    response = msg.content
                    print(response)
                    print()
                    return response
            
            return "抱歉，我没有生成回答。"
            
        except Exception as e:
            error_msg = f"❌ 查询出错: {e}"
            print(error_msg)
            return error_msg


def run_interactive_demo():
    """
    运行交互式演示
    """
    print("=" * 60)
    print("🎓 CampusFlow 校园咨询智能体")
    print("   输入 'quit' 或 'exit' 退出")
    print("=" * 60)
    print()
    
    # 创建 Agent
    try:
        agent = create_campus_agent(
            model_name="gpt-4o-mini",
            temperature=0.7,
            recursion_limit=10
        )
    except Exception as e:
        print(f"❌ Agent 创建失败: {e}")
        return
    
    # 测试用例
    test_queries = [
        "图书馆在哪里？",
        "教务处的联系方式是什么？",
        "从宿舍到图书馆怎么走？",
        "怎么联系财务处？",
    ]
    
    print("🧪 运行预设测试用例：")
    print("-" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n【测试 {i}/{len(test_queries)}】")
        print("=" * 60)
        
        response = run_agent_query(agent, query, thread_id=f"test_{i}")
        
        print("=" * 60)
    
    print()
    print("💬 现在您可以输入自己的问题（输入 'quit' 退出）：")
    print()
    
    # 交互模式
    thread_counter = 100
    while True:
        try:
            user_input = input("📝 您: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit", "退出", "q"]:
                print()
                print("👋 再见！感谢使用 CampusFlow 助手")
                break
            
            thread_counter += 1
            run_agent_query(agent, user_input, thread_id=f"interactive_{thread_counter}")
            
        except KeyboardInterrupt:
            print()
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")


def run_simple_test():
    """
    运行简单测试（非交互式）
    """
    print("=" * 60)
    print("🧪 CampusFlow Agent 简单测试")
    print("=" * 60)
    print()
    
    # 创建 Agent
    try:
        agent = create_campus_agent(
            model_name="gpt-4o-mini",
            temperature=0.7,
            recursion_limit=10
        )
    except Exception as e:
        print(f"❌ Agent 创建失败: {e}")
        return False
    
    # 简单测试
    test_query = "图书馆在哪里？"
    print(f"📝 测试查询: {test_query}")
    print()
    print("🤖 助手回答（流式输出）:")
    print("-" * 60)
    
    response = run_agent_query(agent, test_query, thread_id="simple_test", stream=True)
    
    print("-" * 60)
    print()
    
    # 验证结果
    if "图书馆" in response and len(response) > 50:
        print("✅ 测试通过！Agent 成功返回了关于图书馆的信息")
        return True
    else:
        print("⚠️ 测试可能未完全通过，请检查输出")
        return False


if __name__ == "__main__":
    # 默认运行简单测试
    # 如果想要交互式模式，取消下面这行的注释：
    # run_interactive_demo()
    
    run_simple_test()
