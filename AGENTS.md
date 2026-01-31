# AGENTS.md

## 项目概述
CampusFlow 是基于 FastAPI、LangGraph、LangChain、ChromaDB、Supabase 和 Neo4j 构建的多智能体智慧校园系统。

## 构建/测试命令

### 环境配置
```bash
# 创建并激活虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 安装依赖
uv pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 运行测试
项目使用手动测试脚本（无 pytest）。直接运行单个文件：
```bash
python db/connect.py                  # 测试数据库连接
python utils/test_rag_documents.py    # 测试 RAG 文档处理
python utils/rag_test_basic.py        # 测试基础 RAG 功能
python utils/rag_test_simple.py       # 测试简单 RAG
python utils/build_rag_from_docs.py   # 从文档构建 RAG
```

### 运行应用
```bash
uvicorn api.main:app --reload        # FastAPI 服务器
python <module>/<script>.py           # 直接运行脚本
```

## 代码风格指南

### 导入规范
顺序：标准库 → 第三方库 → 本地模块。使用绝对导入。
```python
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.rag_utils import RAGUtils
```

### 格式规范
- 使用 4 个空格缩进，最大行长 88 字符
- 类方法之间保留空行
- 模块末尾使用 `if __name__ == "__main__":` 作为入口

### 类型提示
始终使用类型提示：`List`、`Optional`、`Dict`、`Any`、`None`
```python
def load_documents(self, file_path: str) -> List:
    """加载并返回文件中的文档"""
    pass
```

### 命名规范
- 类名：PascalCase（如 RAGUtils、DocumentLoader）
- 函数/变量：snake_case（如 load_documents、vector_store）
- 常量：UPPER_SNAKE_CASE（如 MAX_RETRIES）
- 私有成员：以下划线开头（如 _internal_method）

### 文档字符串
使用三引号和中文描述。格式：简要说明 → Args → Returns
```python
def similarity_search(self, vector_store: Chroma, query: str, k: int = 3) -> List:
    """语义相似度搜索

    Args:
        vector_store: 向量数据库实例
        query: 查询文本

    Returns:
        相似度最高的文档块列表
    """
```

### 错误处理
使用 try-except 配合 emoji 指示器（✅ ❌ ⚠️）。抛出适当的异常。
```python
try:
    documents = loader.load()
    print(f"✅ 成功加载文档: {file_path}")
except Exception as e:
    print(f"❌ 加载失败: {e}")
    raise
```

### 环境变量配置
使用 `python-dotenv`。敏感信息存储在 `.env` 中，提供 `.env.example`。
```python
from dotenv import load_dotenv
import os
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
```

### 文件操作
所有路径操作使用 `pathlib.Path`。操作前检查文件是否存在。
```python
from pathlib import Path
file_path = Path(docs_directory) / "test.pdf"
if file_path.exists():
    documents = loader.load(str(file_path))
```

### 打印/日志
使用 emoji 表示状态：✅ ❌ ⚠️ 🚀 📚 🔍。使用分隔线。
```python
print("=" * 50)
print("🚀 构建校园知识向量库")
print("=" * 50)
```

### 项目结构
- `api/` - FastAPI 后端（dao、services）
- `agents/` - LangGraph 智能体实现
- `db/` - 数据库连接和模型
- `utils/` - 工具函数和工具
- 保留 `__init__.py` 文件以支持包结构

### Git 工作流
- `main` → 生产环境，`dev` → 开发环境，`feature/dayX-description` → 功能分支
- 提交格式：`type: description`（feat、fix、docs、style、refactor）

### 语言规范
- 文档字符串和注释使用中文，代码标识符使用英文
- 技术术语保留英文（如 FastAPI、ChromaDB、RAG）

### LangChain/LangGraph 规范
- 使用 `langchain_core.documents.Document` 表示文档
- 使用 `RecursiveCharacterTextSplitter` 进行文档切分（size=500, overlap=50）
- 使用 `HuggingFaceEmbeddings` 并设置 `normalize_embeddings=True`
- ChromaDB 持久化目录：`./db/chroma_db`
- 嵌入模型：`BAAI/bge-m3`
