# LangGraph 多智能体系统详解

## 📋 概述

LangGraph 是 LangChain 生态系统中的工作流编排框架，专门用于构建复杂的多智能体（Multi-Agent）系统。它通过状态图（State Graph）的方式，让多个智能体能够协作完成复杂任务。

### 为什么选择 LangGraph？

| 特性 | 说明 |
|------|------|
| **可视化工作流** | 通过图形定义智能体协作流程 |
| **状态管理** | 内置强大的状态管理机制，支持断点续传 |
| **灵活路由** | 支持条件边（Conditional Edges），动态决定执行路径 |
| **人机协作** | 支持人工干预（Human-in-the-loop） |
| **持久化** | 内置检查点（Checkpoint）机制，支持长时运行任务 |

---

## 🏗️ 核心概念

### 1. 状态图（State Graph）

```
┌─────────────┐         ┌─────────────┐
│   START     │────────▶│  Supervisor │
└─────────────┘         └──────┬──────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │ RAG Agent   │     │ Graph Agent │     │ Search Agent│
    └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
           │                   │                   │
           └───────────────────┼───────────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │   END       │
                        └─────────────┘
```

### 2. 核心组件

```python
from typing import TypedDict, Annotated, List
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

# 1. 状态定义（State）
class AgentState(TypedDict):
    """
    智能体状态定义
    
    所有节点共享这个状态，用于传递数据
    """
    messages: Annotated[List[AnyMessage], add_messages]  # 对话历史
    next: str                                            # 下一个执行的节点
    task: str                                           # 当前任务
    results: dict                                       # 执行结果

# 2. 节点（Nodes）
def supervisor_node(state: AgentState):
    """监督者节点：决定哪个智能体执行"""
    pass

def rag_agent_node(state: AgentState):
    """RAG 智能体节点：处理知识检索"""
    pass

# 3. 边（Edges）
# - 普通边：固定流向
# - 条件边：根据状态动态决定流向
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 LangGraph 及相关依赖
pip install langgraph langchain langchain-openai

# 国内镜像加速
pip install langgraph langchain langchain-openai --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 基础状态图

```python
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# 定义状态
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 创建图构建器
builder = StateGraph(State)

# 定义节点函数
def chatbot(state: State):
    """简单的聊天机器人节点"""
    return {"messages": [AIMessage(content="你好！我是智能助手。")]}

# 添加节点
builder.add_node("chatbot", chatbot)

# 添加边（定义流程）
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# 编译图
graph = builder.compile()

# 执行
result = graph.invoke({"messages": [HumanMessage(content="你好！")]})
print(result)
```

### 3. 可视化图结构

```python
# 生成 Mermaid 图表
graph.get_graph().print_ascii()

# 或者保存为 PNG（需要安装 graphviz）
graph.get_graph().draw_mermaid_png(output_file_path="workflow.png")
```

---

## 🎯 多智能体架构模式

### 模式 1：Supervisor（监督者模式）

这是最常用的多智能体模式，一个监督者（Supervisor）协调多个专业智能体。

```python
from typing import TypedDict, Annotated, Literal
from langchain_core.messages import AnyMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from pydantic import BaseModel
import os

# 定义状态
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    next: str

# 定义路由选项
class RouteResponse(BaseModel):
    """路由决策"""
    next: Literal["rag_agent", "graph_agent", "search_agent", "FINISH"]

# 智能体成员
members = ["rag_agent", "graph_agent", "search_agent"]
options_for_next = ["FINISH"] + members

# 创建监督者提示
system_prompt = """你是一个监督者，负责协调以下智能体的工作：

可用智能体：
- rag_agent: RAG 知识检索智能体，回答校园政策、规定等问题
- graph_agent: 知识图谱智能体，查询复杂关系（同学、教师等）
- search_agent: 网络搜索智能体，获取实时信息

工作流程：
1. 分析用户请求
2. 选择最合适的智能体执行任务
3. 接收智能体返回的结果
4. 如果任务完成，返回 FINISH
5. 如果需要其他智能体协助，继续分配任务

请根据用户请求，选择下一个应该执行的智能体。"""

# 创建 LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# 监督者节点
def supervisor_node(state: AgentState):
    """监督者节点"""
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    # 创建提示模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "根据以上对话，下一个应该由哪个智能体执行？或标记为 FINISH。请从以下选项中选择：{options}"),
    ]).partial(options=str(options_for_next), members=", ".join(members))
    
    # 创建链
    supervisor_chain = prompt | llm.with_structured_output(RouteResponse)
    
    # 执行决策
    result = supervisor_chain.invoke(state)
    
    return {"next": result.next}

