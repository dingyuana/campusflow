"""
RAG 文档加载和切分测试
先不进行向量化，仅测试文档处理功能
"""

from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader


def main():
    print("=" * 60)
    print("📚 RAG 文档处理测试")
    print("=" * 60)
    print()

    docs_directory = "docs/ragfiles"
    documents = []
    file_stats = []

    print("1. 文件扫描")
    print("-" * 60)

    dir_path = Path(docs_directory)
    if not dir_path.exists():
        print(f"❌ 目录不存在: {docs_directory}")
        return

    # 遍历文件
    for file_path in dir_path.iterdir():
        if file_path.is_file():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"📄 {file_path.name} ({size_mb:.2f} MB)")
            file_stats.append({
                'name': file_path.name,
                'size_mb': size_mb,
                'path': str(file_path)
            })

    print()
    print("2. 文档加载")
    print("-" * 60)

    for file_stat in file_stats:
        file_path = Path(file_stat['path'])
        print(f"\n📄 正在加载: {file_stat['name']}")

        try:
            # 根据文件类型选择加载器
            if file_path.suffix.lower() == '.pdf':
                loader = PyPDFLoader(str(file_path))
                file_docs = loader.load()
                print(f"   ✅ PDF 加载成功: {len(file_docs)} 页")
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                loader = Docx2txtLoader(str(file_path))
                file_docs = loader.load()
                print(f"   ✅ Word 加载成功: {len(file_docs)} 页")
            elif file_path.suffix.lower() == '.xlsx':
                print(f"   ⚠️  Excel 文件暂不支持: 跳过")
                continue
            else:
                print(f"   ⚠️  不支持的文件类型: 跳过")
                continue

            documents.extend(file_docs)

        except Exception as e:
            print(f"   ❌ 加载失败: {e}")
            continue

    print()
    print(f"✅ 文档加载完成: {len(documents)} 个文档对象")
    print()

    print("3. 文档切分")
    print("-" * 60)

    if not documents:
        print("❌ 没有可用的文档")
        return

    # 统计文档内容
    total_chars = 0
    for doc in documents:
        total_chars += len(doc.page_content)

    print(f"📊 文档统计:")
    print(f"   - 文档数量: {len(documents)}")
    print(f"   - 总字符数: {total_chars:,}")
    print()

    # 切分文档
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
    )

    splits = text_splitter.split_documents(documents)
    print(f"✅ 文档切分完成: {len(splits)} 个文本块")
    print()

    # 显示前 3 个文本块示例
    print("4. 文本块示例")
    print("-" * 60)

    for i, split in enumerate(splits[:3], 1):
        print(f"\n文本块 {i}:")
        print(f"来源: {split.metadata.get('source', '未知')}")
        print(f"长度: {len(split.page_content)} 字符")
        print(f"内容: {split.page_content[:150]}...")

    print()
    print("=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    print()

    print("✅ 文档处理测试通过")
    print(f"   - 成功加载 {len(documents)} 个文档")
    print(f"   - 切分为 {len(splits)} 个文本块")
    print()
    print("🎯 可以继续进行向量库构建")
    print()
    print("💡 下一步:")
    print("   1. 使用 ChromaDB 构建向量库")
    print("   2. 测试语义搜索功能")
    print("   3. 集成到 RAG 智能体")


if __name__ == "__main__":
    main()
