# CODEBUDDY.md

本文件为 CodeBuddy Code 在本仓库中工作时提供指导。

## 项目概述

这是一个基于 LangGraph 构建智慧校园多智能体问答/服务系统的实训项目。项目实现了一个完整的多智能体系统，包含异构数据融合、协议集成和企业级 CICD 部署。

**核心使命**：从"技术使用"到"工程落地"，构建一个可部署、可交互的智慧校园多智能体问答/办事系统。

## 技术栈

| 组件 | 技术选型 | 说明 |
|-----|---------|------|
| **多智能体引擎** | LangGraph + LangChain | 使用 LangChain-Core 减少依赖体积 |
| **持久化存储** | PostgreSQL | 统一存储业务表、用户记忆、LangGraph Checkpoints。推荐使用 Vercel Postgres/Neon（免费云实例） |
| **非结构化搜索** | Chroma DB | 处理 PDF/Word 文档的 RAG。实训首选本地 Chroma；替代方案：Chroma Cloud、FAISS |
| **关系推理** | Neo4j | 处理复杂的实体关系。推荐使用 Neo4j Aura（免费云实例带可视化界面）。替代方案：ArangoDB |
| **工具连接** | MCP (FastAPI) + 第三方 API | FastAPI 实现 MCP Server（简化版），集成高德/百度地图 API |
| **后端框架** | FastAPI | 高性能 API，支持 SSE 流式传输、自动 Swagger 文档，兼容 Vercel Serverless Functions |
| **前端框架** | Next.js + Tailwind CSS | 全栈框架，无缝对接 Vercel。提供模板降低前端开发复杂度 |
| **部署交付** | Vercel | 托管前端 Next.js 及后端 Serverless Functions。一键部署、自动预览、环境变量管理 |
| **CI/CD 流水线** | GitHub Actions | 自动化测试、代码检查、部署。提供现成 Workflow 模板 |
| **调试工具** | LangSmith | 观察多智能体决策链条、调试状态机、追踪工具调用 |

## 项目结构（标准）

```
campusflow/
├── api/                      # FastAPI 接口层
│   ├── dao/                 # 数据访问对象（PostgreSQL 查询）
│   ├── services/            # 业务逻辑层
│   └── main.py             # FastAPI 应用入口
├── agents/                   # 多智能体实现
│   ├── orchestrator.py     # 意图识别与路由
│   ├── rag_agent.py        # 政策咨询智能体
│   ├── memory_agent.py     # 用户偏好/记忆智能体
│   ├── tool_agent.py       # 工具集成智能体
│   └── langgraph_*.py      # LangGraph 状态机与 Checkpointer
├── db/                       # 数据库工具
│   ├── connect.py          # PostgreSQL 连接
│   ├── models.py           # 表结构定义
│   ├── seed_data.py        # 数据导入脚本
│   ├── neo4j_utils.py      # Neo4j 图操作
│   └── chroma_db/          # 本地 Chroma 存储（自动生成）
├── utils/                    # 工具函数
│   ├── rag_utils.py        # RAG 处理（文本切分、向量化）
│   └── mcp_client.py       # MCP 协议客户端
├── data/                     # 训练数据与文档
│   ├── 校园报到手册.pdf
│   ├── 校园政策指南.pdf
│   └── navigation_data.json
├── frontend/                 # Next.js 前端应用
├── .env                      # 环境变量（永不提交）
├── .gitignore
├── requirements.txt
└── docker-compose.yml       # 可选：本地数据库部署
```

## 数据库架构

### PostgreSQL 表（业务层）

- **student_records**：学生学籍信息（student_id 主键, name, gender, grade, department, admission_date, status）
- **payments**：缴费记录（payment_id 主键, student_id 外键, amount, payment_type, status, payment_date）
- **dormitory**：宿舍分配（dorm_id 主键, student_id 唯一外键, building, floor, room_number, bed_number, check_in_date）
- **user_preference**：用户个性化偏好设置
- **langgraph_checkpoints**：LangGraph 状态持久化（PostgresSaver 自动创建）

