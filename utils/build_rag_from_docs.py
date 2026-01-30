"""
使用真实文档构建 RAG 向量库
从 docs/ragfiles 目录加载文档并构建 Chroma 向量数据库
"""

import os
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
import chromadb


def load_documents_from_directory(directory: str) -> List:
    """
    从目录加载所有支持的文档

    Args:
        directory: 文档目录路径

    Returns:
        文档列表
    """
    documents = []
    dir_path = Path(directory)

    if not dir_path.exists():
        print(f"❌ 目录不存在: {directory}")
        return documents

    # 支持的文件扩展名
    supported_extensions = {'.pdf', '.docx', '.doc', '.txt', '.md'}

    # 遍历目录
    for file_path in dir_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            print(f"📄 正在加载: {file_path.name}")

            try:
                # 根据文件类型选择加载器
                if file_path.suffix.lower() == '.pdf':
                    loader = PyPDFLoader(str(file_path))
                    file_docs = loader.load()
                elif file_path.suffix.lower() in ['.docx', '.doc']:
                    loader = Docx2txtLoader(str(file_path))
                    file_docs = loader.load()
                elif file_path.suffix.lower() in ['.txt', '.md']:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        file_docs = [Document(page_content=text, metadata={'source': str(file_path)})]

                documents.extend(file_docs)
                print(f"   ✅ 加载成功: {len(file_docs)} 页")

            except Exception as e:
                print(f"   ❌ 加载失败: {e}")
                continue

    return documents


def build_vector_store_from_documents(
    documents: List,
    persist_directory: str = "./db/chroma_db_campus",
    collection_name: str = "campus_documents"
):
    """
    从文档列表构建向量库

    Args:
        documents: 文档列表
        persist_directory: 持久化目录
        collection_name: 集合名称
    """
    print()
    print("=" * 60)
    print("🚀 开始构建 RAG 向量库")
    print("=" * 60)
    print()

    # 1. 初始化文本切分器
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
    )

    # 2. 切分文档
    print("📝 正在切分文档...")
    splits = text_splitter.split_documents(documents)
    print(f"✅ 文档切分完成: {len(splits)} 个文本块")
    print()

    # 3. 创建 Chroma 客户端
    print("💾 正在创建向量数据库...")
    client = chromadb.PersistentClient(path=persist_directory)

    # 4. 创建集合
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    print(f"✅ Chroma 集合创建/加载成功")
    print(f"   持久化目录: {persist_directory}")
    print(f"   集合名称: {collection_name}")
    print()

    # 5. 准备数据
    print("📊 正在准备向量数据...")
    ids = [f"doc_{i}" for i in range(len(splits))]
    texts = [split.page_content for split in splits]
    metadatas = [split.metadata for split in splits]

    # 清空集合（如果已存在）
    try:
        collection.delete(ids=collection.get()['ids'])
        print("🧹 清空旧数据")
    except:
        pass

    # 6. 批量添加文档
    print(f"正在添加 {len(texts)} 个文本块...")
    batch_size = 100  # 每批处理 100 个

    for i in range(0, len(texts), batch_size):
        batch_ids = ids[i:i+batch_size]
        batch_texts = texts[i:i+batch_size]
        batch_metadatas = metadatas[i:i+batch_size]

        collection.add(
            ids=batch_ids,
            documents=batch_texts,
            metadatas=batch_metadatas
        )

        print(f"   进度: {min(i+batch_size, len(texts))}/{len(texts)} ({min((i+batch_size)/len(texts)*100, 100):.1f}%)")

    print(f"✅ 文档添加完成")
    print()

    print("=" * 60)
    print("🎉 RAG 向量库构建完成！")
    print("=" * 60)
    print()
    print(f"📊 统计信息:")
    print(f"   - 文档数量: {len(documents)}")
    print(f"   - 文本块数量: {len(splits)}")
    print(f"   - 集合名称: {collection_name}")
    print(f"   - 持久化目录: {persist_directory}")
    print()

    return client, collection


def test_semantic_search(collection, queries: List[str]):
    """
    测试语义搜索

    Args:
        collection: Chroma 集合
        queries: 测试查询列表
    """
    print("=" * 60)
    print("🔍 测试语义搜索")
    print("=" * 60)
    print()

    for i, query in enumerate(queries, 1):
        print(f"查询 {i}: {query}")
        print("-" * 60)

        try:
            results = collection.query(
                query_texts=[query],
                n_results=3
            )

            if results['documents'] and results['documents'][0]:
                for j, (doc, metadata) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0]
                ), 1):
                    print(f"\n结果 {j}:")
                    print(f"来源: {metadata.get('source', '未知')}")
                    print(f"内容: {doc[:150]}...")
            else:
                print("\n未找到相关结果")

        except Exception as e:
            print(f"\n查询出错: {e}")

        print()

    print("=" * 60)
    print("✅ 语义搜索测试完成")
    print("=" * 60)


def main():
    """主函数"""
    # 配置
    docs_directory = "docs/ragfiles"
    persist_directory = "./db/chroma_db_campus"
    collection_name = "campus_documents"

    print("=" * 60)
    print("📚 使用真实文档构建 RAG 向量库")
    print("=" * 60)
    print()

    # 1. 加载文档
    documents = load_documents_from_directory(docs_directory)

    if not documents:
        print("❌ 没有加载到任何文档，程序退出")
        return

    # 2. 构建向量库
    client, collection = build_vector_store_from_documents(
        documents=documents,
        persist_directory=persist_directory,
        collection_name=collection_name
    )

    # 3. 测试查询
    test_queries = [
        "新生报到需要准备什么材料？",
        "学生违纪有哪些处罚规定？",
        "硕士研究生招生的基本条件是什么？",
        "学校有哪些重点实验室？",
        "宿舍管理和生活规定"
    ]

    print()
    test_semantic_search(collection, test_queries)

    # 4. 保存测试报告
    print()
    print("💡 提示:")
    print("   - 向量库已持久化到磁盘")
    print("   - 下次可以直接加载使用")
    print("   - 使用以下代码加载向量库:")
    print(f"""
       import chromadb

       client = chromadb.PersistentClient(path="{persist_directory}")
       collection = client.get_collection(name="{collection_name}")
       """)


if __name__ == "__main__":
    main()
