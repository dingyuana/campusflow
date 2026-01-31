# FastAPI 基础入门

## 📋 概述

FastAPI 是一个现代、高性能的 Python Web 框架，专门用于构建 API。它基于 Starlette（异步 Web 框架）和 Pydantic（数据验证库），提供了极佳的性能和开发体验。

### 为什么选择 FastAPI？

| 特性 | 说明 |
|------|------|
| **高性能** | 基于 Starlette 和 Uvicorn，性能接近 Node.js 和 Go |
| **自动文档** | 自动生成 OpenAPI 文档，自带 Swagger UI 和 ReDoc 界面 |
| **类型提示** | 完全基于 Python 类型提示，IDE 支持好 |
| **数据验证** | 基于 Pydantic，自动进行请求/响应数据验证 |
| **异步支持** | 原生支持 async/await，适合 I/O 密集型应用 |
| **依赖注入** | 强大的依赖注入系统，便于代码复用和测试 |

---

## 🚀 快速开始

### 1. 安装 FastAPI

```bash
# 基础安装
pip install fastapi

# 包含服务器（推荐）
pip install fastapi uvicorn

# 国内镜像加速
pip install fastapi uvicorn --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 第一个 FastAPI 应用

```python
from fastapi import FastAPI

# 创建 FastAPI 实例
app = FastAPI(
    title="CampusFlow API",
    description="智慧校园系统 API 接口",
    version="1.0.0"
)

# 定义路由
@app.get("/")
def read_root():
    """根路径 - 返回欢迎信息"""
    return {
        "message": "Welcome to CampusFlow API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# 带参数的路由
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    """
    获取指定 ID 的物品
    
    Args:
        item_id: 物品 ID（路径参数）
        q: 查询参数（可选）
    """
    return {"item_id": item_id, "q": q}

# 启动服务器（方式1：直接运行）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3. 启动服务器

```bash
# 方式1：使用 Python 直接运行
python main.py

# 方式2：使用 uvicorn 命令行（推荐）
uvicorn main:app --reload

# 参数说明
# main:app - main.py 文件中的 app 对象
# --reload - 开发模式，代码变更自动重启
# --host 0.0.0.0 - 监听所有网络接口
# --port 8000 - 指定端口
```

### 4. 访问 API

```bash
# 访问 API
http://localhost:8000/

# 访问自动生成的文档（Swagger UI）
http://localhost:8000/docs

# 访问替代文档（ReDoc）
http://localhost:8000/redoc
```

---

## 📦 核心概念

### 1. 路由（Routing）

#### HTTP 方法装饰器

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items")          # GET - 获取资源
@app.post("/items")         # POST - 创建资源
@app.put("/items/{id}")     # PUT - 更新资源（完整）
@app.patch("/items/{id}")   # PATCH - 更新资源（部分）
@app.delete("/items/{id}")  # DELETE - 删除资源
```

#### 路径参数

```python
from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/students/{student_id}")
def get_student(
    student_id: int = Path(
        ...,                    # 必需参数
        title="学生 ID",         # 参数标题
        description="学生的唯一标识符",
        gt=0                     # 必须大于 0
    )
):
    """获取指定学生信息"""
    return {"student_id": student_id}

# 多个路径参数
@app.get("/courses/{course_id}/students/{student_id}")
def get_course_student(course_id: int, student_id: int):
    """获取指定课程的指定学生"""
    return {"course_id": course_id, "student_id": student_id}
```

#### 查询参数

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/students")
def list_students(
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(10, description="返回的最大记录数", le=100),
    name: str = Query(None, description="按姓名筛选")
):
    """
    获取学生列表
    
    查询参数：
    - skip: 分页偏移量（默认 0）
    - limit: 每页数量（默认 10，最大 100）
    - name: 姓名筛选（可选）
    """
    return {
        "skip": skip,
        "limit": limit,
        "name": name
    }

# 必需查询参数
@app.get("/search")
def search(q: str = Query(..., min_length=3)):
    """搜索（查询参数 q 必需且至少 3 个字符）"""
    return {"query": q}
```

#### 请求体（Request Body）

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# 定义请求模型
class StudentCreate(BaseModel):
    """创建学生的请求模型"""
    name: str = Field(..., min_length=2, max_length=50, description="学生姓名")
    student_no: str = Field(..., pattern=r"^\d{10}$", description="学号（10位数字）")
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="邮箱")
    age: Optional[int] = Field(None, ge=16, le=30, description="年龄")
    major: str = Field(..., description="专业")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "张三",
                "student_no": "2024001001",
                "email": "zhangsan@example.com",
                "age": 20,
                "major": "计算机科学"
            }
        }