### Neo4j 图模型（知识层）

**核心实体**：
- Student（学生）
- Teacher（教师）
- Laboratory（实验室）
- Course（课程）
- Department（院系）

**关系**：
- Student -[TAKES]-> Course（选修）
- Teacher -[TEACHES]-> Course（授课）
- Teacher -[WORKS_IN]-> Laboratory（入驻）
- Student -[BELONGS_TO]-> Department（隶属）

### Chroma 向量存储（文档层）

存储以下文档的语义切分块：
- 校园报到手册
- 校园政策指南
- 校园导航手册

**Embedding 模型**：BAAI/bge-m3（轻量高效，适合实训）

## 常用开发命令

### 环境配置
```bash
# 创建并激活 Python 虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖（国内镜像加速）
uv pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 数据库操作
```bash
# 创建 PostgreSQL 表
python db/models.py

# 导入种子数据
python db/seed_data.py

# 测试 PostgreSQL 连接
python db/connect.py

# 初始化 Neo4j 图（约束和数据）
python db/neo4j_utils.py

# 从 PDF 构建 Chroma 向量库
python utils/rag_utils.py
```

### 后端开发（FastAPI）
```bash
# 运行 FastAPI 开发服务器
python api/main.py

# 使用自动重载运行
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 访问 Swagger UI 文档
# 打开浏览器：http://localhost:8000/docs
```

### 多智能体开发（LangGraph）
```bash
# 测试基础 LangGraph 状态机
python agents/langgraph_basic.py

# 测试 PostgresSaver 状态持久化
python agents/langgraph_checkpoint.py

# 测试编排器意图路由
python agents/orchestrator.py
```

### 前端开发（Next.js）
```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev

# 构建生产版本
npm run build

# 启动生产服务器
npm start
```

### 本地数据库设置（可选 - Docker）
```bash
# 使用 Docker Compose 启动所有数据库
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 删除卷（重置数据库）
docker-compose down -v
```

### 测试
```bash
# 运行 Python 单元测试
pytest tests/ -v

# 运行测试并生成覆盖率报告
pytest tests/ --cov=. --cov-report=html

# 运行特定测试
pytest tests/test_rag_agent.py::test_semantic_search -v
```

### Git 工作流
```bash
# 创建开发分支
git checkout -b dev

# 创建每日特性分支
git checkout -b feature/day1

# 暂存并提交更改（遵循 Conventional Commits）
git add .
git commit -m "feat: 完成项目初始化与PostgreSQL连接测试"

# 推送到远程仓库
git push origin feature/day1

# 在 GitHub 创建 Pull Request
# Base: dev, Compare: feature/day1
```

## 核心开发概念

### 多智能体架构（LangGraph）

**状态设计模式**：
- State 对象是状态机中的核心数据载体
- 常用字段：`thread_id`、`messages`、`current_step`、`student_id`
- 设计状态时只包含需要持久化的数据

**节点开发**：
- 每个节点是纯函数：`输入状态 -> 输出状态`
- 单一职责原则
- 返回更新后的 State 对象

**边类型**：
- 普通边：顺序执行
- 条件边：基于状态的动态路由
- 入口/出口点：定义工作流的开始和结束

### Checkpointer 与状态持久化

**PostgresSaver 配置**：
```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(
    conn_string=os.getenv("POSTGRES_URL"),
    table_name="langgraph_checkpoints"
)
```

**Thread ID 设计**：
- 每个用户会话的唯一标识符
- 关联用户信息和状态信息
- 使用 UUID 或格式化字符串：`thread_001`、`user_{student_id}`

**状态恢复**：
```python
# 从线程加载之前的状态
config = {"configurable": {"thread_id": thread_id}}
state = graph.get_state(config)

# 从检查点继续执行
result = graph.invoke(None, config=config)
```

### RAG 实现

**语义切分最佳实践**：
- 使用 `RecursiveCharacterTextSplitter` 配合语义感知分隔符
- 典型参数：`chunk_size=500`、`chunk_overlap=50`
- 避免破坏语义边界（段落、句子）

**混合检索**：
```python
# 语义搜索（向量相似度）
semantic_results = db.similarity_search(query, k=3)

