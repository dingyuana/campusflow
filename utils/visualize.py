"""
Day 1: ReAct 流程可视化工具
提供调试和可视化功能
"""

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage


def print_react_trace(messages):
    """
    可视化 ReAct 的思考-行动-观察链
    
    Args:
        messages: Agent 执行的消息列表
    """
    print("\n" + "="*50)
    print("🧠 ReAct 执行链路可视化")
    print("="*50)
    
    for i, msg in enumerate(messages):
        if msg.type == "human":
            print(f"\n{i}. 👤 用户输入: {msg.content}")
        elif msg.type == "ai":
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                tool_name = msg.tool_calls[0]["name"]
                args = msg.tool_calls[0]["args"]
                print(f"{i}. 🔧 Action: 调用 {tool_name}，参数: {args}")
            else:
                print(f"{i}. 💬 Final Answer: {msg.content}")
        elif msg.type == "tool":
            print(f"{i}. 📊 Observation: {msg.content[:80]}...")
    print("="*50)


def format_message_for_display(message: BaseMessage) -> str:
    """
    格式化消息用于显示
    
    Args:
        message: LangChain 消息对象
        
    Returns:
        格式化后的字符串
    """
    if isinstance(message, HumanMessage):
        return f"👤 用户: {message.content}"
    elif isinstance(message, AIMessage):
        if hasattr(message, "tool_calls") and message.tool_calls:
            tool_info = message.tool_calls[0]
            return f"🤖 AI [调用 {tool_info['name']}]: {message.content[:100]}..."
        return f"🤖 AI: {message.content}"
    elif isinstance(message, ToolMessage):
        return f"🔧 工具结果: {message.content[:100]}..."
    else:
        return f"📄 {message.type}: {message.content[:100]}..."


def generate_mermaid_graph(nodes, edges, title="ReAct Agent 流程"):
    """
    生成 Mermaid 流程图代码
    
    Args:
        nodes: 节点列表 [(name, label), ...]
        edges: 边列表 [(from, to, condition), ...]
        title: 图表标题
        
    Returns:
        Mermaid 代码字符串
    """
    mermaid_code = f"""graph TD
    A[开始] --> B[接收用户输入]
    B --> C{{是否需要工具?}}
    C -->|是| D[生成 Thought]
    D --> E[调用工具 Action]
    E --> F[获取 Observation]
    F --> C
    C -->|否| G[生成最终回答]
    G --> H[结束]
    """
    
    print(f"\n📊 {title}")
    print(mermaid_code)
    return mermaid_code
