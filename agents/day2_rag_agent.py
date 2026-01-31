"""
Day 2: RAG Agent 集成
结合向量检索与 ReAct Agent
"""

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.tools import tool
from db.vector_store import create_vector_db, hybrid_search
from db.rag_loader import load_and_split_handbook
import os


# 初始化向量库（全局加载一次）
print("🔄 初始化 RAG 系统...")
# 注意：实际使用时需要提供真实的 PDF 路径
# chunks = load_and_split_handbook("data/新生报到手册.pdf")
# vectordb = create_vector_db(chunks)
vectordb = None  # 占位符，实际使用时初始化


@tool
def query_handbook(question: str) -> str:
    """
    查询《新生报到手册》获取官方信息
    
    Args:
        question: 学生关于报到流程、缴费、宿舍等的问题
        
    Returns:
        检索到的相关信息
    """
    if vectordb is None:
        return "RAG 系统未初始化，请确保 PDF 文件已加载。"
    
    # 混合检索
    results = hybrid_search(vectordb, question, k=3)
    
    if not results:
        return "未找到相关信息，建议联系学工处咨询。"
    
    # 组装上下文
    context = "\n\n".join([
        f"[相关度: {score:.2f}] {doc.page_content}" 
        for doc, score in results
    ])
    
    return f"根据报到手册查询结果：\n{context}"


# 工具列表（复用 Day1 的工具 + RAG 工具）
from agents.tools.campus_info import (
    query_campus_library_status, 
    query_tuition_payment
)

tools = [query_handbook, query_campus_library_status, query_tuition_payment]

model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)

rag_agent = create_react_agent(model, tools)


def ask_about_registration(question: str):
    """
    对外接口：询问报到相关问题
    
    Args:
        question: 用户问题
        
    Returns:
        Agent 回答
    """
    response = rag_agent.invoke({
        "messages": [HumanMessage(content=question)]
    })
    return response["messages"][-1].content


# 测试
if __name__ == "__main__":
    test_questions = [
        "报到需要带哪些材料？",
        "学费最晚什么时候交？",
        "宿舍是怎么分配的？"
    ]
    
    for q in test_questions:
        print(f"\n👤 问题：{q}")
        print(f"🤖 回答：{ask_about_registration(q)}")
        print("-" * 50)
