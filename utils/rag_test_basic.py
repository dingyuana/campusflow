"""
RAG 基础功能测试（不依赖下载模型）
测试基本的数据结构和逻辑
"""

import sys
from pathlib import Path

# 测试导入
print("=" * 50)
print("🧪 RAG 基础功能测试")
print("=" * 50)
print()

print("1. 测试文件结构...")
print("-" * 50)

files_to_check = [
    "utils/rag_utils.py",
    "utils/rag_test_simple.py",
    "data/"
]

all_files_exist = True
for file_path in files_to_check:
    path = Path(file_path)
    exists = path.exists() or path.is_dir()
    status = "✅" if exists else "❌"
    print(f"{status} {file_path} {'存在' if exists else '不存在'}")
    if not exists:
        all_files_exist = False

print()

print("2. 测试 Python 导入...")
print("-" * 50)

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("✅ langchain_text_splitters 导入成功")
except ImportError as e:
    print(f"❌ langchain_text_splitters 导入失败: {e}")
    all_files_exist = False

try:
    from langchain_core.documents import Document
    print("✅ langchain_core.documents 导入成功")
except ImportError as e:
    print(f"❌ langchain_core.documents 导入失败: {e}")
    all_files_exist = False

try:
    import chromadb
    print(f"✅ chromadb 导入成功 (版本: {chromadb.__version__})")
except ImportError as e:
    print(f"❌ chromadb 导入失败: {e}")
    all_files_exist = False

print()

print("3. 测试文档切分功能...")
print("-" * 50)

try:
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    # 创建测试文档
    test_text = """
    校园报到时间：每年 9 月 1 日至 9 月 5 日。报到地点：学校主楼大厅。
    所需材料：录取通知书、身份证原件及复印件、高考准考证。
    """

    documents = [Document(page_content=test_text)]
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        separators=["。", "，", "。", " "]
    )

    splits = splitter.split_documents(documents)
    print(f"✅ 文档切分成功：{len(splits)} 个文本块")

    for i, split in enumerate(splits, 1):
        print(f"\n文本块 {i}:")
        print(f"  {split.page_content[:80]}...")

except Exception as e:
    print(f"❌ 文档切分失败: {e}")
    all_files_exist = False

print()

print("4. 测试 Chroma 基本功能...")
print("-" * 50)

try:
    import chromadb

    # 创建内存客户端
    client = chromadb.Client()

    # 创建集合
    collection = client.create_collection(
        name="test_collection",
        metadata={"hnsw:space": "cosine"}
    )

    # 添加测试数据（使用简单的文本，不依赖 embedding）
    collection.add(
        ids=["doc_1", "doc_2"],
        documents=["测试文档 1", "测试文档 2"],
        metadatas=[{"source": "test1"}, {"source": "test2"}]
    )

    print(f"✅ Chroma 集合创建成功")
    print(f"   集合名称: test_collection")
    print(f"   文档数量: {collection.count()}")

    # 查询测试
    results = collection.query(
        query_texts=["测试"],
        n_results=1
    )

    if results['documents'] and results['documents'][0]:
        print(f"✅ 查询成功，找到结果: {results['documents'][0][0]}")
    else:
        print("⚠️  查询未返回结果")

except Exception as e:
    print(f"❌ Chroma 基本功能测试失败: {e}")
    all_files_exist = False

print()

print("=" * 50)
print("📊 测试总结")
print("=" * 50)

if all_files_exist:
    print("🎉 所有测试通过！RAG 基础功能正常")
    sys.exit(0)
else:
    print("⚠️  部分测试失败，请检查上述错误")
    sys.exit(1)