# 混合搜索（MMR 重排序以增加多样性）
hybrid_results = db.max_marginal_relevance_search(query, k=3, fetch_k=10)
```

### Neo4j Text-to-Cypher

**安全措施**：
- 添加语句过滤以防止危险操作（DELETE、DROP）
- 实现错误重试机制
- 设置查询超时以防止死循环

**查询模式**：
```python
cypher = """
MATCH (s:Student)-[:TAKES]->(c:Course)-[:TEACHES]->(t:Teacher)-[:WORKS_IN]->(l:Laboratory)
WHERE t.name = '张三' AND s-[:BELONGS_TO]->(:Department {name: '计算机学院'})
RETURN s.name, l.name
"""
```

### MCP 协议（简化版）

**实训目的**：
- 重点掌握"标准化工具连接"的概念
- 使用基于 FastAPI 的简化 MCP Server/Client
- 优先理解而非完全符合协议规范

**服务端实现**（FastAPI）：
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/mcp/navigation/indoor")
async def get_indoor_navigation(building: str, destination: str):
    # 返回导航数据
    return {"route": "..."}
```

**客户端集成**：
- 将 MCP 端点封装为 LangChain 工具
- 在 Tool Agent 中用于导航查询
- 生产环境添加身份验证

### SSE 流式传输（后端 + 前端）

**FastAPI SSE 端点**：
```python
from fastapi.responses import StreamingResponse

async def stream_agent_response(thread_id: str, user_input: str):
    async def generate():
        # 流式输出智能体思考链
        yield "data: 意图识别中...\n\n"
        # 流式输出智能体执行
        yield "data: 正在查询数据库...\n\n"
        # 流式输出最终回答
        yield f"data: {final_answer}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

**Next.js SSE 客户端**：
```typescript
const eventSource = new EventSource('/api/stream');
eventSource.onmessage = (event) => {
  // 使用打字效果追加到消息显示
  appendMessage(event.data);
};
```

## 环境变量（.env）

**必需变量**：
```bash
# PostgreSQL (Vercel/Neon)
POSTGRES_URL="postgresql://user:password@host:5432/dbname"

# Neo4j Aura
NEO4J_URI="neo4j+s://xxx.databases.neo4j.io:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="password"

# OpenAI API（或其他 LLM 提供商）
OPENAI_API_KEY="sk-xxx"

