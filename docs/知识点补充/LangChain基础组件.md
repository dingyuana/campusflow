# LangChain 1.0 基础组件详解

## 📋 概述

LangChain 是一个强大的大语言模型应用开发框架，提供了构建 AI 应用的核心组件。LangChain 1.0 对核心组件进行了重构和优化，提供了更统一的接口和更好的性能。

---

## 📦 核心组件架构

```
┌─────────────────────────────────────────────────────────┐
│                    LangChain 1.0                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Loader  │  │ Splitter │  │Embeddings│           │
│  │ (数据加载)│→│ (文档切分)│→│  (向量化) │           │
│  └──────────┘  └──────────┘  └──────────┘           │
│       ↓              ↓              ↓                   │
│  ┌──────────────────────────────────────────┐        │
│  │         Vector Store (向量存储)           │        │
│  └──────────────────────────────────────────┘        │
│       ↓                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │Retriever │  │  Chain   │  │  Agent   │        │
│  │ (检索器) │→│  (链)    │→│ (智能体)  │        │
│  └──────────┘  └──────────┘  └──────────┘        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 1. Loader（文档加载器）

### 1.1 基础概念

**Loader** 是用于从各种数据源加载文档的组件，将非结构化数据转换为 LangChain 的标准 Document 格式。

**Document 结构**：
```python
Document(
    page_content="文档内容",
    metadata={
        "source": "文件路径",
        "page": 1,
        "author": "作者"
    }
)
```

### 1.2 常用 Loader

#### PDF Loader

```python
from langchain_community.document_loaders import PyPDFLoader

# 加载 PDF 文档
loader = PyPDFLoader("docs/教学文件/ragfiles/2025年本科新生报到手册.pdf")
documents = loader.load()

print(f"加载了 {len(documents)} 页")
print(f"第一页内容: {documents[0].page_content[:100]}...")
print(f"元数据: {documents[0].metadata}")
```

**输出**：
```
加载了 29 页
第一页内容: 2025年本科新生报到手册...

元数据: {
    'source': 'docs/教学文件/ragfiles/2025年本科新生报到手册.pdf',
    'page': 1
}
```

#### Text Loader

```python
from langchain_community.document_loaders import TextLoader

# 加载文本文件
loader = TextLoader("data/README.txt", encoding='utf-8')
documents = loader.load()
```

#### Word Loader

```python
from langchain_community.document_loaders import Docx2txtLoader

# 加载 Word 文档
loader = Docx2txtLoader("docs/教学文件/ragfiles/院校简介.docx")
documents = loader.load()
```

#### Web Loader

```python
from langchain_community.document_loaders import WebBaseLoader

# 加载网页
loader = WebBaseLoader("https://example.com")
documents = loader.load()
```

#### Directory Loader

```python
from langchain_community.document_loaders import DirectoryLoader

# 加载整个目录
loader = DirectoryLoader(
    "docs/教学文件/ragfiles/",
    glob="**/*.pdf",  # 只加载 PDF 文件
    show_progress=True
)
documents = loader.load()
```

#### JSON Loader

```python
from langchain_community.document_loaders import JSONLoader

# 加载 JSON 文件
loader = JSONLoader(
    file_path="data/data.json",
    jq=".documents[]",  # jq 查询语句
    text_content=False
)
documents = loader.load()
```

### 1.3 自定义 Loader

```python
from langchain_core.documents import Document
from typing import List
from pathlib import Path

