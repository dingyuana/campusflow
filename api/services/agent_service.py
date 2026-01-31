"""
统一 Agent 服务
整合 Day 1-9 的所有功能
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain.tools import tool

# 导入所有工具
from agents.tools.campus_info import (
    query_campus_library_status,
    query_tuition_payment,
    query_dormitory_info
)


# 初始化模型
llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
    temperature=float(os.getenv("TEMPERATURE", "0.7")),
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)


# 所有可用工具
tools = [
    query_campus_library_status,
    query_tuition_payment,
    query_dormitory_info,
]


class CampusAgentService:
    """
    CampusFlow 统一 Agent 服务
    整合所有功能模块
    """
    
    def __init__(self):
        """初始化服务"""
        self.agent = self._create_agent()
        self.conversation_history: Dict[str, List] = {}
        
    def _create_agent(self):
        """创建 ReAct Agent"""
        system_prompt = """你是 CampusFlow 智慧校园助手，专门为大学新生提供服务。

你的能力包括：
1. 查询图书馆开放状态和座位情况
2. 解答学费缴纳方式和流程
3. 提供宿舍楼信息和住宿指南
4. 回答报到流程相关问题
5. 提供选课建议和学业指导

请使用友好的语气回答学生问题。如果无法回答某个问题，请诚实地告知学生并建议他们联系相关部门。

记住：你正在帮助大学新生适应校园生活！"""
        
        return create_react_agent(
            model=llm,
            tools=tools,
            state_modifier=system_prompt
        )
    
    async def chat(self, user_id: str, message: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """
        处理用户消息
        
        Args:
            user_id: 用户ID
            message: 用户消息
            thread_id: 对话线程ID（可选）
            
        Returns:
            包含回复和元数据的字典
        """
        try:
            # 获取或创建对话历史
            if thread_id not in self.conversation_history:
                self.conversation_history[thread_id] = []
            
            history = self.conversation_history[thread_id]
            
            # 构建消息列表
            messages = history + [HumanMessage(content=message)]
            
            # 调用 Agent
            result = await self.agent.ainvoke({"messages": messages})
            
            # 提取回复
            ai_message = result["messages"][-1]
            response_text = ai_message.content
            
            # 更新历史
            history.extend([
                HumanMessage(content=message),
                AIMessage(content=response_text)
            ])
            
            # 限制历史长度（保留最近10轮）
            if len(history) > 20:
                history = history[-20:]
            self.conversation_history[thread_id] = history
            
            return {
                "success": True,
                "response": response_text,
                "thread_id": thread_id,
                "user_id": user_id,
                "message_count": len(history) // 2
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": "抱歉，服务暂时不可用，请稍后再试。",
                "thread_id": thread_id,
                "user_id": user_id
            }
    
    def clear_history(self, thread_id: str) -> bool:
        """清空对话历史"""
        if thread_id in self.conversation_history:
            del self.conversation_history[thread_id]
            return True
        return False
    
    def get_stats(self, thread_id: str) -> Dict[str, int]:
        """获取对话统计"""
        history = self.conversation_history.get(thread_id, [])
        message_count = len(history) // 2
        return {
            "messages": message_count,
            "queries": message_count,
            "searches": 0
        }


# 全局服务实例
_agent_service: Optional[CampusAgentService] = None


def get_agent_service() -> CampusAgentService:
    """获取或创建 Agent 服务实例（单例模式）"""
    global _agent_service
    if _agent_service is None:
        _agent_service = CampusAgentService()
    return _agent_service


# 快捷响应数据库（用于快速回答常见问题）
QUICK_RESPONSES = {
    "报到": {
        "title": "🎒 新生报到指南",
        "content": """**欢迎来到校园！** 🎉

**📋 必备材料清单：**
1. ✅ 录取通知书原件
2. ✅ 身份证及复印件（2份）
3. ✅ 高考准考证
4. ✅ 一寸免冠照片（蓝底/白底各8张）
5. ✅ 党团组织关系转移证明
6. ✅ 户口迁移证（如需迁户口）
7. ✅ 档案袋（密封完好）

**⏰ 重要时间节点：**
- 报到时间：9月1日 - 9月3日（8:00-18:00）
- 军训开始：9月5日
- 正式上课：9月18日

**📍 报到地点：**
学生活动中心一楼大厅"""
    },
    "宿舍": {
        "title": "🏠 宿舍生活指南",
        "content": """**你的温馨小家！** 🏡