@app.post("/students", status_code=201)
def create_student(student: StudentCreate):
    """
    创建新学生
    
    FastAPI 会自动：
    1. 解析 JSON 请求体
    2. 验证数据（根据 Pydantic 模型）
    3. 转换数据类型
    4. 提供自动补全和类型检查
    """
    return {
        "message": "学生创建成功",
        "data": student,
        "id": 12345
    }
```

---

### 2. Pydantic 数据模型

#### 基础模型定义

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Gender(str, Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class StudentBase(BaseModel):
    """学生基础模型"""
    name: str = Field(..., min_length=2, max_length=50)
    email: str
    age: Optional[int] = Field(None, ge=16, le=60)
    gender: Gender = Field(default=Gender.OTHER)

class StudentCreate(StudentBase):
    """创建学生请求模型"""
    password: str = Field(..., min_length=8, max_length=100)

class StudentUpdate(BaseModel):
    """更新学生请求模型（所有字段可选）"""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[str] = None
    age: Optional[int] = Field(None, ge=16, le=60)

class StudentInDB(StudentBase):
    """数据库中的学生模型（包含额外字段）"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # 支持从 ORM 对象创建

class StudentResponse(BaseModel):
    """学生响应模型"""
    code: int = 200
    message: str = "success"
    data: StudentInDB
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": {
                    "id": 1,
                    "name": "张三",
                    "email": "zhangsan@example.com",
                    "age": 20,
                    "gender": "male",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00"
                }
            }
        }
```

#### 自定义验证器

```python
from pydantic import BaseModel, validator, ValidationError

class StudentCreate(BaseModel):
    name: str
    email: str
    student_no: str
    age: int
    
    @validator('email')
    def validate_email(cls, v):
        """验证邮箱格式"""
        if '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v.lower()  # 转换为小写
    
    @validator('student_no')
    def validate_student_no(cls, v):
        """验证学号格式（10位数字）"""
        if not v.isdigit() or len(v) != 10:
            raise ValueError('学号必须是10位数字')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        """验证年龄范围"""
        if v < 16 or v > 30:
            raise ValueError('年龄必须在16-30岁之间')
        return v
```

---

### 3. 依赖注入（Dependency Injection）

#### 基础依赖

```python
from fastapi import FastAPI, Depends, HTTPException
from typing import Optional

app = FastAPI()

# 定义依赖函数
def common_parameters(
    skip: int = 0,
    limit: int = 10,
    q: Optional[str] = None
):
    """通用分页参数"""
    return {"skip": skip, "limit": limit, "q": q}

# 使用依赖
@app.get("/students")
def read_students(commons: dict = Depends(common_parameters)):
    """获取学生列表（使用通用参数）"""
    return commons

@app.get("/courses")
def read_courses(commons: dict = Depends(common_parameters)):
    """获取课程列表（使用通用参数）"""
    return commons
```

#### 数据库依赖

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

app = FastAPI()

# 数据库连接依赖
def get_db():
    """
    获取数据库会话
    使用 yield 确保会话正确关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/students/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):
    """
    获取学生信息
    
    Args:
        student_id: 学生 ID
        db: 数据库会话（自动注入）
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return student

@app.post("/students")
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    """创建学生"""
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student
```

#### 认证依赖

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    获取当前登录用户
    
    从 Authorization Header 中提取 Token 并验证
    """
    token = credentials.credentials
    user = verify_token(token)  # 自定义验证逻辑
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.get("/users/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息（需要认证）"""
    return current_user

@app.post("/admin/only")
def admin_only(
    current_user: User = Depends(get_current_user)
):
    """仅管理员可访问"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="权限不足")
    return {"message": "管理员专用接口"}
```

---

### 4. 异常处理

#### HTTP 异常

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

@app.get("/students/{student_id}")
def get_student(student_id: int):
    """获取学生信息"""
    student = find_student_by_id(student_id)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"学生 ID {student_id} 不存在"
        )
    
    return student

@app.post("/students")
def create_student(student: StudentCreate):
    """创建学生"""
    if email_exists(student.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"邮箱 {student.email} 已被注册"
        )
    
    # 创建逻辑...
    return {"message": "创建成功"}
```

#### 全局异常处理器

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求验证错误
    
    自定义验证错误的响应格式
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "请求参数验证失败",
            "errors": exc.errors()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    处理 HTTP 异常
    
    统一错误响应格式
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    处理所有未捕获的异常
    
    防止内部错误信息泄露
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误"
        }
    )
```

