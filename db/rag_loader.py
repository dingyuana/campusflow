"""
Day 2: 文档加载与智能切分
针对《校园报到手册》PDF 的智能切分策略
"""

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import re


def load_and_split_handbook(pdf_path: str):
    """
    加载报到手册并进行语义友好的切分
    
    策略：按段落切分，保留上下文标题
    
    Args:
        pdf_path: PDF 文件路径
        
    Returns:
        切分后的文档块列表
    """
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    # 预处理：合并页眉页脚，提取标题层级
    processed_docs = []
    for doc in documents:
        # 清理页码等噪声
        cleaned = re.sub(r'\n\s*\d+\s*\n', '\n', doc.page_content)
        # 识别标题（如"三、缴费说明"）
        if re.match(r'^[一二三四五六七八九十]+、', cleaned.strip()):
            doc.metadata["is_header"] = True
        processed_docs.append(doc)
    
    # 递归字符切分：chunk_size=500，保留段落完整性
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""],
        length_function=len,
        is_separator_regex=False
    )
    
    chunks = text_splitter.split_documents(processed_docs)
    
    # 增强 metadata：继承章节标题
    for chunk in chunks:
        # 简单的上下文增强：如果 chunk 以"("开头，可能接上一段
        if chunk.page_content.startswith(("(", "（", "[", "【")):
            chunk.metadata["context_hint"] = "continued"
    
    print(f"📄 原始文档页数：{len(documents)}")
    print(f"✂️ 切分后 chunks 数：{len(chunks)}")
    print(f"📊 平均 chunk 长度：{sum(len(c.page_content) for c in chunks)/len(chunks):.0f} 字符")
    
    return chunks