# RAG 智能体
def rag_agent_node(state: AgentState):
    """RAG 智能体：检索知识库回答"""
    # 实现 RAG 逻辑
    response = "根据知识库，新生报到需要准备：录取通知书、身份证..."
    return {
        "messages": [AIMessage(content=response, name="rag_agent")],
        "next": "supervisor"
    }

# 知识图谱智能体
def graph_agent_node(state: AgentState):
    """知识图谱智能体：查询复杂关系"""
    # 实现 Neo4j 查询逻辑
    response = "张三的同学有：李四、王五..."
    return {
        "messages": [AIMessage(content=response, name="graph_agent")],
        "next": "supervisor"
    }

# 搜索智能体
def search_agent_node(state: AgentState):
    """搜索智能体：获取实时信息"""
    # 实现网络搜索逻辑
    response = "根据最新搜索，今天校园有学术讲座..."
    return {
        "messages": [AIMessage(content=response, name="search_agent")],
        "next": "supervisor"
    }

# 创建状态图
builder = StateGraph(AgentState)

# 添加节点
builder.add_node("supervisor", supervisor_node)
builder.add_node("rag_agent", rag_agent_node)
builder.add_node("graph_agent", graph_agent_node)
builder.add_node("search_agent", search_agent_node)

# 添加边
builder.add_edge(START, "supervisor")

# 条件边：监督者决定流向
builder.add_conditional_edges(
    "supervisor",
    lambda x: x["next"],
    {
        "rag_agent": "rag_agent",
        "graph_agent": "graph_agent",
        "search_agent": "search_agent",
        "FINISH": END
    }
)

# 各智能体完成后返回监督者
builder.add_edge("rag_agent", "supervisor")
builder.add_edge("graph_agent", "supervisor")
builder.add_edge("search_agent", "supervisor")

# 编译
graph = builder.compile()

# 执行示例
result = graph.invoke({
    "messages": [HumanMessage(content="新生报到需要准备什么材料？")]
})
```

### 模式 2：Sequential（顺序执行）

按固定顺序依次执行多个智能体。

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class PipelineState(TypedDict):
    query: str
    retrieved_docs: list
    generated_response: str
    final_answer: str

# 创建顺序处理流程
builder = StateGraph(PipelineState)

# 节点 1：检索
def retrieve(state: PipelineState):
    """检索相关文档"""
    docs = ["文档1内容...", "文档2内容..."]
    return {"retrieved_docs": docs}

# 节点 2：生成
def generate(state: PipelineState):
    """生成回答"""
    response = f"基于以下文档：{state['retrieved_docs']}，答案是..."
    return {"generated_response": response}

# 节点 3：优化
def optimize(state: PipelineState):
    """优化回答格式"""
    final = f"优化后的回答：{state['generated_response']}"
    return {"final_answer": final}

# 添加节点和边（顺序执行）
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_node("optimize", optimize)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", "optimize")
builder.add_edge("optimize", END)

graph = builder.compile()

# 执行
result = graph.invoke({"query": "什么是 LangGraph？"})
print(result["final_answer"])
```

### 模式 3：Parallel（并行执行）

多个智能体同时执行，然后合并结果。

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
import operator
from functools import reduce

class ParallelState(TypedDict):
    query: str
    results_rag: str
    results_graph: str
    results_search: str
    final_answer: str

# 创建并行处理流程
builder = StateGraph(ParallelState)

# 并行节点 1：RAG 检索
def rag_task(state: ParallelState):
    """并行执行 RAG 检索"""
    return {"results_rag": "RAG 检索结果..."}

# 并行节点 2：知识图谱查询
def graph_task(state: ParallelState):
    """并行执行图谱查询"""
    return {"results_graph": "知识图谱查询结果..."}

# 并行节点 3：网络搜索
def search_task(state: ParallelState):
    """并行执行网络搜索"""
    return {"results_search": "网络搜索结果..."}

# 合并节点
def merge_results(state: ParallelState):
    """合并所有并行任务的结果"""
    final = f"""
    综合回答：
    
    【知识库信息】{state['results_rag']}
    
    【关系信息】{state['results_graph']}
    
    【实时信息】{state['results_search']}
    """
    return {"final_answer": final}

# 添加节点
builder.add_node("rag_task", rag_task)
builder.add_node("graph_task", graph_task)
builder.add_node("search_task", search_task)
builder.add_node("merge", merge_results)

# 添加边
builder.add_edge(START, "rag_task")
builder.add_edge(START, "graph_task")
builder.add_edge(START, "search_task")

