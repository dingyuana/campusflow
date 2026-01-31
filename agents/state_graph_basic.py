"""
Day 5: 状态图与上下文工程
使用 StateGraph 和 PostgresSaver 实现状态持久化
"""

from typing import TypedDict, Annotated, Sequence, List, Any, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

load_dotenv()


# 定义 CampusState（强类型状态）
class CampusState(TypedDict):
    """
    智慧校园智能体状态定义

    包含：
    - messages: 对话历史
    - user_id: 用户 ID
    - current_query: 当前用户查询
    - context: 上下文信息（来自 RAG 或知识图谱）
    - next_action: 下一步行动
    """
    messages: Annotated[Sequence[BaseMessage], "add_messages"]
    user_id: str
    current_query: str
    context: dict
    next_action: str


# 定义简单的工具函数
def search_rag(query: str) -> str:
    """
    RAG 搜索工具（模拟）

    Args:
        query: 查询文本

    Returns:
        搜索结果
    """
    # 这里应该调用真实的 RAG 检索
    return f"RAG 搜索结果：{query}"


def search_knowledge_graph(query: str) -> str:
    """
    知识图谱搜索工具（模拟）

    Args:
        query: 查询文本

    Returns:
        搜索结果
    """
    # 这里应该调用真实的 Neo4j 查询
    return f"知识图谱查询结果：{query}"


# 定义节点函数
def user_query_node(state: CampusState) -> CampusState:
    """
    用户查询节点：处理用户输入

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    query = state["current_query"]
    print(f"\n🔍 用户查询: {query}")

    # 添加用户消息到历史
    state["messages"].append(HumanMessage(content=query))

    # 设置下一步行动
    state["next_action"] = "analyze_query"

    return state


def analyze_query_node(state: CampusState) -> CampusState:
    """
    查询分析节点：分析用户意图

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    query = state["current_query"]

    print("🤖 分析查询意图...")

    # 简单的意图分析（实际应使用 LLM）
    if "报到" in query or "入学" in query:
        intent = "enrollment"
    elif "选课" in query or "课程" in query:
        intent = "course"
    elif "宿舍" in query or "住宿" in query:
        intent = "dormitory"
    else:
        intent = "general"

    print(f"   意图识别: {intent}")

    # 将意图存储到上下文
    state["context"]["intent"] = intent

    # 根据意图设置下一步
    if intent in ["enrollment", "course", "dormitory"]:
        state["next_action"] = "retrieve_rag"
    else:
        state["next_action"] = "retrieve_kg"

    return state


def retrieve_rag_node(state: CampusState) -> CampusState:
    """
    RAG 检索节点：从 RAG 向量库检索相关信息

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    query = state["current_query"]

    print("📚 RAG 检索...")

    # 调用 RAG 搜索
    rag_result = search_rag(query)
    print(f"   {rag_result}")

    # 将检索结果存储到上下文
    state["context"]["rag_result"] = rag_result

    # 设置下一步
    state["next_action"] = "generate_response"

    return state


def retrieve_kg_node(state: CampusState) -> CampusState:
    """
    知识图谱检索节点：从 Neo4j 查询相关信息

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    query = state["current_query"]

    print("🕸️  知识图谱查询...")

    # 调用知识图谱查询
    kg_result = search_knowledge_graph(query)
    print(f"   {kg_result}")

    # 将查询结果存储到上下文
    state["context"]["kg_result"] = kg_result

    # 设置下一步
    state["next_action"] = "generate_response"

    return state


