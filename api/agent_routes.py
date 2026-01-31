"""
Agent API 路由
提供 Agent 对话接口
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import asyncio

from api.services.agent_service import get_agent_service, get_quick_response


# 创建路由
router = APIRouter(prefix="/agent", tags=["Agent"])


# 请求模型
class ChatRequest(BaseModel):
    user_id: str
    message: str
    thread_id: Optional[str] = None


class ClearHistoryRequest(BaseModel):
    thread_id: str


# 响应模型
class ChatResponse(BaseModel):
    success: bool
    response: str
    thread_id: str
    user_id: str
    message_count: int
    error: Optional[str] = None


class StatsResponse(BaseModel):
    messages: int
    queries: int
    searches: int


class QuickResponse(BaseModel):
    topic: str
    title: str
    content: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Agent 对话接口
    
    - **user_id**: 用户ID
    - **message**: 用户消息
    - **thread_id**: 对话线程ID（可选，不传则自动创建）
    """
    try:
        service = get_agent_service()
        
        # 如果没有 thread_id，创建一个
        thread_id = request.thread_id or f"{request.user_id}_{asyncio.get_event_loop().time()}"
        
        # 调用服务
        result = await service.chat(
            user_id=request.user_id,
            message=request.message,
            thread_id=thread_id
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quick/{topic}", response_model=Optional[QuickResponse])
async def get_quick_info(topic: str):
    """
    获取快捷信息
    
    - **topic**: 主题，可选值: 报到, 宿舍, 选课, 缴费, 导航, 食堂
    """
    response = get_quick_response(topic)
    if response:
        return QuickResponse(topic=topic, **response)
    return None


@router.get("/quick/list", response_model=List[str])
async def list_quick_topics():
    """列出所有可用的快捷主题"""
    from api.services.agent_service import QUICK_RESPONSES
    return list(QUICK_RESPONSES.keys())


@router.post("/clear")
async def clear_history(request: ClearHistoryRequest):
    """清空对话历史"""
    try:
        service = get_agent_service()
        success = service.clear_history(request.thread_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{thread_id}", response_model=StatsResponse)
async def get_stats(thread_id: str):
    """获取对话统计"""
    try:
        service = get_agent_service()
        stats = service.get_stats(thread_id)
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def agent_health():
    """Agent 服务健康检查"""
    try:
        service = get_agent_service()
        return {
            "status": "healthy",
            "service": "CampusAgent",
            "conversations": len(service.conversation_history)
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