# 所有并行任务完成后，才执行合并
builder.add_edge("rag_task", "merge")
builder.add_edge("graph_task", "merge")
builder.add_edge("search_task", "merge")

builder.add_edge("merge", END)

graph = builder.compile()
```

---

## 💾 持久化和检查点

### 检查点机制

```python
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph

# 创建内存检查点（开发测试用）
memory = SqliteSaver.from_conn_string(":memory:")

# 或使用持久化检查点
# memory = SqliteSaver.from_conn_string("checkpoints.sqlite")

# 编译图时添加检查点
graph = builder.compile(checkpointer=memory)

# 执行时提供线程 ID
config = {"configurable": {"thread_id": "conversation_001"}}

# 第一次执行
result = graph.invoke(
    {"messages": [HumanMessage(content="你好！")]},
    config=config
)

# 后续执行（会自动恢复之前的状态）
result = graph.invoke(
    {"messages": [HumanMessage(content="告诉我校园情况")]},
    config=config
)

# 查看状态历史
states = list(graph.get_state_history(config))
for state in states:
    print(f"状态: {state}")
```

### 断点续传

```python
# 在特定节点设置断点（人工审核）
builder.add_node("human_review", human_review_node)

# 添加中断点
builder.add_node("critical_action", critical_action_node, interrupt_before=["critical_action"])

# 编译
checkpointer = SqliteSaver.from_conn_string(":memory:")
graph = builder.compile(checkpointer=checkpointer)

# 执行到断点会暂停
result = graph.invoke(input_data, config=config)

# 检查是否需要人工干预
if result.get("__interrupt__"):
    # 人工审核逻辑
    user_input = input("是否继续执行？(yes/no): ")
    if user_input.lower() == "yes":
        # 继续执行
        result = graph.invoke(None, config=config)
```

---

## 🎓 CampusFlow 实战示例

### 智慧校园多智能体系统

```python
"""
CampusFlow 多智能体系统
实现：Supervisor + RAG/Graph/Search Agents
"""

from typing import TypedDict, Annotated, Literal
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from pydantic import BaseModel
from functools import lru_cache

# ========== 1. 状态定义 ==========

class CampusState(TypedDict):
    """
    校园智能体系统状态
    
    包含：
    - messages: 对话历史
    - next: 下一个执行节点
    - task_type: 任务类型（知识查询、关系查询、实时信息）
    - context: 上下文信息（检索到的文档、查询结果等）
    """
    messages: Annotated[list[AnyMessage], add_messages]
    next: str
    task_type: str
    context: dict

# ========== 2. 路由定义 ==========

class RouteDecision(BaseModel):
    """路由决策结果"""
    next: Literal["knowledge_agent", "relationship_agent", "search_agent", "FINISH"]
    reason: str

# 智能体列表
AGENTS = {
    "knowledge_agent": "知识查询智能体 - 回答校园政策、规定、流程等问题",
    "relationship_agent": "关系查询智能体 - 查询同学、教师、班级等复杂关系",
    "search_agent": "搜索智能体 - 获取最新新闻、政策、公告等实时信息"
}

# ========== 3. 智能体实现 ==========

class CampusAgents:
    """校园智能体集合"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        
    def supervisor(self, state: CampusState):
        """
        监督者智能体
        
        分析用户请求，决定由哪个智能体处理
        """
        system_prompt = f"""你是 CampusFlow 系统的监督者智能体。

可用智能体：
{knowledge_agent}: 回答校园政策、规定、流程等问题（如：报到流程、选课规定）
{relationship_agent}: 查询复杂关系（如：张三的同学有哪些、李老师的班级）
{search_agent}: 获取实时信息（如：最新通知、今天的新闻）

任务：
1. 分析用户最新请求
2. 选择最合适的智能体
3. 简要说明选择理由

