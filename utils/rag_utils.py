"""
RAG 工具函数模块
Day 2: ChromaDB 向量库构建与语义搜索
"""

import os
from typing import List, Optional
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
# from sentence_transformers import SentenceTransformer  # 不需要直接导入


class RAGUtils:
    """RAG（检索增强生成）工具类"""

    def __init__(
        self,
        embedding_model: str = "BAAI/bge-m3",
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        初始化 RAG 工具

        Args:
            embedding_model: Embedding 模型名称（默认使用 BAAI/bge-m3）
            chunk_size: 文本块大小
            chunk_overlap: 文本块重叠大小
        """
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 初始化文本切分器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )

        # 初始化 Embedding 模型
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True},
            show_progress=False  # 减少输出
        )

    def load_documents(self, file_path: str) -> List:
        """
        加载文档（支持 PDF 和 TXT）

        Args:
            file_path: 文档路径

        Returns:
            加载的文档列表
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if path.suffix.lower() == '.pdf':
            loader = PyPDFLoader(file_path)
        elif path.suffix.lower() in ['.txt', '.md']:
            loader = TextLoader(file_path, encoding='utf-8')
        else:
            raise ValueError(f"不支持的文件格式: {path.suffix}")

        documents = loader.load()
        print(f"✅ 成功加载文档: {file_path}")
        print(f"   文档页数: {len(documents)}")

        return documents

    def split_documents(self, documents: List) -> List:
        """
        将文档切分为小块

        Args:
            documents: 文档列表

        Returns:
            切分后的文档块列表
        """
        splits = self.text_splitter.split_documents(documents)
        print(f"✅ 文档切分完成: {len(splits)} 个文本块")
        return splits

    def create_vector_store(
        self,
        documents: List,
        persist_directory: str = "./db/chroma_db",
        collection_name: str = "campus_knowledge"
    ) -> Chroma:
        """
        创建并持久化向量数据库

        Args:
            documents: 文档列表
            persist_directory: 持久化目录
            collection_name: 集合名称

        Returns:
            Chroma 向量数据库实例
        """
        # 创建持久化目录
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        # 创建向量数据库
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=persist_directory,
            collection_name=collection_name
        )

        # 持久化到磁盘
        vector_store.persist()

        print(f"✅ 向量数据库创建成功！")
        print(f"   持久化目录: {persist_directory}")
        print(f"   集合名称: {collection_name}")

        return vector_store

    def load_vector_store(
        self,
        persist_directory: str = "./db/chroma_db",
        collection_name: str = "campus_knowledge"
    ) -> Chroma:
        """
        从磁盘加载已存在的向量数据库

        Args:
            persist_directory: 持久化目录
            collection_name: 集合名称

        Returns:
            Chroma 向量数据库实例
        """
        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name=collection_name
        )

        print(f"✅ 向量数据库加载成功！")
        print(f"   持久化目录: {persist_directory}")
        print(f"   集合名称: {collection_name}")

        return vector_store

    def similarity_search(
        self,
        vector_store: Chroma,
        query: str,
        k: int = 3
    ) -> List:
        """
        语义相似度搜索

        Args:
            vector_store: 向量数据库实例
            query: 查询文本
            k: 返回的文档块数量

        Returns:
            相似度最高的文档块列表
        """
        results = vector_store.similarity_search(query, k=k)

        print(f"✅ 搜索完成，找到 {len(results)} 个相关文档块")

        return results

    def max_marginal_relevance_search(
        self,
        vector_store: Chroma,
        query: str,
        k: int = 3,
        fetch_k: int = 10
    ) -> List:
        """
        最大边际相关性搜索（MMR）
        在相关性和多样性之间取得平衡

        Args:
            vector_store: 向量数据库实例
            query: 查询文本
            k: 返回的文档块数量
            fetch_k: 从中选择的候选文档块数量

        Returns:
            相似度高且多样化的文档块列表
        """
        results = vector_store.max_marginal_relevance_search(
            query, k=k, fetch_k=fetch_k
        )

        print(f"✅ MMR 搜索完成，找到 {len(results)} 个相关文档块")

        return results