**🚪 门禁与作息：**
- 开门时间：6:00 AM
- 门禁时间：23:00 PM（周日至周四）
- 周末门禁：24:00 PM（周五、周六）

**⚡ 用电安全：**
**允许使用：** 手机充电器、笔记本电脑、台灯、小风扇
**禁止使用：** 电热毯、电磁炉、电饭煲（>1200W）
- 每月免费用电额度：20度/人
- 超额电费：0.6元/度

**📞 紧急联系：**
- 宿管阿姨：内线 8888
- 物业维修：内线 6666"""
    },
    "选课": {
        "title": "📚 选课完全攻略",
        "content": """**大学选课秘籍！** 📖

**🎯 选课系统入口：**
教务处网站 → 学生服务 → 网上选课

**⏰ 选课时间表：**
- **第一轮**（正选）：开学第2周
- **第二轮**（补选）：开学第3周
- **第三轮**（退补选）：开学第4周

**📊 学分要求：**
- 每学期建议选课：20-26学分
- 四年总学分要求：160-180学分

**⭐ 抢课技巧：**
1. 提前研究课程评价（问问学长学姐）
2. 准备好备用方案（Plan B、C、D）
3. 使用Chrome浏览器，提前登录
4. 选课前5分钟开始刷新页面"""
    },
    "缴费": {
        "title": "💳 缴费大厅",
        "content": """**费用一览表** 💰

**📋 学费标准（每学年）：**
- 文科类专业：4,800元
- 理工类专业：5,500元
- 艺术类专业：8,000元

**🏠 住宿费用：**
- 4人间：1,200元/年
- 6人间：1,000元/年

**💳 缴费方式：**
1. **网上缴费**（推荐）：官网 → 财务平台，支持支付宝/微信
2. **银行转账**：户名：XX大学，备注：学号+姓名
3. **现场缴费**：行政楼财务处，工作日 9:00-16:30

**⏰ 缴费截止日期：9月15日**"""
    },
    "导航": {
        "title": "🗺️ 校园导航",
        "content": """**校园地图攻略！** 🗺️

**🏛️ 主要建筑位置：**

**教学区（中区）：**
- 📍 第一教学楼：南门正对面
- 📍 第二教学楼：图书馆西侧
- 📍 图书馆：校园中心地标

**生活区（东区）：**
- 📍 学生宿舍1-8号楼
- 📍 第一食堂（东区食堂）
- 📍 学生超市、快递站

**运动区（西区）：**
- 📍 田径运动场（标准400米）
- 📍 体育馆（篮球、羽毛球、乒乓球）
- 📍 第二食堂（西区食堂）

**🚌 校内交通：**
- 校园巴士：1元/次，环线运行
- 共享自行车：支付宝扫码"""
    },
    "食堂": {
        "title": "🍜 美食地图",
        "content": """**吃货的福音！** 🍔

**🍚 东区食堂（第一食堂）：**
**一层（大众餐）：**
- 💰 价格：8-15元
- 🍱 推荐：红烧肉、糖醋排骨、麻辣香锅
- ⏰ 时间：6:30-8:30, 11:00-13:00, 17:00-19:00

**二层（特色餐）：**
- 🍜 兰州拉面：12元，正宗！
- 🍕 西式简餐：披萨、意面
- 🍣 日韩料理：石锅拌饭、寿司
- ⏰ 时间：10:00-21:00

**🌙 夜宵攻略：**
- 地点：东区食堂后门小吃街
- 时间：21:00-24:00
- 推荐：烤冷面、章鱼小丸子、炸串、奶茶"""
    }
}


def get_quick_response(topic: str) -> Optional[Dict[str, str]]:
    """获取快捷响应"""
    return QUICK_RESPONSES.get(topic)


if __name__ == "__main__":
    # 测试
    print("🧪 测试 CampusAgentService")
    
    import asyncio
    
    async def test():
        service = get_agent_service()
        
        # 测试 1: 普通查询
        result = await service.chat("user_001", "图书馆现在开放吗？", "thread_001")
        print(f"\n测试 1 - 图书馆查询:")
        print(f"回复: {result['response'][:100]}...")
        
        # 测试 2: 继续对话
        result = await service.chat("user_001", "那座位多吗？", "thread_001")
        print(f"\n测试 2 - 追问:")
        print(f"回复: {result['response'][:100]}...")
        
        # 测试统计
        stats = service.get_stats("thread_001")
        print(f"\n对话统计: {stats}")
    
    asyncio.run(test())