def generate_response_node(state: CampusState) -> CampusState:
    """
    回答生成节点：根据上下文生成回答

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    context = state["context"]
    query = state["current_query"]

    print("💬 生成回答...")

    # 简单的模拟回答（实际应使用 LLM）
    if "rag_result" in context:
        answer = f"根据RAG检索结果：{context['rag_result']}"
    elif "kg_result" in context:
        answer = f"根据知识图谱查询：{context['kg_result']}"
    else:
        answer = "抱歉，我暂时无法回答这个问题。"

    print(f"   回答: {answer}")

    # 添加 AI 回复到历史
    state["messages"].append(AIMessage(content=answer))

    # 设置下一步为结束
    state["next_action"] = "end"

    return state


def build_campus_graph() -> StateGraph:
    """
    构建校园智能体状态图

    Returns:
        StateGraph 实例
    """
    print("=" * 60)
    print("🏗️  构建校园智能体状态图")
    print("=" * 60)
    print()

    # 创建状态图
    workflow = StateGraph(CampusState)

    # 添加节点
    workflow.add_node("user_query", user_query_node)
    workflow.add_node("analyze_query", analyze_query_node)
    workflow.add_node("retrieve_rag", retrieve_rag_node)
    workflow.add_node("retrieve_kg", retrieve_kg_node)
    workflow.add_node("generate_response", generate_response_node)

    # 添加边
    workflow.add_edge(START, "user_query")
    workflow.add_edge("user_query", "analyze_query")

    # 条件边：根据意图选择检索方式
    workflow.add_conditional_edges(
        "analyze_query",
        lambda state: state["context"].get("intent", "general"),
        {
            "enrollment": "retrieve_rag",
            "course": "retrieve_rag",
            "dormitory": "retrieve_rag",
            "general": "retrieve_kg"
        }
    )

    workflow.add_edge("retrieve_rag", "generate_response")
    workflow.add_edge("retrieve_kg", "generate_response")
    workflow.add_edge("generate_response", END)

    print("✅ 状态图构建完成")
    print()
    print("节点:")
    print("  - user_query: 处理用户查询")
    print("  - analyze_query: 分析查询意图")
    print("  - retrieve_rag: RAG 向量检索")
    print("  - retrieve_kg: 知识图谱检索")
    print("  - generate_response: 生成回答")
    print()

    return workflow


def setup_postgres_saver() -> Optional[PostgresSaver]:
    """
    配置 PostgresSaver 状态持久化

    Returns:
        PostgresSaver 实例（配置成功时）或 None
    """
    print("=" * 60)
    print("💾 配置 PostgresSaver 状态持久化")
    print("=" * 60)
    print()

    # 获取数据库连接字符串
    db_url = os.getenv("SUPABASE_DB_URL")

    if not db_url:
        print("⚠️  未配置 SUPABASE_DB_URL，状态持久化将不可用")
        return None

    try:
        # 创建 PostgresSaver
        checkpointer = PostgresSaver.from_conn_string(db_url)

        # 初始化数据库表
        checkpointer.setup()

        print("✅ PostgresSaver 配置成功")
        print(f"   数据库: {db_url}")
        print()

        return checkpointer

    except Exception as e:
        print(f"❌ PostgresSaver 配置失败: {e}")
        print()
        return None


def run_demo():
    """
    运行演示
    """
    print("=" * 60)
    print("🚀 校园智能体演示")
    print("=" * 60)
    print()

    # 配置状态持久化
    checkpointer = setup_postgres_saver()

    # 构建状态图
    workflow = build_campus_graph()

    # 编译状态图
    app = workflow.compile(checkpointer=checkpointer)

    # 初始状态
    initial_state: CampusState = {
        "messages": [],
        "user_id": "test_user",
        "current_query": "新生报到需要准备什么材料？",
        "context": {},
        "next_action": ""
    }

    # 运行状态图
    print("执行查询:")
    print("-" * 60)

    try:
        # 使用可配置的 thread_id 支持多会话
        thread_id = "thread_1"

        # 执行状态图
        result = app.invoke(
            initial_state,
            config={"configurable": {"thread_id": thread_id}}
        )

        print()
        print("=" * 60)
        print("✅ 查询执行完成")
        print("=" * 60)
        print()

        # 显示最终状态
        print("最终状态:")
        print(f"  消息数量: {len(result['messages'])}")
        print(f"  查询: {result['current_query']}")
        print(f"  上下文: {result['context']}")
        print()

        # 显示对话历史
        print("对话历史:")
        print("-" * 60)
        for msg in result['messages']:
            role = "用户" if isinstance(msg, HumanMessage) else "助手"
            print(f"{role}: {msg.content}")
        print()

    except Exception as e:
        print(f"❌ 执行失败: {e}")


if __name__ == "__main__":
    run_demo()
