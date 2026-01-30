# 🎓 智慧校园多智能体系统

基于 LangGraph 的多智能体协作系统，提供智慧校园问答/办事服务。

## 📚 项目简介

本项目是一个企业级多智能体系统实训项目，涵盖从数据层到运维层的全栈技术实践。

### 核心功能

- 🤖 多智能体协作：Orchestrator 编排器 + 专业 Agent
- 📄 RAG 知识检索：校园政策/手册语义搜索
- 🕸️ 知识图谱：复杂关系查询（Neo4j）
- 💾 状态持久化：断点续传、多端同步
- 🧭 校园导航：室内+室外路径规划
- 🌐 全栈交付：Next.js + FastAPI + Vercel

## 🏗️ 技术栈

| 维度 | 技术选型 |
|------|----------|
| 逻辑引擎 | LangGraph + LangChain |
| 业务数据库 | PostgreSQL |
| 向量库 | Chroma DB |
| 知识图谱 | Neo4j |
| 后端框架 | FastAPI |
| 前端框架 | Next.js + Tailwind CSS |
| 部署平台 | Vercel |
| CI/CD | GitHub Actions |

## 📁 项目结构

```
CampusFlow/
├── api/                    # FastAPI 后端接口
│   ├── dao/               # 数据访问层
│   ├── services/          # 业务逻辑层
│   └── main.py            # 接口入口
├── agents/                 # LangGraph 智能体
│   ├── langgraph_basic.py
│   └── langgraph_checkpoint.py
├── db/                     # 数据库相关
│   ├── connect.py
│   ├── models.py
│   ├── seed_data.py
│   └── neo4j_utils.py
├── utils/                  # 工具函数
│   └── rag_utils.py
├── data/                   # 数据文件
├── .env.example            # 环境变量示例
├── requirements.txt        # Python 依赖
└── README.md
```

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone <your-repo-url>
cd CampusFlow
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 国内用户使用清华镜像加速
uv pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云镜像
uv pip install -r requirements.txt --index-url https://mirrors.aliyun.com/pypi/simple/
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的数据库连接信息
```

### 5. 运行测试

```bash
# 测试数据库连接
python db/connect.py
```

## 📝 开发规范

### Git Flow 工作流

- `main`: 生产分支
- `dev`: 开发分支
- `feature/dayX`: 每日特性分支

### Commit 规范

- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `style`: 代码格式
- `refactor`: 重构

## 📖 文档

- [教学大纲](教学大纲.md)
- [教学计划](教学计划.md)

## 📝 License

MIT License
