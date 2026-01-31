"""
Day 4: StateGraph 报到流程状态机
实现"新生报到流程"的完整状态管理
"""

from typing import TypedDict, Annotated, Optional, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
import json
from langchain_openai import ChatOpenAI
import os


# 定义状态结构
class RegistrationState(TypedDict):
    """报到流程状态结构"""
    # 基础消息（自动聚合）
    messages: Annotated[List[BaseMessage], operator.add]
    
    # 学生信息收集
    student_name: Optional[str]
    student_id: Optional[str]
    major: Optional[str]
    
    # 流程控制
    current_step: str  # 'info_collection', 'verification', 'payment', 'completed'
    is_verified: bool
    documents_ready: bool
    payment_confirmed: bool
    
    # 错误处理
    error_message: Optional[str]
    retry_count: int


# 初始化函数
def init_state() -> RegistrationState:
    """初始化状态"""
    return {
        "messages": [],
        "student_name": None,
        "student_id": None,
        "major": None,
        "current_step": "info_collection",
        "is_verified": False,
        "documents_ready": False,
        "payment_confirmed": False,
        "error_message": None,
        "retry_count": 0
    }


# 初始化模型
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)


def info_collection_node(state: RegistrationState):
    """信息收集节点：提取学生基本信息"""
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""
    
    # 使用 LLM 提取实体
    prompt = f"""从以下对话中提取学生信息，以 JSON 格式返回：
    可用字段：student_name, student_id, major
    如果某个字段未提及，使用 null。
    
    对话：{last_message}
    
    注意：只需返回 JSON，不要其他内容。
    示例：{{"student_name": "张三", "student_id": "2024001", "major": null}}
    """
    
    response = model.invoke(prompt)
    try:
        extracted = json.loads(response.content)
        return {
            "student_name": extracted.get("student_name") or state["student_name"],
            "student_id": extracted.get("student_id") or state["student_id"],
            "major": extracted.get("major") or state["major"],
            "current_step": "verification",
            "messages": [AIMessage(content=f"已记录信息：姓名 {extracted.get('student_name')}, "
                                       f"学号 {extracted.get('student_id')}")]
        }
    except:
        return {
            "error_message": "信息提取失败，请重新提供",
            "retry_count": state["retry_count"] + 1,
            "current_step": "info_collection"
        }


def verification_node(state: RegistrationState):
    """身份验证节点：模拟验证学号是否存在"""
    student_id = state["student_id"]
    
    # 模拟验证（实际应查询数据库）
    valid_ids = ["2024001", "2024002", "2024003"]
    
    if student_id in valid_ids:
        return {
            "is_verified": True,
            "current_step": "payment",
            "messages": [AIMessage(content=f"✅ 学号 {student_id} 验证通过，请完成缴费。")]
        }
    else:
        return {
            "is_verified": False,
            "error_message": "学号不存在或已被注册",
            "retry_count": state["retry_count"] + 1,
            "messages": [AIMessage(content="❌ 学号验证失败，请检查学号是否正确。")]
        }


def payment_node(state: RegistrationState):
    """缴费确认节点"""
    # 这里可以集成真实的支付 API 查询
    # 模拟：询问用户是否已完成缴费
    last_message = state["messages"][-1].content if state["messages"] else ""
    
    if "已缴费" in last_message or "完成" in last_message:
        return {
            "payment_confirmed": True,
            "current_step": "completed",
            "messages": [AIMessage(content="✅ 缴费确认完成！报到流程结束，欢迎来到校园！")]
        }
    else:
        return {
            "payment_confirmed": False,
            "current_step": "payment",
            "messages": [AIMessage(content="请前往财务处或在线平台完成学费缴纳，完成后回复'已缴费'。")]
        }


def error_handler_node(state: RegistrationState):
    """错误处理节点"""
    if state["retry_count"] > 3:
        return {
            "messages": [AIMessage(content="错误次数过多，已转接人工客服。")],
            "current_step": "error"
        }
    return {
        "messages": [AIMessage(content=f"发生错误：{state['error_message']}，请重试。")],
        "current_step": "info_collection"
    }


def route_based_on_state(state: RegistrationState) -> str:
    """条件路由函数"""
    if state.get("error_message") and state["retry_count"] > 0:
        if state["retry_count"] > 3:
            return "error_handler"
        return "info_collection"  # 重试
    
    step = state["current_step"]
    
    routing_map = {
        "info_collection": "verification",
        "verification": "payment" if state["is_verified"] else "error_handler",
        "payment": "completed" if state["payment_confirmed"] else "payment",
        "completed": END,
        "error": END
    }
    
    return routing_map.get(step, END)


# 构建图
def create_registration_workflow():
    """创建报到流程工作流"""
    workflow = StateGraph(RegistrationState)
    
    # 添加节点
    workflow.add_node("info_collection", info_collection_node)
    workflow.add_node("verification", verification_node)
    workflow.add_node("payment", payment_node)
    workflow.add_node("error_handler", error_handler_node)
    
    # 添加边
    workflow.set_entry_point("info_collection")
    
    # 条件边：从每个节点根据状态路由
    workflow.add_conditional_edges(
        "info_collection",
        route_based_on_state,
        {
            "verification": "verification",
            "error_handler": "error_handler"
        }
    )
    
    workflow.add_conditional_edges(
        "verification",
        route_based_on_state,
        {
            "payment": "payment",
            "error_handler": "error_handler"
        }
    )
    
    workflow.add_conditional_edges(
        "payment",
        route_based_on_state,
        {
            "payment": "payment",  # 自循环直到确认
            "completed": END,
            "error_handler": "error_handler"
        }
    )
    
    workflow.add_edge("error_handler", END)
    
    # 添加检查点（持久化）
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


def visualize_workflow():
    """生成 Mermaid 流程图代码"""
    mermaid_code = """
    graph TD
        A[开始] --> B[信息收集]
        B --> C{验证学号}
        C -->|成功| D[缴费确认]
        C -->|失败| E[错误处理]
        D -->|未完成| D
        D -->|已完成| F[结束]
        E -->|重试<3| B
        E -->|重试>=3| F
    """
    print(mermaid_code)
    return mermaid_code


def demo_with_interrupt():
    """演示检查点与中断恢复"""
    app = create_registration_workflow()
    
    # 配置：使用 thread_id 标识对话线程
    config = {"configurable": {"thread_id": "student_2024001"}}
    
    print("🎓 新生报到流程演示（输入 'quit' 退出，'check' 查看状态）\n")
    
    while True:
        user_input = input("👤 输入: ")
        
        if user_input == "quit":
            break
        elif user_input == "check":
            # 查看当前状态（检查点）
            state = app.get_state(config)
            print(f"📊 当前状态：{state.values}")
            continue
        
        # 运行图
        events = app.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config,
            stream_mode="values"
        )
        
        for event in events:
            if "messages" in event:
                print(f"🤖 Agent: {event['messages'][-1].content}")
            if "current_step" in event:
                print(f"   [当前步骤: {event['current_step']}]")


if __name__ == "__main__":
    # 显示流程图
    print("📊 报到流程图：")
    visualize_workflow()
    
    # 运行演示
    demo_with_interrupt()
