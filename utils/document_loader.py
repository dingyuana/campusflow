"""
多格式文档加载器
Day 2: 支持 PDF、Word、Excel 文档加载

功能：
- PDF: PyPDFLoader、UnstructuredPDFLoader
- Word: UnstructuredWordDocumentLoader、Docx2txtLoader
- Excel: UnstructuredExcelLoader

教学计划 Day 2 要求：
- 使用 PyPDFLoader/UnstructuredLoader 处理文档
- 完成文本清洗、语义切分
"""

import os
from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document


class DocumentLoader:
    """
    多格式文档加载器
    
    支持格式：
    - PDF (.pdf)
    - Word (.doc, .docx)
    - Excel (.xls, .xlsx, .csv)
    - Text (.txt, .md)
    """
    
    def __init__(self):
        """初始化文档加载器"""
        self.supported_extensions = {
            '.pdf': 'pdf',
            '.doc': 'word',
            '.docx': 'word',
            '.xls': 'excel',
            '.xlsx': 'excel',
            '.csv': 'excel',
            '.txt': 'text',
            '.md': 'text'
        }
    
    def load_document(self, file_path: str) -> List[Document]:
        """
        加载单个文档
        
        Args:
            file_path: 文档路径
            
        Returns:
            Document 列表
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不支持的文件格式
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"❌ 文件不存在: {file_path}")
        
        ext = path.suffix.lower()
        
        if ext not in self.supported_extensions:
            raise ValueError(
                f"❌ 不支持的文件格式: {ext}\n"
                f"   支持的格式: {', '.join(self.supported_extensions.keys())}"
            )
        
        doc_type = self.supported_extensions[ext]
        
        print(f"📄 加载文档: {path.name}")
        print(f"   类型: {doc_type.upper()}, 大小: {path.stat().st_size / 1024:.1f} KB")
        
        # 根据类型选择加载器
        if doc_type == 'pdf':
            return self._load_pdf(file_path)
        elif doc_type == 'word':
            return self._load_word(file_path)
        elif doc_type == 'excel':
            return self._load_excel(file_path)
        elif doc_type == 'text':
            return self._load_text(file_path)
        
        return []
    
    def load_documents_from_directory(
        self,
        directory: str,
        extensions: Optional[List[str]] = None
    ) -> List[Document]:
        """
        从目录加载所有支持的文档
        
        Args:
            directory: 目录路径
            extensions: 指定加载的文件扩展名（默认加载所有支持的格式）
            
        Returns:
            Document 列表
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"❌ 目录不存在: {directory}")
        
        if not dir_path.is_dir():
            raise ValueError(f"❌ 路径不是目录: {directory}")
        
        # 确定要加载的扩展名
        if extensions is None:
            extensions = list(self.supported_extensions.keys())
        
        # 收集所有文件
        all_files = []
        for ext in extensions:
            all_files.extend(dir_path.glob(f"*{ext}"))
            all_files.extend(dir_path.glob(f"*{ext.upper()}"))
        
        # 去重并排序
        all_files = sorted(set(all_files))
        
        print(f"📁 扫描目录: {directory}")
        print(f"   找到 {len(all_files)} 个文件")
        print()
        
        # 加载所有文档
        all_documents = []
        for file_path in all_files:
            try:
                docs = self.load_document(str(file_path))
                all_documents.extend(docs)
                print(f"   ✅ 成功: {file_path.name}")
            except Exception as e:
                print(f"   ❌ 失败: {file_path.name} - {e}")
        
        print()
        print(f"📊 总计加载: {len(all_documents)} 个文档块")
        
        return all_documents
    
    def _load_pdf(self, file_path: str) -> List[Document]:
        """
        加载 PDF 文档
        
        使用 PyPDFLoader，每页作为一个 Document
        """
        try:
            from langchain_community.document_loaders import PyPDFLoader
            
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # 添加元数据
            for i, doc in enumerate(documents):
                doc.metadata.update({
                    'source': file_path,
                    'page': i + 1,
                    'type': 'pdf'
                })
            
            print(f"   ✅ PDF 加载成功: {len(documents)} 页")
            return documents
            
        except Exception as e:
            print(f"   ⚠️  PyPDFLoader 失败，尝试 UnstructuredPDFLoader: {e}")
            
            try:
                from langchain_community.document_loaders import UnstructuredPDFLoader
                
                loader = UnstructuredPDFLoader(file_path, mode="elements")
                documents = loader.load()
                
                for doc in documents:
                    doc.metadata.update({
                        'source': file_path,
                        'type': 'pdf'
                    })
                
                print(f"   ✅ PDF 加载成功: {len(documents)} 个元素")
                return documents
                
            except Exception as e2:
                raise RuntimeError(f"PDF 加载失败: {e2}")
    
    def _load_word(self, file_path: str) -> List[Document]:
        """
        加载 Word 文档
        
        使用 UnstructuredWordDocumentLoader
        """
        try:
            from langchain_community.document_loaders import UnstructuredWordDocumentLoader
            
            loader = UnstructuredWordDocumentLoader(file_path, mode="elements")
            documents = loader.load()
            
            for doc in documents:
                doc.metadata.update({
                    'source': file_path,
                    'type': 'word'
                })
            
            print(f"   ✅ Word 加载成功: {len(documents)} 个元素")
            return documents
            
        except Exception as e:
            print(f"   ⚠️  UnstructuredWordDocumentLoader 失败，尝试 Docx2txtLoader: {e}")
            
            try:
                from langchain_community.document_loaders import Docx2txtLoader
                
                loader = Docx2txtLoader(file_path)
                documents = loader.load()
                
                for doc in documents:
                    doc.metadata.update({
                        'source': file_path,
                        'type': 'word'
                    })
                
                print(f"   ✅ Word 加载成功: {len(documents)} 段")
                return documents
                
            except Exception as e2:
                raise RuntimeError(f"Word 加载失败: {e2}")
    
    def _load_excel(self, file_path: str) -> List[Document]:
        """
        加载 Excel/CSV 文档
        
        使用 UnstructuredExcelLoader 或 CSVLoader
        """
        path = Path(file_path)
        
        if path.suffix.lower() == '.csv':
            try:
                from langchain_community.document_loaders.csv_loader import CSVLoader
                
                loader = CSVLoader(file_path)
                documents = loader.load()
                
                for doc in documents:
                    doc.metadata.update({
                        'source': file_path,
                        'type': 'csv'
                    })
                
                print(f"   ✅ CSV 加载成功: {len(documents)} 行")
                return documents
                
            except Exception as e:
                raise RuntimeError(f"CSV 加载失败: {e}")
        
        else:
            # Excel 文件 (.xls, .xlsx)
            try:
                from langchain_community.document_loaders import UnstructuredExcelLoader
                
                loader = UnstructuredExcelLoader(file_path, mode="elements")
                documents = loader.load()
                
                for doc in documents:
                    doc.metadata.update({
                        'source': file_path,
                        'type': 'excel'
                    })
                
                print(f"   ✅ Excel 加载成功: {len(documents)} 个元素")
                return documents
                
            except Exception as e:
                raise RuntimeError(f"Excel 加载失败: {e}")
    
    def _load_text(self, file_path: str) -> List[Document]:
        """
        加载纯文本文档
        
        使用 TextLoader
        """
        try:
            from langchain_community.document_loaders import TextLoader
            
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            
            for doc in documents:
                doc.metadata.update({
                    'source': file_path,
                    'type': 'text'
                })
            
            print(f"   ✅ 文本加载成功: {len(documents)} 个文档")
            return documents
            
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                from langchain_community.document_loaders import TextLoader
                
                loader = TextLoader(file_path, encoding='gbk')
                documents = loader.load()
                
                for doc in documents:
                    doc.metadata.update({
                        'source': file_path,
                        'type': 'text'
                    })
                
                print(f"   ✅ 文本加载成功 (GBK): {len(documents)} 个文档")
                return documents
                
            except Exception as e:
                raise RuntimeError(f"文本加载失败: {e}")


def test_document_loader():
    """
    测试文档加载器
    """
    print("=" * 60)
    print("🧪 多格式文档加载器测试")
    print("=" * 60)
    print()
    
    loader = DocumentLoader()
    
    # 检查教学文件目录
    docs_dir = "docs/教学文件/ragfiles"
    
    if not Path(docs_dir).exists():
        print(f"⚠️  目录不存在: {docs_dir}")
        print("   请确保文档目录存在")
        return
    
    # 加载所有文档
    try:
        documents = loader.load_documents_from_directory(docs_dir)
        
        print()
        print("=" * 60)
        print(f"🎉 文档加载完成！")
        print(f"   总计: {len(documents)} 个文档块")
        print("=" * 60)
        
        # 显示前几个文档的信息
        print("\n📋 文档样本:")
        for i, doc in enumerate(documents[:3], 1):
            print(f"\n【文档 {i}】")
            print(f"   来源: {doc.metadata.get('source', 'unknown')}")
            print(f"   类型: {doc.metadata.get('type', 'unknown')}")
            print(f"   内容: {doc.page_content[:200]}...")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    test_document_loader()