class CustomLoader:
    """
    自定义文档加载器
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[Document]:
        """加载文档"""
        # 自定义加载逻辑
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 创建 Document 对象
        return [
            Document(
                page_content=content,
                metadata={"source": self.file_path}
            )
        ]

# 使用自定义 Loader
loader = CustomLoader("data/custom.txt")
documents = loader.load()
```

---

## 2. Splitter（文档切分器）

### 2.1 基础概念

**Splitter** 用于将长文档切分为小的、语义完整的文本块（chunks），以便于向量化和检索。

**切分原则**：
1. **语义完整性**：在语义边界（段落、句子）切分
2. **合理的重叠**：相邻文本块有一定重叠，避免信息丢失
3. **合适的大小**：通常 400-800 字符

### 2.2 RecursiveCharacterTextSplitter

这是 LangChain 推荐的切分器，能够递归尝试多种分隔符。

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 创建切分器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,          # 文本块大小
    chunk_overlap=50,        # 文本块重叠
    length_function=len,      # 长度计算函数
    separators=[             # 分隔符列表（按优先级）
        "\n\n",  # 段落
        "\n",     # 行
        "。",    # 中文句号
        "！",    # 中文感叹号
        "？",    # 中文问号
        ".",     # 英文句号
        "!",     # 英文感叹号
        "?",     # 英文问号
        " ",     # 空格
        ""       # 兜底
    ]
)

# 切分文档
splits = text_splitter.split_documents(documents)

print(f"切分后文本块数量: {len(splits)}")
```

**切分效果**：
```python
# 原始文档
"新生报到时间：每年 9 月 1 日至 9 月 5 日。报到地点：学校主楼大厅。所需材料：录取通知书、身份证原件及复印件。"

# 文本块 1
"新生报到时间：每年 9 月 1 日至 9 月 5 日。报到地点：学校主楼大厅。"

# 文本块 2（有 50 字符重叠）
"报到地点：学校主楼大厅。所需材料：录取通知书、身份证原件及复印件。"
```

### 2.3 CharacterTextSplitter

基于字符的简单切分器。

```python
from langchain_text_splitters import CharacterTextSplitter

text_splitter = CharacterTextSplitter(
    separator="\n",      # 分隔符
    chunk_size=500,
    chunk_overlap=50,
    length_function=len
)

splits = text_splitter.split_documents(documents)
```

### 2.4 其他切分器

#### HTML 标题切分器

```python
from langchain_text_splitters import HTMLHeaderTextSplitter

html_splitter = HTMLHeaderTextSplitter(
    headers_to_split_on=[
        ("h1", "Header 1"),
        ("h2", "Header 2"),
        ("h3", "Header 3")
    ]
)

splits = html_splitter.split_text(html_content)
```

#### Markdown 切分器

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter

markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3")
    ]
)

splits = markdown_splitter.split_text(markdown_content)
```

### 2.5 切分器参数调优

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `chunk_size` | 400-800 | 文本块大小，根据模型调整 |
| `chunk_overlap` | 50-100 | 重叠大小，通常为 chunk_size 的 10-15% |
| `separators` | 按优先级排序 | 优先使用语义分隔符 |

---

## 3. Embeddings（嵌入模型）

### 3.1 基础概念

**Embeddings** 将文本转换为数值向量，使相似文本在向量空间中距离更近。

### 3.2 使用 HuggingFace Embeddings

```python
from langchain_community.embeddings import HuggingFaceEmbeddings

# 初始化 Embeddings 模型
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",  # 模型名称
    model_kwargs={'device': 'cpu'},  # 使用 CPU
    encode_kwargs={'normalize_embeddings': True}  # 归一化
)

# 生成文档向量
text = "新生报到需要准备什么材料？"
vector = embeddings.embed_query(text)

print(f"向量维度: {len(vector)}")
print(f"向量前5个值: {vector[:5]}")
```

**输出**：
```
向量维度: 1024
向量前5个值: [0.0234, -0.1567, 0.8721, 0.4532, -0.2312]
```

### 3.3 批量生成向量

```python
# 批量生成文档向量
texts = [
    "新生报到需要准备录取通知书",
    "学校有多个重点实验室",
    "学生违纪分为警告、严重警告等"
]

vectors = embeddings.embed_documents(texts)

print(f"生成了 {len(vectors)} 个向量")
```

### 3.4 使用 OpenAI Embeddings

```python
from langchain_openai import OpenAIEmbeddings

# 初始化 OpenAI Embeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key="your-api-key"
)

# 生成向量
vector = embeddings.embed_query("查询文本")
```

---

## 4. Vector Store（向量存储）

### 4.1 基础概念

**Vector Store** 是专门用于存储和检索向量的数据库，支持高效的相似度搜索。

### 4.2 ChromaDB

```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# 初始化 Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    encode_kwargs={'normalize_embeddings': True}
)

# 创建向量数据库（内存模式）
vector_store = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    collection_name="campus_knowledge"
)

# 持久化到磁盘
vector_store = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="./db/chroma_db",
    collection_name="campus_knowledge"
)

# 加载已存在的向量数据库
vector_store = Chroma(
    persist_directory="./db/chroma_db",
    embedding_function=embeddings,
    collection_name="campus_knowledge"
)
```

### 4.3 相似度搜索

```python
# 相似度搜索
query = "新生报到需要准备什么材料？"
results = vector_store.similarity_search(query, k=3)

for i, doc in enumerate(results, 1):
    print(f"结果 {i}:")
    print(f"内容: {doc.page_content[:100]}...")
    print(f"来源: {doc.metadata}")
    print()
```

### 4.4 MMR 搜索（最大边际相关性）

```python
# MMR 搜索（平衡相关性和多样性）
results = vector_store.max_marginal_relevance_search(
    query,
    k=3,
    fetch_k=10  # 从 10 个候选中选择 3 个
)
```

### 4.5 带分数的相似度搜索

```python
# 带相似度分数的搜索
results = vector_store.similarity_search_with_score(query, k=3)

for i, (doc, score) in enumerate(results, 1):
    print(f"结果 {i}:")
    print(f"相似度分数: {score:.4f}")
    print(f"内容: {doc.page_content[:100]}...")
    print()
```

### 4.6 其他 Vector Store

#### FAISS

```python
from langchain_community.vectorstores import FAISS

# 创建 FAISS 向量数据库
vector_store = FAISS.from_documents(
    documents=splits,
    embedding=embeddings
)

# 保存到磁盘
vector_store.save_local("db/faiss_index")

# 加载
vector_store = FAISS.load_local(
    "db/faiss_index",
    embeddings=embeddings,
    allow_dangerous_deserialization=True
)
```

#### Qdrant

```python
from langchain_community.vectorstores import Qdrant

# 创建 Qdrant 向量数据库
vector_store = Qdrant.from_documents(
    documents=splits,
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="campus_knowledge"
)
```

---

## 5. Retriever（检索器）

### 5.1 基础概念

**Retriever** 是用于检索相关文档的组件，可以基于向量相似度、关键词匹配等方式进行检索。

### 5.2 Vector Store Retriever

```python
# 从 Vector Store 创建 Retriever
retriever = vector_store.as_retriever(
    search_type="similarity",      # 检索类型
    search_kwargs={"k": 3}         # 返回结果数量
)

# 执行检索
results = retriever.invoke("报到需要什么材料？")

for doc in results:
    print(doc.page_content)
```

### 5.3 MMRetriever

```python
# 使用 MMR 检索
retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 3,
        "fetch_k": 10  # 从 10 个候选中选择
    }
)
```

### 5.4 最大边际相关性分数检索

```python
# 带分数的 MMR 检索
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "score_threshold": 0.7,  # 相似度阈值
        "k": 3
    }
)
```

### 5.5 自定义 Retriever

```python
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from typing import List

class CustomRetriever(BaseRetriever):
    """自定义检索器"""

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """实现检索逻辑"""
        # 自定义检索逻辑
        results = vector_store.similarity_search(query, k=3)
        return results

# 使用自定义检索器
retriever = CustomRetriever()
results = retriever.invoke("查询文本")
```

---

## 6. Chain（链）

### 6.1 基础概念

**Chain** 是将多个组件串联起来，构建复杂工作流的机制。

### 6.2 LLM Chain

```python
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 创建 LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 创建提示模板
prompt = ChatPromptTemplate.from_template(
    "请回答以下问题：\n{question}"
)

# 创建 Chain
chain = LLMChain(llm=llm, prompt=prompt)

# 执行 Chain
result = chain.invoke({"question": "新生报到需要准备什么材料？"})
print(result["text"])
```

### 6.3 RetrievalQA Chain

```python
from langchain.chains import RetrievalQA

# 创建 RetrievalQA Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # 链类型
    retriever=retriever,
    return_source_documents=True
)

# 执行查询
query = "新生报到需要准备什么材料？"
result = qa_chain.invoke({"query": query})

print(f"回答: {result['result']}")
print(f"来源: {result['source_documents']}")
```

### 6.4 链类型

| 类型 | 说明 |
|------|------|
| `stuff` | 简单拼接所有文档块 |
| `map_reduce` | 分别处理每个文档块，然后合并结果 |
| `refine` | 迭代优化回答 |
| `map_rerank` | 对每个文档块评分，选择最好的 |

### 6.5 Sequential Chain

```python
from langchain.chains import SequentialChain

# Chain 1：提取关键信息
chain1 = LLMChain(
    llm=llm,
    prompt=ChatPromptTemplate.from_template(
        "从以下文本中提取关键信息：\n{text}\n\n关键信息："
    ),
    output_key="key_info"
)

# Chain 2：生成回答
chain2 = LLMChain(
    llm=llm,
    prompt=ChatPromptTemplate.from_template(
        "根据以下关键信息生成回答：\n{key_info}\n\n回答："
    ),
    output_key="answer"
)

# 串联 Chain
overall_chain = SequentialChain(
    chains=[chain1, chain2],
    input_variables=["text"],
    output_variables=["answer"]
)

# 执行
result = overall_chain.invoke({"text": "文本内容"})
print(result["answer"])
```

---

## 7. Agent（智能体）

### 7.1 基础概念

**Agent** 是能够自主决策和执行任务的智能体，可以调用工具来完成复杂任务。

### 7.2 ReAct Agent

```python
from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool

# 定义工具
def search_database(query: str) -> str:
    """搜索数据库"""
    return f"数据库查询结果：{query}"

def search_internet(query: str) -> str:
    """搜索互联网"""
    return f"互联网搜索结果：{query}"

tools = [
    Tool(
        name="DatabaseSearch",
        func=search_database,
        description="搜索校园数据库，回答关于学校政策、规定的问题"
    ),
    Tool(
        name="InternetSearch",
        func=search_internet,
        description="搜索互联网，获取实时信息"
    )
]

# 初始化 Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 执行查询
result = agent.invoke("今天校园有什么活动？")
print(result["output"])
```

### 7.3 OpenAI Functions Agent

```python
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 创建提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个校园智能助手"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# 创建 Agent
agent = create_openai_functions_agent(llm, tools, prompt)

# 创建 Agent 执行器
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

# 执行查询
result = agent_executor.invoke({
    "input": "新生报到需要准备什么材料？",
    "chat_history": []
})
```

---

## 📊 组件对比

| 组件 | 作用 | 输入 | 输出 |
|------|------|------|------|
| **Loader** | 加载数据 | 文件路径/URL | List[Document] |
| **Splitter** | 切分文档 | List[Document] | List[Document] |
| **Embeddings** | 向量化 | 文本 | List[float] |
| **Vector Store** | 存储向量 | Document+Embedding | VectorStore |
| **Retriever** | 检索文档 | 查询文本 | List[Document] |
| **Chain** | 串联组件 | 输入字典 | 输出字典 |
| **Agent** | 自主决策 | 用户问题 | 最终答案 |

---

## 🚀 完整示例：RAG 应用

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# 1. 加载文档
loader = PyPDFLoader("docs/教学文件/ragfiles/2025年本科新生报到手册.pdf")
documents = loader.load()

# 2. 切分文档
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
)
splits = text_splitter.split_documents(documents)

# 3. 创建向量数据库
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    encode_kwargs={'normalize_embeddings': True}
)
vector_store = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="./db/chroma_db",
    collection_name="campus_knowledge"
)

# 4. 创建检索器
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# 5. 创建 LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 6. 创建 RAG Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

# 7. 执行查询
query = "新生报到需要准备什么材料？"
result = qa_chain.invoke({"query": query})

print(f"问题: {query}")
print(f"回答: {result['result']}")
print(f"来源: {[doc.metadata for doc in result['source_documents']]}")
```

---

## 📚 学习资源

### 官方文档
- LangChain 文档：https://python.langchain.com/
- LangChain 1.0 更新日志：https://python.langchain.com/docs/versions/

### 推荐阅读
- 《LangChain 实战》
- 《大语言模型应用开发指南》
- 《RAG 与 LangChain 最佳实践》

---

**文档创建时间**：2026-01-30
**文档维护者**：CampusFlow 项目组