---

### 5. 中间件

#### 创建中间件

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

app = FastAPI()

# CORS 中间件（跨域支持）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 自定义日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    记录所有 HTTP 请求
    
    记录请求方法、路径、处理时间和状态码
    """
    start_time = time.time()
    
    # 记录请求开始
    logging.info(f"Request: {request.method} {request.url.path}")
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    
    # 记录请求完成
    logging.info(
        f"Response: {request.method} {request.url.path} "
        f"- Status: {response.status_code} "
        f"- Time: {process_time:.3f}s"
    )
    
    # 添加自定义响应头
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# 认证中间件示例
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """添加安全响应头"""
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response
```

---

## 🎯 实战示例：CampusFlow API

### 项目结构

```
api/
├── __init__.py
├── main.py              # FastAPI 主入口
├── student_routes.py    # 学生相关路由
├── dao/                 # 数据访问层
│   ├── __init__.py
│   ├── student_dao.py
│   └── course_dao.py
└── services/            # 业务逻辑层
    ├── __init__.py
    └── student_service.py
```

### 主入口 (main.py)

```python
"""
FastAPI 主入口
提供 RESTful API 服务
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.student_routes import router as student_router

# 创建 FastAPI 应用
app = FastAPI(
    title="CampusFlow API",
    description="智慧校园系统 API 接口",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(student_router, prefix="/api/v1")

@app.get("/")
def read_root():
    """根路径 - API 信息"""
    return {
        "message": "Welcome to CampusFlow API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "CampusFlow API"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 路由模块 (student_routes.py)

```python
"""
学生相关 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field

router = APIRouter(prefix="/students", tags=["students"])

# 数据模型
class StudentBase(BaseModel):
    """学生基础信息"""
    name: str = Field(..., min_length=2, max_length=50)
    student_no: str = Field(..., pattern=r"^\d{10}$")
    email: str
    major: str

class StudentCreate(StudentBase):
    """创建学生请求"""
    password: str = Field(..., min_length=8)

class StudentUpdate(BaseModel):
    """更新学生请求"""
    name: Optional[str] = None
    email: Optional[str] = None
    major: Optional[str] = None

class StudentInDB(StudentBase):
    """数据库学生模型"""
    id: int
    created_at: str

# 模拟数据
students_db = []

@router.get("/", response_model=List[StudentInDB])
def list_students(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的最大记录数")
):
    """
    获取学生列表
    
    Args:
        skip: 分页偏移量
        limit: 每页数量
    
    Returns:
        学生列表
    """
    return students_db[skip: skip + limit]

@router.get("/{student_id}", response_model=StudentInDB)
def get_student(student_id: int):
    """
    获取指定学生信息
    
    Args:
        student_id: 学生 ID
    
    Returns:
        学生详细信息
    """
    student = next((s for s in students_db if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return student

@router.post("/", response_model=StudentInDB, status_code=201)
def create_student(student: StudentCreate):
    """
    创建新学生
    
    Args:
        student: 学生信息
    
    Returns:
        创建成功的学生信息
    """
    new_student = {
        "id": len(students_db) + 1,
        **student.dict(exclude={"password"}),  # 不返回密码
        "created_at": "2024-01-01T00:00:00"
    }
    students_db.append(new_student)
    return new_student

@router.patch("/{student_id}", response_model=StudentInDB)
def update_student(student_id: int, student_update: StudentUpdate):
    """
    更新学生信息
    
    Args:
        student_id: 学生 ID
        student_update: 更新的字段
    
    Returns:
        更新后的学生信息
    """
    student = next((s for s in students_db if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    # 更新非空字段
    update_data = student_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            student[field] = value
    
    return student

@router.delete("/{student_id}")
def delete_student(student_id: int):
    """
    删除学生
    
    Args:
        student_id: 学生 ID
    
    Returns:
        删除结果
    """
    global students_db
    students_db = [s for s in students_db if s["id"] != student_id]
    return {"message": "学生删除成功"}
```

---

## 📚 学习资源

### 官方文档
- FastAPI 官方文档：https://fastapi.tiangolo.com/
- FastAPI 教程：https://fastapi.tiangolo.com/tutorial/
- Pydantic 文档：https://docs.pydantic.dev/

### 推荐阅读
- 《FastAPI 实战》
- 《Python Web 开发：基于 FastAPI》
- 《RESTful API 设计指南》

---

**文档创建时间**：2026-01-30
**文档维护者**：CampusFlow 项目组
