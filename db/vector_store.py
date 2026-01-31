"""
Day 2: 向量数据库与混合检索
使用 ChromaDB 和 BGE-m3 嵌入模型
"""

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
from typing import List, Tuple


# 使用 BGE-m3 模型（中文优化）
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={'device': 'cpu'},  # 无 GPU 环境使用 cpu
    encode_kwargs={'normalize_embeddings': True}  # 归一化便于余弦相似度计算
)


def create_vector_db(chunks, persist_dir="./chroma_db"):
    """
    创建并持久化向量数据库
    
    Args:
        chunks: 文档块列表
        persist_dir: 持久化目录
        
    Returns:
        Chroma 向量数据库实例
    """
    
    # 如果已存在则加载，否则创建
    if os.path.exists(persist_dir) and len(os.listdir(persist_dir)) > 0:
        print("🔄 加载已存在的向量数据库...")
        vectordb = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings
        )
    else:
        print("🔨 创建新的向量数据库...")
        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_dir,
            collection_metadata={"hnsw:space": "cosine"}  # 使用余弦距离
        )
        vectordb.persist()
    
    return vectordb


def hybrid_search(vectordb, query: str, k: int = 5):
    """
    混合检索：语义检索 + 关键词过滤
    
    Args:
        vectordb: Chroma 向量数据库
        query: 查询文本
        k: 返回结果数
        
    Returns:
        检索结果列表 [(doc, score), ...]
    """
    # 1. 语义检索
    semantic_results = vectordb.similarity_search_with_score(query, k=k*2)
    
    # 2. 关键词匹配强化（简单实现：包含关键词的 boost）
    keywords = extract_keywords(query)  # 简单分词提取关键词
    boosted_results = []
    
    for doc, score in semantic_results:
        # 原始分数是距离（越小越好），转为相似度（越大越好）
        similarity = 1 - score
        
        # 关键词匹配加分
        content_lower = doc.page_content.lower()
        keyword_boost = sum(0.1 for kw in keywords if kw in content_lower)
        final_score = similarity + keyword_boost
        
        boosted_results.append((doc, final_score))
    
    # 按最终分数排序并返回前 k 个
    boosted_results.sort(key=lambda x: x[1], reverse=True)
    return boosted_results[:k]


def extract_keywords(text: str) -> List[str]:
    """
    简单关键词提取（实际可用 jieba）
    
    Args:
        text: 输入文本
        
    Returns:
        关键词列表
    """
    # 针对校园场景的关键词库
    key_terms = ["学费", "宿舍", "一卡通", "军训", "图书馆", "报到", "档案", "户口"]
    return [term for term in key_terms if term in text]
