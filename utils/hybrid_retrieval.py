"""
混合检索增强模块
Day 2: 语义检索 + 关键词检索混合策略

实现两种检索方式的融合：
1. 语义检索 (Similarity Search): 基于向量相似度
2. 关键词检索 (BM25/关键词匹配): 基于词频匹配
3. 混合融合 (RRF): Reciprocal Rank Fusion 算法

参考教学计划 Day 2 要求：
- 混合检索策略（关键词检索+语义检索）
- 语义切分原则（按语义完整性、固定长度+重叠窗口）
- Chroma DB 的核心特性
"""

import os
import re
from typing import List, Dict, Tuple
from collections import Counter
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


class HybridRetriever:
    """
    混合检索器
    
    结合语义检索和关键词检索，使用 RRF 算法融合结果
    """
    
    def __init__(
        self,
        vector_store: Chroma,
        embedding_model: str = "BAAI/bge-m3",
        semantic_weight: float = 0.6,
        keyword_weight: float = 0.4,
        k: int = 5
    ):
        """
        初始化混合检索器
        
        Args:
            vector_store: Chroma 向量数据库实例
            embedding_model: 嵌入模型名称
            semantic_weight: 语义检索权重 (0-1)
            keyword_weight: 关键词检索权重 (0-1)
            k: 返回结果数量
        """
        self.vector_store = vector_store
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.k = k
        
        # 初始化嵌入模型（用于语义检索）
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True},
            show_progress=False
        )
    
    def keyword_search(
        self,
        query: str,
        documents: List[Document],
        top_k: int = 10
    ) -> List[Tuple[Document, float]]:
        """
        关键词检索 - 基于 BM25 简化版本
        
        算法：
        1. 提取查询中的关键词
        2. 计算每个文档的词频得分
        3. 返回得分最高的文档
        
        Args:
            query: 查询文本
            documents: 待检索的文档列表
            top_k: 返回结果数量
            
        Returns:
            [(文档, 得分), ...]
        """
        # 提取查询关键词（去除停用词）
        query_terms = self._extract_terms(query)
        
        if not query_terms:
            return []
        
        # 计算每个文档的得分
        scores = []
        for doc in documents:
            doc_text = doc.page_content.lower()
            doc_terms = self._extract_terms(doc_text)
            
            # 计算 TF (词频)
            score = 0
            for term in query_terms:
                # 精确匹配得分更高
                exact_count = doc_text.count(term)
                # 部分匹配
                partial_count = sum(1 for t in doc_terms if term in t or t in term)
                
                score += exact_count * 2 + partial_count * 0.5
            
            scores.append((doc, score))
        
        # 按得分排序
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores[:top_k]
    
    def _extract_terms(self, text: str) -> List[str]:
        """
        提取文本中的关键词（去除停用词）
        
        Args:
            text: 输入文本
            
        Returns:
            关键词列表
        """
        # 停用词列表
        stopwords = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
            '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
            '你', '会', '着', '没有', '看', '好', '自己', '这', '那',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were'
        }
        
        # 提取中文和英文词汇
        # 中文：2-4 个字符的词
        chinese_terms = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
        # 英文：长度 >= 3 的词
        english_terms = re.findall(r'[a-zA-Z]{3,}', text.lower())
        
        all_terms = chinese_terms + english_terms
        
        # 过滤停用词和短词
        filtered_terms = [
            term for term in all_terms 
            if term not in stopwords and len(term) >= 2
        ]
        
        return filtered_terms
    
    def reciprocal_rank_fusion(
        self,
        semantic_results: List[Tuple[Document, float]],
        keyword_results: List[Tuple[Document, float]],
        k: int = 60
    ) -> List[Tuple[Document, float]]:
        """
        RRF (Reciprocal Rank Fusion) 融合算法
        
        公式：score = Σ 1 / (k + rank)
        
        其中：
        - k: 常数，通常取 60
        - rank: 文档在某个列表中的排名（从 1 开始）
        
        Args:
            semantic_results: 语义检索结果 [(doc, score), ...]
            keyword_results: 关键词检索结果 [(doc, score), ...]
            k: RRF 常数
            
        Returns:
            融合后的结果 [(doc, rrf_score), ...]
        """
        # 创建文档到排名的映射
        semantic_ranks = {
            id(doc): rank + 1 
            for rank, (doc, _) in enumerate(semantic_results)
        }
        keyword_ranks = {
            id(doc): rank + 1 
            for rank, (doc, _) in enumerate(keyword_results)
        }
        
        # 获取所有唯一文档
        all_docs = set()
        for doc, _ in semantic_results:
            all_docs.add(id(doc))
        for doc, _ in keyword_results:
            all_docs.add(id(doc))
        
        # 计算 RRF 得分
        rrf_scores = []
        
        # 从语义结果中获取文档对象
        doc_map = {id(doc): doc for doc, _ in semantic_results + keyword_results}
        
        for doc_id in all_docs:
            score = 0.0
            
            # 语义检索得分
            if doc_id in semantic_ranks:
                rank = semantic_ranks[doc_id]
                score += self.semantic_weight * (1.0 / (k + rank))
            
            # 关键词检索得分
            if doc_id in keyword_ranks:
                rank = keyword_ranks[doc_id]
                score += self.keyword_weight * (1.0 / (k + rank))
            
            rrf_scores.append((doc_map[doc_id], score))
        
        # 按 RRF 得分排序
        rrf_scores.sort(key=lambda x: x[1], reverse=True)
        
        return rrf_scores
    
    def hybrid_search(
        self,
        query: str,
        documents: List[Document],
        k: int = None
    ) -> List[Tuple[Document, float]]:
        """
        混合检索 - 融合语义检索和关键词检索
        
        流程：
        1. 语义检索获取相关文档
        2. 关键词检索获取相关文档
        3. 使用 RRF 算法融合结果
        
        Args:
            query: 查询文本
            documents: 候选文档列表
            k: 返回结果数量
            
        Returns:
            [(文档, 融合得分), ...]
        """
        k = k or self.k
        
        print(f"🔍 执行混合检索: '{query}'")
        print(f"   候选文档数: {len(documents)}")
        print(f"   语义权重: {self.semantic_weight}, 关键词权重: {self.keyword_weight}")
        
        # 1. 语义检索
        print("\n📊 步骤 1: 语义检索...")
        semantic_results = self._semantic_search(query, documents, top_k=10)
        print(f"   ✅ 获取 {len(semantic_results)} 个语义检索结果")
        
        # 2. 关键词检索
        print("\n🔤 步骤 2: 关键词检索...")
        keyword_results = self.keyword_search(query, documents, top_k=10)
        print(f"   ✅ 获取 {len(keyword_results)} 个关键词检索结果")
        
        # 3. RRF 融合
        print("\n🔄 步骤 3: RRF 融合...")
        fused_results = self.reciprocal_rank_fusion(semantic_results, keyword_results)
        print(f"   ✅ 融合后共 {len(fused_results)} 个结果")
        
        # 返回 Top K
        return fused_results[:k]
    
    def _semantic_search(
        self,
        query: str,
        documents: List[Document],
        top_k: int = 10
    ) -> List[Tuple[Document, float]]:
        """
        语义检索（使用向量相似度）
        
        Args:
            query: 查询文本
            documents: 候选文档
            top_k: 返回数量
            
        Returns:
            [(文档, 相似度得分), ...]
        """
        # 将文档临时添加到向量库
        temp_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name="temp_hybrid"
        )
        
        # 执行相似度搜索
        results = temp_store.similarity_search_with_score(query, k=top_k)
        
        # 转换格式
        return [(doc, score) for doc, score in results]


