"""
FastAPI 主入口
提供 RESTful API 服务
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.student_routes import router as student_router
from api.agent_routes import router as agent_router


# 创建 FastAPI 应用
app = FastAPI(
    title="CampusFlow API",
    description="智慧校园系统 API 接口 - 集成多智能体服务",
    version="2.0.0"
)


# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(student_router)
app.include_router(agent_router)


@app.get("/")
def read_root():
    """
    根路径 - API 信息
    """
    return {
        "message": "Welcome to CampusFlow API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    """
    健康检查端点
    """
    return {
        "status": "healthy",
        "service": "CampusFlow API"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