def build_sample_knowledge_base():
    """
    构建示例知识库（使用示例文本数据）
    """
    print("=" * 50)
    print("🚀 构建校园知识向量库")
    print("=" * 50)
    print()

    # 创建 RAG 工具实例
    rag = RAGUtils(
        embedding_model="BAAI/bge-m3",
        chunk_size=500,
        chunk_overlap=50
    )

    # 创建示例文档（模拟校园政策文档）
    sample_docs = [
        """
        校园报到指南

        新生报到时间：每年 9 月 1 日至 9 月 5 日
        报到地点：学校主楼大厅
        所需材料：
        1. 录取通知书
        2. 身份证原件及复印件
        3. 高考准考证
        4. 近期一寸免冠照片 8 张
        5. 团员证及党组织关系证明（如有）

        注意事项：
        - 请按时报到，逾期需向学校教务处申请
        - 报到当日可办理校园一卡通和宿舍入住手续
        - 家庭经济困难学生可在报到时申请助学金
        """,
        """
        宿舍管理规定

        宿舍开放时间：每天 6:00 - 23:00
        门禁时间：晚上 23:00，周末延长至 24:00
        宿舍分配：按照院系和班级统一分配
        宿舍设施：每个宿舍配备空调、独立卫生间、书桌和衣柜

        宿舍管理要求：
        1. 保持宿舍卫生，每日打扫
        2. 禁止使用大功率电器（电热毯、电炉等）
        3. 禁止在宿舍吸烟和饮酒
        4. 宿舍内禁止饲养宠物
        5. 晚 23:00 后保持安静，不影响他人休息

        违规处理：
        - 首次违规：口头警告
        - 二次违规：书面警告
        - 三次违规：取消住宿资格
        """,
        """
        选课与学分制度

        学分要求：本科生需修满 160 学分方可毕业
        课程类型：
        1. 公共基础课（约 40 学分）
        2. 专业基础课（约 60 学分）
        3. 专业选修课（约 40 学分）
        4. 通识教育选修课（约 20 学分）

        选课时间：
        - 每学期第 1 周为选课周
        - 第 2 周为补选和退选时间
        - 第 3 周起课程正式开始

        注意事项：
        - 每学期最多可选 25 学分
        - 选课需在规定时间内完成，逾期无法补选
        - 课程冲突需自行调整选课计划
        """,
        """
        奖学金评定标准

        国家奖学金：每人每年 8000 元
        评定条件：
        1. 综合素质测评成绩排名在前 5%
        2. 无挂科记录
        3. 积极参与社会实践活动

        国家励志奖学金：每人每年 5000 元
        评定条件：
        1. 家庭经济困难学生
        2. 综合素质测评成绩排名在前 15%
        3. 无挂科记录

        校级奖学金：
        - 一等奖学金：3000 元，成绩排名前 5%
        - 二等奖学金：1500 元，成绩排名前 10%
        - 三等奖学金：800 元，成绩排名前 20%

        申请时间：每学年秋季学期（10 月-11 月）
        """,
        """
        图书馆服务指南

        开放时间：
        - 周一至周五：8:00 - 22:00
        - 周六、周日：9:00 - 21:00
        - 节假日：10:00 - 18:00

        借阅规则：
        1. 本科生最多可借 10 本图书
        2. 借阅期限为 30 天，可续借一次（15 天）
        3. 逾期图书每本每天罚款 0.5 元
        4. 遗失图书需照价赔偿

        电子资源：
        - 学校提供 CNKI、万方等学术数据库
        - 可在校园网内免费访问
        - 需使用学号和密码登录

        注意事项：
        - 保持图书馆安静，不得大声喧哗
        - 禁止在图书馆内饮食
        - 随身物品自行保管
        """
    ]

    # 切分文档
    from langchain.schema import Document

    documents = [Document(page_content=doc) for doc in sample_docs]
    splits = rag.split_documents(documents)

    # 创建向量数据库
    vector_store = rag.create_vector_store(
        documents=splits,
        persist_directory="./db/chroma_db",
        collection_name="campus_knowledge"
    )

    print()
    print("=" * 50)
    print("🎉 知识库构建完成！")
    print("=" * 50)

    return vector_store


def test_semantic_search():
    """
    测试语义搜索功能
    """
    print()
    print("=" * 50)
    print("🔍 测试语义搜索")
    print("=" * 50)
    print()

    # 加载向量数据库
    rag = RAGUtils(embedding_model="BAAI/bge-m3")
    vector_store = rag.load_vector_store(
        persist_directory="./db/chroma_db",
        collection_name="campus_knowledge"
    )

    # 测试查询
    test_queries = [
        "新生报到需要准备什么材料？",
        "宿舍晚上几点关门？",
        "奖学金怎么申请？",
        "图书馆可以借几本书？"
    ]

    for query in test_queries:
        print(f"\n📝 查询：{query}")
        print("-" * 50)

        # 执行语义搜索
        results = rag.similarity_search(vector_store, query, k=2)

        for i, doc in enumerate(results, 1):
            print(f"\n结果 {i}:")
            print(f"内容: {doc.page_content[:200]}...")

    print()
    print("=" * 50)
    print("✅ 语义搜索测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    # 构建示例知识库
    build_sample_knowledge_base()

    # 测试语义搜索
    test_semantic_search()
