# 文档目录说明

本目录包含 CampusFlow 项目的所有文档和教学材料。

## 📁 目录结构

```
docs/
├── 教学文件/              # 教学相关的文档和测试文件
│   ├── ragfiles/          # RAG 测试文档（PDF、Word、Excel）
│   │   ├── 2025年本科新生报到手册.pdf
│   │   ├── 东华大学2026年硕士研究生招生简章.docx
│   │   ├── 东华大学学生违纪处分规定.pdf
│   │   ├── 院校简介.docx
│   │   └── 院系设置及重点实验室.xlsx
│   └── neo4j知识图谱.md  # Neo4j 知识图谱相关文档
├── 测试报告/              # 项目测试报告
│   ├── 测试报告-Day1-Day2.md    # Day 1-2 测试报告
│   └── RAG测试报告-真实文档.md   # RAG 真实文档测试报告
├── 知识点补充/            # 补充知识点和学习指南
│   ├── Git-GitHub使用指南.md      # Git 和 GitHub 使用指南
│   ├── 环境配置指南.md            # Python 环境配置指南
│   ├── LangChain基础组件.md       # LangChain 核心组件详解
│   ├── RAG全流程解析.md           # RAG 完整流程解析
│   ├── 向量库基本概念.md          # 向量库核心概念
│   ├── FastAPI基础入门.md         # FastAPI 后端开发指南
│   ├── LangGraph多智能体系统.md   # LangGraph 多智能体详解
│   ├── Neo4j图数据库与知识图谱.md # Neo4j 图数据库详解
│   ├── Gradio前端开发指南.md      # Gradio 界面开发指南
│   ├── MCP模型上下文协议.md       # MCP 协议详解
│   └── Docker容器化部署指南.md    # Docker 生产部署指南
├── DEPLOY.md              # 生产部署完整方案
└── README.md              # 本文档
```

## 📚 知识点补充文档

### 基础篇

#### `Git-GitHub使用指南.md`
Git 和 GitHub 的使用指南：
- Git 基础命令（clone、commit、push、branch）
- GitHub 工作流（Fork、PR、Code Review）
- 分支管理策略（Git Flow）
- 提交规范（Conventional Commits）

#### `环境配置指南.md`
Python 虚拟环境配置指南：
- uv venv 使用（快速虚拟环境管理）
- 依赖安装（国内镜像加速）
- 环境变量配置（.env 文件）

### RAG 与向量库篇

#### `LangChain基础组件.md`
LangChain 1.0 基础组件详解（800+行）：
- Loader（文档加载器）：PDF、Word、Web 加载
- Splitter（文档切分器）：RecursiveCharacterTextSplitter 详解
- Embeddings（嵌入模型）：HuggingFace、OpenAI
- Vector Store（向量存储）：Chroma、FAISS、Qdrant
- Retriever（检索器）：相似度检索、MMR、混合检索
- Chain（链）：LLMChain、RetrievalQA
- Agent（智能体）：ReAct、OpenAI Functions

#### `RAG全流程解析.md`
RAG（检索增强生成）全流程深度解析（600+行）：
- 数据加载（Document Loading）
- 文档切分（Document Splitting）
- 向量化（Embeddings）
- 存储（Vector Store）
- 检索（Retrieval）：相似度、MMR、混合
- 生成（Generation）
- 实际应用场景与快速开始

#### `向量库基本概念.md`
向量库核心概念详解（400+行）：
- Embedding（嵌入/向量化）原理
- 相似度匹配（余弦相似度、欧氏距离）
- ChromaDB 实战（增删改查）
- 性能优化（批量操作、索引优化）
- 实际应用场景

### 后端与数据库篇

#### `FastAPI基础入门.md`
FastAPI 后端开发完整指南（700+行）：
- 快速开始与核心概念
- 路由（路径参数、查询参数、请求体）
- Pydantic 数据模型与验证
- 依赖注入（数据库、认证）
- 异常处理与中间件
- 实战示例：CampusFlow API 开发