def test_hybrid_retrieval():
    """
    测试混合检索功能
    """
    print("=" * 60)
    print("🧪 混合检索测试")
    print("=" * 60)
    print()
    
    # 创建测试文档
    test_docs = [
        Document(page_content="""
        图书馆借阅规则
        
        本科生最多可借 10 本图书，借阅期限为 30 天，可续借一次（15 天）。
        逾期图书每本每天罚款 0.5 元。遗失图书需照价赔偿。
        学校提供 CNKI、万方等学术数据库，可在校园网内免费访问。
        """, metadata={"source": "library_rules"}),
        
        Document(page_content="""
        新生报到指南
        
        新生报到时间：每年 9 月 1 日至 9 月 5 日
        报到地点：学校主楼大厅
        所需材料：录取通知书、身份证原件及复印件、高考准考证、近期一寸免冠照片 8 张
        报到当日可办理校园一卡通和宿舍入住手续
        """, metadata={"source": "enrollment_guide"}),
        
        Document(page_content="""
        宿舍管理规定
        
        宿舍开放时间：每天 6:00 - 23:00
        门禁时间：晚上 23:00，周末延长至 24:00
        宿舍分配：按照院系和班级统一分配
        宿舍设施：每个宿舍配备空调、独立卫生间、书桌和衣柜
        """, metadata={"source": "dormitory_rules"}),
        
        Document(page_content="""
        奖学金评定标准
        
        国家奖学金：每人每年 8000 元
        评定条件：综合素质测评成绩排名在前 5%，无挂科记录，积极参与社会实践活动
        申请时间：每学年秋季学期（10 月-11 月）
        """, metadata={"source": "scholarship"}),
        
        Document(page_content="""
        选课与学分制度
        
        学分要求：本科生需修满 160 学分方可毕业
        课程类型：公共基础课（约 40 学分）、专业基础课（约 60 学分）
        选课时间：每学期第 1 周为选课周，第 2 周为补选和退选时间
        """, metadata={"source": "course_selection"})
    ]
    
    # 创建混合检索器
    # 注意：这里需要一个空的向量库作为占位符
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True},
        show_progress=False
    )
    
    temp_store = Chroma.from_documents(
        documents=[Document(page_content="placeholder")],
        embedding=embeddings
    )
    
    retriever = HybridRetriever(
        vector_store=temp_store,
        semantic_weight=0.6,
        keyword_weight=0.4,
        k=3
    )
    
    # 测试查询
    test_queries = [
        "图书馆借书有什么规定？",
        "新生报到需要带什么？",
        "宿舍晚上几点关门？",
        "怎么申请奖学金？"
    ]
    
    for query in test_queries:
        print("=" * 60)
        print(f"📝 查询: {query}")
        print("=" * 60)
        
        results = retriever.hybrid_search(query, test_docs, k=3)
        
        print("\n📋 检索结果:")
        for i, (doc, score) in enumerate(results, 1):
            print(f"\n【结果 {i}】融合得分: {score:.4f}")
            print(f"来源: {doc.metadata.get('source', 'unknown')}")
            print(f"内容: {doc.page_content[:150]}...")
        
        print()
    
    print("=" * 60)
    print("✅ 混合检索测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_hybrid_retrieval()
