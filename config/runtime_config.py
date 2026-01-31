"""
Day 8: 上下文工程与多租户配置
运行时配置管理与租户隔离
"""

from typing import TypedDict, Optional, Literal
from dataclasses import dataclass
from langchain_core.messages import SystemMessage, HumanMessage


class AgentConfig(TypedDict, total=False):
    """运行时配置"""
    # 身份标识
    user_id: str
    tenant_id: str  # 学院/部门 ID，如 "cs_dept", "art_dept"
    thread_id: str
    
    # 模型配置
    model_name: Literal["gpt-4o-mini", "gpt-4o", "qwen-turbo"]
    temperature: float
    
    # 业务配置
    personality: Literal["professional", "friendly", "humorous"]  # 人格设定
    knowledge_scope: list[str]  # 可访问的知识库列表
    enable_rag: bool
    enable_kg: bool
    
    # 安全策略
    max_tokens: int
    enable_pii_filter: bool


@dataclass
class TenantConfig:
    """租户（学院）级配置"""
    tenant_id: str
    name: str
    vector_collection: str  # 该租户的向量集合名
    neo4j_database: Optional[str]  # 图数据库隔离（Neo4j 4.0+ 支持多库）
    system_prompt: str
    allowed_tools: list[str]
    
    # 行级安全策略（RLS）
    rls_enabled: bool = True


class ConfigManager:
    """配置管理器"""
    
    TENANT_DB = {
        "cs_dept": TenantConfig(
            tenant_id="cs_dept",
            name="计算机学院",
            vector_collection="cs_knowledge",
            system_prompt="你是计算机学院助手，擅长编程、算法、系统架构。回答简洁专业。",
            allowed_tools=["query_handbook", "query_campus_kg", "code_assistant"]
        ),
        "art_dept": TenantConfig(
            tenant_id="art_dept",
            name="艺术学院",
            vector_collection="art_knowledge",
            system_prompt="你是艺术学院助手，富有创意和艺术气质。回答富有感染力。",
            allowed_tools=["query_handbook", "query_campus_kg", "design_inspiration"]
        ),
        "default": TenantConfig(
            tenant_id="default",
            name="通用租户",
            vector_collection="general_knowledge",
            system_prompt="你是校园助手，可以回答各类校园相关问题。",
            allowed_tools=["query_handbook", "query_campus_kg"]
        )
    }
    
    @classmethod
    def get_tenant_config(cls, tenant_id: str) -> TenantConfig:
        """获取租户配置（带缓存）"""
        if tenant_id not in cls.TENANT_DB:
            raise ValueError(f"未知租户：{tenant_id}")
        return cls.TENANT_DB[tenant_id]
    
    @classmethod
    def validate_access(cls, user_id: str, tenant_id: str) -> bool:
        """验证用户是否有权访问该租户（简化版）"""
        # 实际应查询用户-租户关联表
        return True  # 模拟验证通过
    
    @classmethod
    def build_runnable_config(cls, user_id: str, tenant_id: str, **kwargs) -> dict:
        """构建 RunnableConfig"""
        if not cls.validate_access(user_id, tenant_id):
            raise PermissionError("无权访问该租户资源")
        
        tenant = cls.get_tenant_config(tenant_id)
        
        return {
            "configurable": {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "thread_id": kwargs.get("thread_id", f"{tenant_id}_{user_id}"),
                "vector_collection": tenant.vector_collection,
                "system_prompt": tenant.system_prompt,
                "allowed_tools": tenant.allowed_tools,
                **kwargs
            }
        }


def adaptive_response(state: dict, config: dict):
    """
    自适应响应节点：根据配置调整行为
    config 由 LangGraph 自动注入
    """
    # 从 config 中提取运行时配置
    configurable = config.get("configurable", {})
    tenant_id = configurable.get("tenant_id", "default")
    personality = configurable.get("personality", "professional")
    system_prompt = configurable.get("system_prompt", "你是校园助手。")
    
    # 根据人格调整回复风格
    style_instructions = {
        "professional": "使用正式、准确的学术用语。",
        "friendly": "使用亲切、鼓励性的语言，适当使用表情符号。",
        "humorous": "适当加入幽默元素，但保持尊重。"
    }
    
    # 组装系统提示
    full_system_prompt = f"{system_prompt}\n\n回复风格：{style_instructions.get(personality, '')}"
    
    # 限制工具使用（租户隔离）
    allowed_tools = configurable.get("allowed_tools", [])
    
    # 构建增强消息
    messages = state.get("messages", [])
    if messages and not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=full_system_prompt)] + messages
    
    return {
        "messages": messages,
        "tenant_id": tenant_id,
        "allowed_tools": allowed_tools,
        "system_prompt": full_system_prompt
    }


if __name__ == "__main__":
    # 测试多租户配置
    print("🧪 测试多租户配置")
    
    # 计算机学院配置
    cs_config = ConfigManager.build_runnable_config(
        user_id="cs_student_001",
        tenant_id="cs_dept",
        personality="professional"
    )
    print(f"\n计算机学院配置：")
    print(f"  向量集合: {cs_config['configurable']['vector_collection']}")
    print(f"  允许工具: {cs_config['configurable']['allowed_tools']}")
    
    # 艺术学院配置
    art_config = ConfigManager.build_runnable_config(
        user_id="art_student_001",
        tenant_id="art_dept",
        personality="friendly"
    )
    print(f"\n艺术学院配置：")
    print(f"  向量集合: {art_config['configurable']['vector_collection']}")
    print(f"  允许工具: {art_config['configurable']['allowed_tools']}")
    
    # 测试自适应响应
    test_state = {"messages": [HumanMessage(content="你好")]}
    result = adaptive_response(test_state, cs_config)
    print(f"\n自适应响应系统提示：{result['system_prompt'][:50]}...")
