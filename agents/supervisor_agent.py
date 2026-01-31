"""
Day 7: 监督者模式和并行执行
实现 Supervisor Agent 和多任务并行
"""

from typing import Annotated, Sequence, List, Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing_extensions import TypedDict


# 定义共享状态
class SupervisorState(TypedDict):
    """监督者状态"""
    messages: Annotated[Sequence[BaseMessage], "add_messages"]
    next: str  # 下一个要调用的 Agent
    rag_result: str
    kg_result: str
    combined_result: str


# 定义 Agent 状态
class AgentState(TypedDict):
    """Agent 状态"""
    messages: Annotated[Sequence[BaseMessage], "add_messages"]
    query: str
    result: str


# 模拟 RAG Agent
def rag_agent_node(state: AgentState) -> AgentState:
    """
    RAG Agent 节点：处理 RAG 相关查询

    Args:
        state: Agent 状态

    Returns:
        更新后的状态
    """
    query = state["query"]
    print(f"\n📚 RAG Agent 处理查询: {query}")

    # 模拟 RAG 检索
    result = f"RAG Agent 根据知识库回答: {query}"
    print(f"   结果: {result}")

    state["result"] = result
    state["messages"].append(AIMessage(content=result))

    return state


# 模拟知识图谱 Agent
def knowledge_graph_agent_node(state: AgentState) -> AgentState:
    """
    知识图谱 Agent 节点：处理知识图谱查询

    Args:
        state: Agent 状态

    Returns:
        更新后的状态
    """
    query = state["query"]
    print(f"\n🕸️  知识图谱 Agent 处理查询: {query}")

    # 模拟图数据库查询
    result = f"知识图谱 Agent 根据图关系回答: {query}"
    print(f"   结果: {result}")

    state["result"] = result
    state["messages"].append(AIMessage(content=result))

    return state


# 模拟数据库 Agent
def database_agent_node(state: AgentState) -> AgentState:
    """
    数据库 Agent 节点：处理数据库查询

    Args:
        state: Agent 状态

    Returns:
        更新后的状态
    """
    query = state["query"]
    print(f"\n💾 数据库 Agent 处理查询: {query}")

    # 模拟数据库查询
    result = f"数据库 Agent 查询业务数据: {query}"
    print(f"   结果: {result}")

    state["result"] = result
    state["messages"].append(AIMessage(content=result))

    return state


# Supervisor Agent 决策函数
def supervisor_node(state: SupervisorState) -> SupervisorState:
    """
    Supervisor Agent 节点：决策调用哪个 Agent

    Args:
        state: Supervisor 状态

    Returns:
        更新后的状态，包含决策结果
    """
    query = state["messages"][-1].content if state["messages"] else ""

    print("\n👑 Supervisor Agent 分析查询")
    print("-" * 60)
    print(f"   查询: {query}")

    # 简单的决策逻辑（实际应使用 LLM）
    if any(keyword in query.lower() for keyword in ["报到", "入学", "材料", "手册"]):
        decision = "rag_agent"
        reason = "查询涉及报到相关，调用 RAG Agent"
    elif any(keyword in query.lower() for keyword in ["同学", "教师", "关系", "路径"]):
        decision = "kg_agent"
        reason = "查询涉及关系，调用知识图谱 Agent"
    elif any(keyword in query.lower() for keyword in ["学生", "课程", "成绩", "选课"]):
        decision = "db_agent"
        reason = "查询涉及业务数据，调用数据库 Agent"
    else:
        decision = "rag_agent"  # 默认使用 RAG
        reason = "使用默认 RAG Agent"

    print(f"   决策: {decision}")
    print(f"   原因: {reason}")
    print()

    state["next"] = decision

    return state


# 结果聚合节点
def aggregate_results_node(state: SupervisorState) -> SupervisorState:
    """
    结果聚合节点：整合所有 Agent 的结果

    Args:
        state: Supervisor 状态

    Returns:
        更新后的状态
    """
    print("\n🔄 聚合结果")
    print("-" * 60)

    rag_result = state.get("rag_result", "")
    kg_result = state.get("kg_result", "")
    db_result = state.get("combined_result", "")

    # 聚合逻辑
    combined = ""

    if rag_result:
        combined += f"{rag_result}\n"
    if kg_result:
        combined += f"{kg_result}\n"
    if db_result:
        combined += f"{db_result}\n"

    state["combined_result"] = combined

    print(f"   聚合结果: {combined[:100]}...")

    # 添加最终回答
    state["messages"].append(AIMessage(content=combined))

    return state


def build_supervisor_graph() -> StateGraph:
    """
    构建监督者模式的状态图

    Returns:
        StateGraph 实例
    """
    print("=" * 60)
    print("🏗️  构建监督者模式状态图")
    print("=" * 60)
    print()

    # 创建监督者图
    workflow = StateGraph(SupervisorState)

    # 添加节点
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("rag_agent", rag_agent_node)
    workflow.add_node("kg_agent", knowledge_graph_agent_node)
    workflow.add_node("db_agent", database_agent_node)
    workflow.add_node("aggregate", aggregate_results_node)

    # 添加边
    workflow.add_edge(START, "supervisor")

    # 条件边：Supervisor 决定
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["next"],
        {
            "rag_agent": "rag_agent",
            "kg_agent": "kg_agent",
            "db_agent": "db_agent"
        }
    )

    workflow.add_edge("rag_agent", "aggregate")
    workflow.add_edge("kg_agent", "aggregate")
    workflow.add_edge("db_agent", "aggregate")
    workflow.add_edge("aggregate", END)

    print("✅ 监督者模式图构建完成")
    print()
    print("节点:")
    print("  - supervisor: 决策调用哪个 Agent")
    print("  - rag_agent: RAG 知识检索")
    print("  - kg_agent: 知识图谱查询")
    print("  - db_agent: 业务数据库查询")
    print("  - aggregate: 聚合结果")
    print()

    return workflow


def run_supervisor_demo():
    """
    运行监督者模式演示
    """
    print("=" * 60)
    print("🚀 监督者模式演示")
    print("=" * 60)
    print()

    # 构建监督者图
    workflow = build_supervisor_graph()
    app = workflow.compile()

    # 测试查询
    test_queries = [
        "新生报到需要准备什么材料？",
        "张三的同学有哪些？",
        "查询学生 S001 的选课情况"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 60}")
        print(f"📝 查询 {i}: {query}")
        print(f"{'=' * 60}")
        print()

        # 初始状态
        initial_state: SupervisorState = {
            "messages": [HumanMessage(content=query)],
            "next": "",
            "rag_result": "",
            "kg_result": "",
            "combined_result": ""
        }

        # 执行图
        try:
            result = app.invoke(initial_state)

            # 显示最终结果
            print("\n最终回答:")
            print("-" * 60)
            final_message = result["messages"][-1]
            print(final_message.content)
            print()

        except Exception as e:
            print(f"❌ 执行失败: {e}")


if __name__ == "__main__":
    run_supervisor_demo()
