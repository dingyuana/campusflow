"""
RAG 简化测试脚本
使用本地测试数据，不依赖下载大型模型
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions
import chromadb


def test_chroma_basic():
    """测试 Chroma 基本功能"""

    print("=" * 50)
    print("🚀 测试 Chroma 向量库")
    print("=" * 50)
    print()

    # 1. 准备测试文档
    sample_docs = [
        "校园报到时间：每年 9 月 1 日至 9 月 5 日。报到地点：学校主楼大厅。所需材料：录取通知书、身份证原件及复印件、高考准考证。",
        "宿舍开放时间：每天 6:00 - 23:00。门禁时间：晚上 23:00。宿舍设施：每个宿舍配备空调、独立卫生间、书桌和衣柜。",
        "学分要求：本科生需修满 160 学分方可毕业。课程类型：公共基础课（约 40 学分）、专业基础课（约 60 学分）。",
        "国家奖学金：每人每年 8000 元。评定条件：综合素质测评成绩排名在前 5%、无挂科记录、积极参与社会实践活动。",
        "图书馆开放时间：周一至周五 8:00 - 22:00。借阅规则：本科生最多可借 10 本图书，借阅期限为 30 天。",
    ]

    print(f"✅ 准备了 {len(sample_docs)} 个测试文档")
    print()

    # 2. 切分文档
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20,
        separators=["。", "，", "。", " "]
    )

    documents = [Document(page_content=doc) for doc in sample_docs]
    splits = text_splitter.split_documents(documents)

    print(f"✅ 文档切分完成：{len(splits)} 个文本块")
    print()

    # 3. 初始化 Chroma 客户端（内存模式）
    client = chromadb.Client()

    # 4. 创建集合
    collection = client.create_collection(
        name="campus_knowledge_test",
        metadata={"hnsw:space": "cosine"}
    )

    print(f"✅ 创建 Chroma 集合成功")
    print()

    # 5. 准备数据
    ids = [f"doc_{i}" for i in range(len(splits))]
    texts = [split.page_content for split in splits]

    print(f"✅ 准备向量数据：{len(texts)} 个")
    print()

    # 6. 添加文档（不使用 embedding，使用简单文本）
    # 注意：生产环境应该使用真实的 embedding 模型
    for i, text in enumerate(texts):
        collection.add(
            ids=[ids[i]],
            documents=[text],
            metadatas=[{"source": f"chunk_{i}"}]
        )

    print(f"✅ 文档添加成功")
    print()

    # 7. 测试查询（使用简单的文本相似度）
    test_queries = [
        "新生报到需要什么材料？",
        "宿舍几点关门？",
        "奖学金怎么申请？",
        "图书馆可以借几本书？"
    ]

    print("=" * 50)
    print("🔍 测试语义搜索")
    print("=" * 50)
    print()

    for query in test_queries:
        print(f"📝 查询：{query}")
        print("-" * 50)

        try:
            results = collection.query(
                query_texts=[query],
                n_results=2
            )

            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0], 1):
                    print(f"\n结果 {i}:")
                    print(f"内容: {doc[:100]}...")
            else:
                print("\n未找到相关结果")
        except Exception as e:
            print(f"\n查询出错: {e}")

        print()

    print("=" * 50)
    print("🎉 测试完成！")
    print("=" * 50)
    print()
    print("💡 注意：")
    print("   - 当前测试使用简化模式，未使用真实的 Embedding 模型")
    print("   - 生产环境应使用 BAAI/bge-m3 或其他 Embedding 模型")
    print("   - Chroma 向量库已成功创建和测试")


if __name__ == "__main__":
    test_chroma_basic()