如果任务已完成或不需要进一步处理，选择 FINISH。"""
        
        messages = [
            SystemMessage(content=system_prompt),
            *state["messages"]
        ]
        
        # 使用结构化输出
        decision = self.llm.with_structured_output(RouteDecision).invoke(messages)
        
        return {
            "next": decision.next,
            "context": {"reason": decision.reason}
        }
    
    def knowledge_agent(self, state: CampusState):
        """
        知识查询智能体（RAG）
        
        使用 RAG 技术回答校园知识问题
        """
        # 这里应该调用 RAG 系统
        # 简化示例：
        query = state["messages"][-1].content
        
        # 模拟 RAG 检索
        retrieved_info = self._simulate_rag(query)
        
        # 生成回答
        response = f"【知识库回答】\n\n{retrieved_info}"
        
        return {
            "messages": [AIMessage(content=response, name="knowledge_agent")],
            "next": "supervisor",
            "context": {"source": "knowledge_base"}
        }
    
    def relationship_agent(self, state: CampusState):
        """
        关系查询智能体（Neo4j）
        
        使用知识图谱查询复杂关系
        """
        query = state["messages"][-1].content
        
        # 这里应该调用 Neo4j 查询
        # 简化示例：
        graph_result = self._simulate_graph_query(query)
        
        response = f"【知识图谱查询】\n\n{graph_result}"
        
        return {
            "messages": [AIMessage(content=response, name="relationship_agent")],
            "next": "supervisor",
            "context": {"source": "knowledge_graph"}
        }
    
    def search_agent(self, state: CampusState):
        """
        搜索智能体
        
        获取实时信息
        """
        query = state["messages"][-1].content
        
        # 这里应该调用搜索 API
        # 简化示例：
        search_result = self._simulate_search(query)
        
        response = f"【实时搜索】\n\n{search_result}"
        
        return {
            "messages": [AIMessage(content=response, name="search_agent")],
            "next": "supervisor",
            "context": {"source": "web_search"}
        }
    
    def _simulate_rag(self, query: str) -> str:
        """模拟 RAG 检索"""
        return f"基于知识库检索，关于'{query}'的信息：新生报到需要准备录取通知书、身份证、照片等材料。"
    
    def _simulate_graph_query(self, query: str) -> str:
        """模拟图查询"""
        return f"基于知识图谱查询，关于'{query}'的关系：张三（CS2024001）的同学包括李四、王五..."
    
    def _simulate_search(self, query: str) -> str:
        """模拟网络搜索"""
        return f"最新搜索结果，关于'{query}'：2025年校园科技节将于3月15日举行..."

# ========== 4. 构建工作流 ==========

def create_campus_workflow():
    """创建 CampusFlow 多智能体工作流"""
    
    agents = CampusAgents()
    
    # 创建图构建器
    builder = StateGraph(CampusState)
    
    # 添加节点
    builder.add_node("supervisor", agents.supervisor)
    builder.add_node("knowledge_agent", agents.knowledge_agent)
    builder.add_node("relationship_agent", agents.relationship_agent)
    builder.add_node("search_agent", agents.search_agent)
    
    # 添加边
    builder.add_edge(START, "supervisor")
    
    # 条件路由
    builder.add_conditional_edges(
        "supervisor",
        lambda x: x["next"],
        {
            "knowledge_agent": "knowledge_agent",
            "relationship_agent": "relationship_agent",
            "search_agent": "search_agent",
            "FINISH": END
        }
    )
    
    # 各智能体返回监督者
    builder.add_edge("knowledge_agent", "supervisor")
    builder.add_edge("relationship_agent", "supervisor")
    builder.add_edge("search_agent", "supervisor")
    
    # 编译（添加检查点）
    checkpointer = SqliteSaver.from_conn_string(":memory:")
    graph = builder.compile(checkpointer=checkpointer)
    
    return graph

# ========== 5. 使用示例 ==========

if __name__ == "__main__":
    # 创建工作流
    workflow = create_campus_workflow()
    
    # 配置（用于状态持久化）
    config = {"configurable": {"thread_id": "user_001"}}
    
    # 示例 1：知识查询
    print("=" * 60)
    print("示例 1：知识查询")
    print("=" * 60)
    
    result = workflow.invoke(
        {"messages": [HumanMessage(content="新生报到需要准备什么材料？")]},
        config=config
    )
    
    for msg in result["messages"]:
        print(f"\n{msg.type}: {msg.content}")
    
    # 示例 2：关系查询
    print("\n" + "=" * 60)
    print("示例 2：关系查询")
    print("=" * 60)
    
    result = workflow.invoke(
        {"messages": [HumanMessage(content="张三有哪些同班同学？")]},
        config=config
    )
    
    for msg in result["messages"]:
        print(f"\n{msg.type}: {msg.content}")
```

---

## 📚 学习资源

### 官方文档
- LangGraph 官方文档：https://langchain-ai.github.io/langgraph/
- LangGraph 教程：https://langchain-ai.github.io/langgraph/tutorials/
- LangChain 文档：https://python.langchain.com/

### 推荐阅读
- 《LangGraph 实战：构建多智能体系统》
- 《AI Agent 设计与实现》
- 《LLM 应用开发：从入门到实践》

### 实践项目
1. **客服机器人**：多轮对话 + 知识库检索
2. **数据分析助手**：代码执行 + 图表生成
3. **写作助手**：大纲生成 + 内容扩展 + 润色修改

---

**文档创建时间**：2026-01-30
**文档维护者**：CampusFlow 项目组