#### `Neo4j图数据库与知识图谱.md`
Neo4j 图数据库详解（900+行）：
- 核心概念（节点、关系、属性）
- Cypher 查询语言（CREATE、MATCH、SET、DELETE）
- 校园知识图谱实战
- Text-to-Cypher 自然语言转查询
- 性能优化（索引、查询优化）

### 智能体与前端篇

#### `LangGraph多智能体系统.md`
LangGraph 多智能体系统详解（800+行）：
- 核心概念（状态图、节点、边）
- 多智能体架构模式（Supervisor、Sequential、Parallel）
- 持久化和检查点机制
- CampusFlow 实战：智慧校园多智能体系统
- 完整代码示例

#### `Gradio前端开发指南.md`
Gradio 界面开发完整指南（800+行）：
- 快速开始与核心组件
- 输入组件（Textbox、Dropdown、Slider、File）
- 输出组件（Textbox、Chatbot、Markdown）
- 布局管理（Row、Column、Tab）
- 交互与事件（流式输出、异步函数）
- 主题定制与部署
- CampusFlow 实战：智慧校园助手界面

### 协议与部署篇

#### `MCP模型上下文协议.md`
MCP（Model Context Protocol）详解（700+行）：
- 协议概述与架构
- 核心组件（Tools、Resources、Prompts）
- 传输方式（stdio、HTTP with SSE）
- CampusFlow MCP Server 实战
- 工具实现、资源管理、提示模板

#### `Docker容器化部署指南.md`
Docker 生产部署完整指南（600+行）：
- Docker 核心概念（镜像、容器、网络、卷）
- Dockerfile 多阶段构建
- Docker Compose 编排
- 监控配置（Prometheus、Grafana）
- 部署脚本与运维命令
- 完整生产环境配置

## 📚 其他重要文档

### `DEPLOY.md`
生产部署完整方案，包含：
- 项目结构规划
- Dockerfile 配置（API、前端、Nginx）
- docker-compose.prod.yml 生产编排
- 监控栈配置（Prometheus、Grafana）
- 环境变量模板
- 自动化部署脚本
- 运维管理命令

## 🚀 快速开始

### 1. 按天学习

| Day | 主题 | 参考文档 |
|-----|------|----------|
| Day 1 | 项目启动 | `Git-GitHub使用指南.md`、`环境配置指南.md` |
| Day 2 | RAG 向量库 | `RAG全流程解析.md`、`向量库基本概念.md`、`LangChain基础组件.md` |
| Day 3 | 知识图谱 | `Neo4j图数据库与知识图谱.md` |
| Day 4 | 后端开发 | `FastAPI基础入门.md` |
| Day 5 | 智能体状态 | `LangGraph多智能体系统.md` |
| Day 6-8 | 多智能体 | `LangGraph多智能体系统.md`、`MCP模型上下文协议.md` |
| Day 9 | 前端开发 | `Gradio前端开发指南.md` |
| Day 10 | 部署 | `Docker容器化部署指南.md`、`DEPLOY.md` |

### 2. 查看具体文档

```bash
# Git 使用指南
cat docs/知识点补充/Git-GitHub使用指南.md

# RAG 全流程
cat docs/知识点补充/RAG全流程解析.md

# FastAPI 开发
cat docs/知识点补充/FastAPI基础入门.md

# Docker 部署
cat docs/知识点补充/Docker容器化部署指南.md

# 完整部署方案
cat docs/DEPLOY.md
```

## 📝 文档分类说明

### 教学文件
包含测试用的原始文档（PDF、Word、Excel）和各个教学模块的详细说明文档。

### 测试报告
包含各个阶段的测试报告、测试结果统计、技术实现说明。

### 知识点补充
包含工具使用指南、最佳实践、常见问题解答，按主题分类，便于学生按需学习。

---

**文档更新时间**：2026-01-30  
**文档数量**：11 个知识点文档 + 1 个部署方案文档  
**文档维护者**：CampusFlow 项目组