# 第三方 API
AMAP_API_KEY="xxx"  # 或 BAIDU_MAP_API_KEY
```

**安全规则**：
- 永不提交 .env 文件
- 所有敏感数据使用环境变量
- 生产环境定期轮换 API 密钥
- 为云资源实施访问控制

## Git 工作流与提交规范

**分支策略**：
- `main`：生产就绪的代码（受保护）
- `dev`：开发集成分支
- `feature/day1`、`feature/day2`：每日特性分支

**提交信息格式**（Conventional Commits）：
```
feat: 添加RAG向量库构建功能
fix: 修复Neo4j查询死循环问题
docs: 更新README部署说明
refactor: 重构DAO层数据访问逻辑
test: 添加学生服务单元测试
```

**Pull Request 指南**：
- 始终从特性分支向 dev 创建 PR
- 包含测试截图和验证步骤
- 合并前请求代码审查
- 保持 PR 聚焦于单一功能

## 部署（Vercel）

### GitHub Actions CI/CD

**工作流触发器**：
- 推送到特性分支：运行测试，创建预览部署
- 向 dev 提交 Pull Request：运行测试、代码检查、创建预览
- 合并到 dev/main：部署到生产环境

**典型工作流步骤**：
1. 安装依赖
2. 运行代码检查（flake8/black）
3. 运行单元测试（pytest）
4. 构建前端（npm run build）
5. 部署到 Vercel

### Vercel 配置

**环境设置**：
1. 将 GitHub 仓库导入 Vercel
2. 配置构建设置：
   - 根目录：`./`
   - 构建命令：空（后端是 Python）
   - 输出目录：`frontend/.next`
3. 在 Vercel 控制台添加环境变量
4. 连接 Vercel PostgreSQL 实例

**Serverless Functions 适配器**：
- FastAPI 作为 Vercel Serverless Function 运行
- 配置 `vercel.json` 进行 API 路由：
```json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/main.py" }
  ]
}
```

## 常见问题与故障排除

### 数据库连接问题
- **症状**：连接超时或身份验证失败
- **解决方案**：检查防火墙规则，验证连接字符串格式，确保云数据库可访问

### Chroma 向量存储错误
- **症状**：Embedding 模型下载失败
- **解决方案**：使用本地模型缓存，检查网络连接，必要时使用镜像站点

### Neo4j 查询性能
- **症状**：多跳查询缓慢
- **解决方案**：在频繁查询的属性上添加索引，优化 Cypher 查询结构，限制结果集

### LangGraph 状态丢失
- **症状**：线程恢复失败或返回错误状态
- **解决方案**：验证 PostgresSaver 配置，确保 thread_id 一致性，检查 PostgreSQL 表创建

### Vercel 部署失败
- **症状**：构建失败或运行时错误
- **解决方案**：检查构建日志，验证 Python 版本兼容性，确保所有依赖列在 requirements.txt 中

## 性能优化技巧

1. **并行节点执行**：对独立节点使用 LangGraph 的并行执行
2. **向量搜索优化**：调整 chunk_size/overlap 参数，使用混合检索
3. **数据库索引**：在 PostgreSQL 频繁查询的列上添加索引
4. **缓存**：为重复查询实现响应缓存
5. **查询批处理**：尽可能批量处理数据库操作
6. **流式传输**：使用 SSE 进行流式响应以减少感知延迟

## 安全最佳实践

1. **护栏机制**：实施隐私数据过滤（身份证号、银行卡号）
2. **速率限制**：为 API 端点添加速率限制
3. **身份验证**：为生产部署实施用户身份验证
4. **输入验证**：处理前验证所有用户输入
5. **密钥管理**：永不硬编码 API 密钥或凭证
6. **SQL 注入防护**：使用参数化查询（LangChain 自动处理）

## 测试策略

**单元测试**：
- 测试单个智能体逻辑
- 测试数据库查询（DAO 层）
- 测试工具函数

**集成测试**：
- 端到端测试多智能体工作流
- 使用真实数据测试 API 端点
- 测试状态持久化和恢复

**手动测试**：
- 验证 RAG 检索准确率（目标：≥80%）
- 测试 Neo4j 多跳查询
- 模拟用户工作流（报到、缴费、宿舍查询、导航）
- 测试检查点恢复（刷新页面、重新打开会话）

## LangSmith 调试

**设置**：
1. 创建 LangSmith 账户（提供免费教育额度）
2. 配置环境变量：`LANGCHAIN_TRACING_V2=true`、`LANGCHAIN_API_KEY="ls-xxx"`

**使用场景**：
- 追踪多智能体决策链
- 调试状态机执行流程
- 监控工具调用序列
- 分析性能瓶颈
- 查看对话历史

## 开发工作流总结

**第 1-2 天**：数据层搭建
- 初始化 PostgreSQL、Chroma、Neo4j
- 导入种子数据并构建向量库

**第 3-4 天**：业务层
- 设计并创建 PostgreSQL 表
- 实现 FastAPI DAO/Service/API 层
- 构建 RAG 和知识图谱查询

**第 5-6 天**：状态与编排
- 实现 LangGraph 状态机
- 配置 PostgresSaver 实现持久化
- 构建带有意图识别的编排器

**第 7-8 天**：智能体开发
- 实现 RAG、Memory 和 Tool 智能体
- 集成 MCP 协议和外部 API
- 测试多智能体协作

**第 9-10 天**：全栈与部署
- 构建 Next.js 前端并实现 SSE
- 配置 GitHub Actions CI/CD
- 部署到 Vercel 生产环境

**第 11 天及以后**（可选）：高级功能
- 性能优化
- 安全增强
- 扩展功能（语音、权限、自动更新）
