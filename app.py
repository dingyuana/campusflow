"""
CampusFlow 智慧校园助手 - 青春版
使用 Gradio 构建充满活力的校园对话界面

设计特点：
- 青春活力的配色方案 (靛蓝+活力橙)
- 圆润友好的字体 (Fredoka + Nunito)
- 卡片式模块化布局
- 响应式设计支持
"""

import gradio as gr
from typing import List, Tuple, Dict
import os
import random


class CampusAssistant:
    """校园助手类 - 青春版"""

    def __init__(self):
        """初始化校园助手"""
        self.messages: List[Dict] = []
        self.stats = {
            "messages": 0,
            "queries": 0,
            "searches": 0,
            "start_time": None
        }
        self.quick_responses = {
            "报到": {
                "icon": "🎒",
                "title": "新生报到指南",
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
学生活动中心一楼大厅

**💡 温馨提示：**
- 建议提前1天到达，避免报到高峰
- 可提前在线预缴学费，减少排队时间
- 报到当天有志愿者引导，不用担心迷路~"""
            },
            "宿舍": {
                "icon": "🏠",
                "title": "宿舍生活指南",
                "content": """**你的温馨小家！** 🏡

**🚪 门禁与作息：**
- 开门时间：6:00 AM
- 门禁时间：23:00 PM（周日至周四）
- 周末门禁：24:00 PM（周五、周六）
- 夜不归宿需提前向辅导员申请

**⚡ 用电安全：**
**允许使用：** 手机充电器、笔记本电脑、台灯、小风扇
**禁止使用：** 电热毯、电磁炉、电饭煲、大功率吹风机（>1200W）
- 每月免费用电额度：20度/人
- 超额电费：0.6元/度

**🧹 卫生检查：**
- 检查时间：每周三下午
- 评分标准：床铺整洁、桌面有序、地面干净、无异味
- 优秀宿舍奖励：流动红旗 +  bonus学分

**📞 紧急联系：**
- 宿管阿姨：内线 8888
- 物业维修：内线 6666
- 校园110：内线 5110

**💡 新生建议：**
- 和室友一起制定宿舍公约
- 准备好耳塞和眼罩（集体生活必备）
- 购买一把好锁保护贵重物品"""
            },
            "选课": {
                "icon": "📚",
                "title": "选课完全攻略",
                "content": """**大学选课秘籍！** 📖

**🎯 选课系统入口：**
教务处网站 → 学生服务 → 网上选课
或直接使用教务APP

**⏰ 选课时间表：**
- **第一轮**（正选）：开学第2周
  - 热门课程先到先得！
  - 建议提前收藏心仪课程
  
- **第二轮**（补选）：开学第3周
  - 针对第一轮未选满的课程
  
- **第三轮**（退补选）：开学第4周
  - 可退选不合适的课程

**📊 学分要求：**
- 每学期建议选课：20-26学分
- 四年总学分要求：160-180学分
- 必修课：必须修读
- 选修课：按兴趣选择（注意类别要求）

**⭐ 抢课技巧：**
1. 提前研究课程评价（问问学长学姐）
2. 准备好备用方案（Plan B、C、D）
3. 使用Chrome浏览器，提前登录
4. 选课前5分钟开始刷新页面
5. 网速很重要！建议去图书馆或机房

**⚠️ 注意事项：**
- 注意课程时间冲突
- 平衡课程难度，不要一学期全是"硬课"
- 体育课、实验课通常名额紧张

需要推荐具体课程吗？告诉我你的专业！"""
            },
            "缴费": {
                "icon": "💳",
                "title": "缴费大厅",
                "content": """**费用一览表** 💰

**📋 学费标准（每学年）：**
- 文科类专业：4,800元
- 理工类专业：5,500元
- 艺术类专业：8,000元
- 软件工程专业：12,000元

**🏠 住宿费用：**
- 4人间：1,200元/年
- 6人间：1,000元/年
- 空调使用费：200元/年（另计）

**📚 其他费用：**
- 教材费：约500-800元（按实际领书结算）
- 体检费：80元
- 军训服装：120元
- 大学生医保：280元/年
- 校园一卡通：工本费20元（首次免费）

**💳 缴费方式：**
1. **网上缴费**（推荐）：
   - 学校官网 → 财务平台
   - 支持支付宝、微信、银联
   - 24小时服务，方便快捷

2. **银行转账：**
   - 户名：XX大学
   - 开户行：工商银行XX支行
   - 账号：XXXX XXXX XXXX XXXX
   - **⚠️ 备注必须写：姓名+学号**

3. **现场缴费：**
   - 地点：行政楼财务处
   - 时间：工作日 9:00-11:30, 14:00-16:30
   - 支持现金、刷卡

**⏰ 缴费截止日期：**
- 秋季学期：9月15日
- 春季学期：3月1日
- **逾期未缴将产生滞纳金（0.05%/天）**

**🎁 绿色通道：**
家庭经济困难学生可申请：
- 学费缓交
- 助学贷款
- 勤工助学岗位
请联系学生资助中心：电话 XXXX-XXXXXXX"""
            },
            "导航": {
                "icon": "🗺️",
                "title": "校园导航",
                "content": """**校园地图攻略！** 🗺️

**🏛️ 主要建筑位置：**

**教学区（中区）：**
- 📍 第一教学楼：南门正对面
- 📍 第二教学楼：图书馆西侧
- 📍 实验楼：一教北侧
- 📍 图书馆：校园中心地标

**生活区（东区）：**
- 📍 学生宿舍1-8号楼
- 📍 第一食堂（东区食堂）
- 📍 学生超市、快递站
- 📍 校医院（东一门旁）

**运动区（西区）：**
- 📍 田径运动场（标准400米）
- 📍 体育馆（篮球、羽毛球、乒乓球）
- 📍 游泳馆（需预约）
- 📍 第二食堂（西区食堂）

**🏃 常用路线：**
**宿舍 → 教学楼：**步行约8-12分钟
**宿舍 → 食堂：**步行约3-5分钟  
**东门 → 图书馆：**步行约15分钟

**🚌 校内交通：**
- 校园巴士：1元/次，环线运行
- 共享自行车：支付宝扫码
- 共享电动车：需戴头盔

**🚗 校外交通：**
- 南门：地铁2号线XX站（步行5分钟）
- 东门：公交XX路、XX路
- 西门：主要货运通道

**📱 实用工具：**
- 下载"校园地图"APP，支持AR导航
- 关注学校公众号，发送"地图"获取高清版

想去哪里？我可以给你详细路线！"""
            },
            "食堂": {
                "icon": "🍜",
                "title": "美食地图",
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

**三层（教职工餐厅）：**
- 学生也可以去，菜品更精致
- 支持小炒点餐

**🍲 西区食堂（第二食堂）：**
- 🥟 北方风味：饺子、包子、面食
- 🌶️ 川湘菜：麻辣鲜香
- 🥗 轻食区：沙拉、低卡餐（健身党福利）
- ☕ 咖啡厅：24小时营业！

**🌙 夜宵攻略：**
- 地点：东区食堂后门小吃街
- 时间：21:00-24:00
- 推荐：烤冷面、章鱼小丸子、炸串、奶茶

**💳 支付方式：**
- 校园一卡通（推荐，享9.5折）
- 支付宝/微信
- 部分窗口支持人脸支付

**💡 就餐Tips：**
- 避开高峰：11:45-12:15, 17:30-18:00
- 周一、周五人最多
- 期末周夜宵会延长到1:00
- 食堂阿姨手不抖，放心点肉菜！

**🏪 其他觅食地点：**
- 教超（教学楼B1层）：便当、三明治
- 瑞幸咖啡：三教、图书馆各一家
- 奶茶店：书亦、蜜雪冰城、茶百道

想吃啥？我可以推荐具体档口！"""
            }
        }

    def process_message(
        self,
        message: str,
        history: List[Tuple[str, str]]
    ) -> Tuple[str, List[Tuple[str, str]], str]:
        """
        处理用户消息
        
        Returns:
            (response, updated_history, stats_text)
        """
        self.stats["messages"] += 1
        self.stats["queries"] += 1

        # 检查是否是快捷查询
        response = self.check_quick_queries(message)
        
        if not response:
            # 智能匹配关键词
            response = self.generate_smart_response(message)

        # 更新历史
        history = history + [(message, response)]
        
        return response, history, self.get_stats_text()

    def check_quick_queries(self, message: str) -> str:
        """检查是否匹配快捷查询"""
        msg_lower = message.lower()
        
        for key, data in self.quick_responses.items():
            if key in msg_lower or data["title"] in msg_lower:
                return f"{data['icon']} **{data['title']}**\n\n{data['content']}"
        
        return ""

    def generate_smart_response(self, message: str) -> str:
        """生成智能回复"""
        msg_lower = message.lower()
        
        greetings = ["你好", "您好", "hi", "hello", "在吗"]
        if any(g in msg_lower for g in greetings):
            return self.get_welcome_message()
        
        thanks = ["谢谢", "感谢", "thank"]
        if any(t in msg_lower for t in thanks):
            return "😊 不客气！有问题随时找我，祝你大学生活愉快！"
        
        bye = ["再见", "拜拜", "bye", "goodbye"]
        if any(b in msg_lower for b in bye):
            return "👋 再见！有问题随时回来找我哦~ 祝你今天开心！"
        
        # 默认回复
        return f"{self.get_welcome_message()}\n\n🤔 我好像没完全理解你的问题...\n\n试试点击右侧的快捷入口，或者问得更具体一点？比如：\n• 图书馆怎么借书？\n• 校医院几点开门？\n• 哪里有打印店？"

    def get_welcome_message(self) -> str:
        """获取欢迎消息"""
        hour = random.randint(8, 22)  # 模拟时间
        greetings = {
            "morning": "☀️ 早上好！新的一天开始了",
            "afternoon": "🌤️ 下午好！学习累了记得休息",
            "evening": "🌙 晚上好！今天过得怎么样"
        }
        
        if hour < 12:
            greeting = greetings["morning"]
        elif hour < 18:
            greeting = greetings["afternoon"]
        else:
            greeting = greetings["evening"]
        
        return f"{greeting}！我是 **CampusFlow** 智慧校园助手 🎓\n\n我可以帮你：\n• 📋 查询报到流程\n• 🏠 了解宿舍规定\n• 📚 解答选课问题\n• 💰 查询缴费信息\n• 🗺️ 提供校园导航\n• 🍜 推荐美食攻略\n\n有什么我可以帮你的吗？"

    def get_stats_text(self) -> str:
        """获取统计信息文本"""
        return f"💬 对话 {self.stats['messages']} 次 | 🔍 查询 {self.stats['queries']} 次"

    def clear_history(self) -> Tuple[List, str, str]:
        """清空历史"""
        self.stats = {"messages": 0, "queries": 0, "searches": 0, "start_time": None}
        return [], "", self.get_stats_text()

    def handle_quick_button(self, topic: str) -> Tuple[str, List]:
        """处理快捷按钮点击"""
        if topic in self.quick_responses:
            data = self.quick_responses[topic]
            return f"{data['icon']} **{data['title']}**\n\n{data['content']}", []
        return "", []


# 创建助手实例
assistant = CampusAssistant()

# 自定义 CSS - 青春活力风格
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@300;400;500;600;700&display=swap');

/* 全局字体 */
* {
    font-family: 'Nunito', 'Fredoka', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* 页面背景 */
body {
    background: linear-gradient(135deg, #EEF2FF 0%, #F5F3FF 100%) !important;
}

/* 主容器 */
.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto !important;
    padding: 20px !important;
}

/* 标题样式 */
.main-title {
    font-family: 'Fredoka', sans-serif !important;
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #4F46E5 0%, #F97316 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    text-align: center !important;
    margin-bottom: 0.5rem !important;
}

.subtitle {
    font-size: 1.1rem !important;
    color: #64748B !important;
    text-align: center !important;
    margin-bottom: 2rem !important;
}

/* 聊天区域样式 */
.chatbot-container {
    background: white !important;
    border-radius: 20px !important;
    box-shadow: 0 10px 40px -10px rgba(79, 70, 229, 0.15) !important;
    border: 2px solid #E0E7FF !important;
    overflow: hidden !important;
}

/* 用户消息 */
.user-message {
    background: linear-gradient(135deg, #4F46E5 0%, #6366F1 50%, #818CF8 100%) !important;
    color: white !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 12px 16px !important;
    margin: 8px 0 !important;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
    font-weight: 500 !important;
}

/* 助手消息 */
.bot-message {
    background: white !important;
    color: #1E1B4B !important;
    border-radius: 18px !important;
    padding: 12px 16px !important;
    margin: 8px 0 !important;
    border: 2px solid #E0E7FF !important;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.08) !important;
}

/* 快捷入口卡片 */
.quick-card {
    background: white !important;
    border-radius: 16px !important;
    padding: 20px !important;
    border: 2px solid #E0E7FF !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
    text-align: center !important;
}

.quick-card:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 24px rgba(79, 70, 229, 0.15) !important;
    border-color: #4F46E5 !important;
}

.quick-icon {
    font-size: 2rem !important;
    margin-bottom: 8px !important;
    display: block !important;
}

.quick-title {
    font-weight: 600 !important;
    color: #1E1B4B !important;
    font-size: 0.9rem !important;
}

/* 按钮样式 */
.send-btn {
    background: linear-gradient(135deg, #4F46E5 0%, #F97316 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4) !important;
}

.send-btn:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5) !important;
}

/* 输入框样式 */
.input-box {
    border: 2px solid #E0E7FF !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
    background: white !important;
}

.input-box:focus {
    border-color: #4F46E5 !important;
    box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1) !important;
    outline: none !important;
}

/* 统计面板 */
.stats-panel {
    background: linear-gradient(135deg, #F97316 0%, #FB923C 100%) !important;
    color: white !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    font-weight: 600 !important;
    text-align: center !important;
    box-shadow: 0 4px 14px rgba(249, 115, 22, 0.3) !important;
}

/* 清空按钮 */
.clear-btn {
    background: white !important;
    color: #64748B !important;
    border: 2px solid #E2E8F0 !important;
    border-radius: 10px !important;
    padding: 8px 16px !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
}

.clear-btn:hover {
    background: #FEE2E2 !important;
    color: #EF4444 !important;
    border-color: #FCA5A5 !important;
}

/* 示例问题标签 */
.example-tag {
    background: #EEF2FF !important;
    color: #4F46E5 !important;
    border: 2px dashed #C7D2FE !important;
    border-radius: 20px !important;
    padding: 8px 16px !important;
    margin: 4px !important;
    font-size: 0.85rem !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    display: inline-block !important;
}

.example-tag:hover {
    background: #4F46E5 !important;
    color: white !important;
    border-style: solid !important;
    transform: scale(1.05) !important;
}

/* 右侧面板 */
.side-panel {
    background: white !important;
    border-radius: 20px !important;
    padding: 24px !important;
    border: 2px solid #E0E7FF !important;
    box-shadow: 0 10px 40px -10px rgba(79, 70, 229, 0.1) !important;
}

/* 滚动条样式 */
::-webkit-scrollbar {
    width: 8px !important;
}

::-webkit-scrollbar-track {
    background: #F1F5F9 !important;
    border-radius: 4px !important;
}

::-webkit-scrollbar-thumb {
    background: #C7D2FE !important;
    border-radius: 4px !important;
}

::-webkit-scrollbar-thumb:hover {
    background: #818CF8 !important;
}

/* 响应式调整 */
@media (max-width: 768px) {
    .main-title {
        font-size: 1.8rem !important;
    }
    
    .gradio-container {
        padding: 12px !important;
    }
    
    .quick-card {
        padding: 16px !important;
    }
}
"""

# 构建 Gradio 界面
with gr.Blocks(
    title="🎓 CampusFlow - 智慧校园助手"
) as demo:
    
    # 头部区域
    gr.HTML("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 class="main-title">🎓 CampusFlow</h1>
        <p class="subtitle">你的智慧校园伙伴，让大学生活更轻松</p>
    </div>
    """)
    
    with gr.Row(equal_height=False):
        # 左侧：对话区域
        with gr.Column(scale=3, min_width=400):
            with gr.Group(elem_classes=["chatbot-container"]):
                chatbot = gr.Chatbot(
                    label="对话",
                    height=550,
                    elem_classes=["chatbot"]
                )
                
                # 输入区域
                with gr.Row():
                    user_input = gr.Textbox(
                        label="",
                        placeholder="💬 输入你想了解的问题，比如：新生报到要带什么？",
                        scale=9,
                        elem_classes=["input-box"]
                    )
                    submit_btn = gr.Button(
                        "🚀 发送",
                        scale=1,
                        elem_classes=["send-btn"]
                    )
                
                # 示例问题
                with gr.Row():
                    gr.HTML("<p style='color: #64748B; font-size: 0.9rem; margin: 10px 0;'>💡 试试问这些：</p>")
                
                with gr.Row():
                    example_1 = gr.Button("🎒 新生报到攻略", variant="secondary", size="sm")
                    example_2 = gr.Button("🏠 宿舍生活指南", variant="secondary", size="sm")
                    example_3 = gr.Button("📚 选课完全攻略", variant="secondary", size="sm")
                    example_4 = gr.Button("🍜 食堂美食地图", variant="secondary", size="sm")
        
        # 右侧：快捷入口 + 统计
        with gr.Column(scale=1, min_width=250):
            with gr.Group(elem_classes=["side-panel"]):
                gr.Markdown("### 🎛️ 快捷入口")
                
                # 快捷按钮网格
                with gr.Row():
                    btn_enrollment = gr.Button("🎒\n报到指南", variant="secondary")
                    btn_dormitory = gr.Button("🏠\n宿舍生活", variant="secondary")
                
                with gr.Row():
                    btn_course = gr.Button("📚\n选课助手", variant="secondary")
                    btn_payment = gr.Button("💳\n缴费大厅", variant="secondary")
                
                with gr.Row():
                    btn_nav = gr.Button("🗺️\n校园导航", variant="secondary")
                    btn_food = gr.Button("🍜\n美食攻略", variant="secondary")
                
                gr.Markdown("---")
                
                # 统计面板
                stats_text = gr.Textbox(
                    label="📊 今日互动",
                    value=assistant.get_stats_text(),
                    interactive=False,
                    elem_classes=["stats-panel"],
                    lines=2
                )
                
                gr.Markdown("---")
                
                # 清空按钮
                btn_clear = gr.Button("🗑️ 清空对话", variant="secondary", elem_classes=["clear-btn"])
                
                gr.Markdown("""
                <div style="margin-top: 20px; padding: 16px; background: #F8FAFC; border-radius: 12px; border: 2px dashed #CBD5E1;">
                    <p style="margin: 0; color: #64748B; font-size: 0.85rem; text-align: center;">
                        💡 提示：点击快捷入口<br>可快速获取相关信息
                    </p>
                </div>
                """)
    
    # 事件绑定
    def handle_message(message, history):
        """处理用户消息"""
        if not message.strip():
            return history, "", assistant.get_stats_text()
        response, updated_history, stats = assistant.process_message(message, history)
        return updated_history, "", stats
    
    def handle_example(example_text):
        """处理示例问题"""
        return example_text
    
    def handle_quick_button(topic):
        """处理快捷按钮"""
        response, _ = assistant.handle_quick_button(topic)
        return response, [(f"查看{topic}信息", response)]
    
    def handle_clear():
        """清空历史"""
        empty_list, _, stats = assistant.clear_history()
        return empty_list, "", stats
    
    # 绑定提交事件
    submit_btn.click(
        handle_message,
        inputs=[user_input, chatbot],
        outputs=[chatbot, user_input, stats_text]
    )
    
    user_input.submit(
        handle_message,
        inputs=[user_input, chatbot],
        outputs=[chatbot, user_input, stats_text]
    )
    
    # 绑定示例按钮
    example_1.click(lambda: "🎒 新生报到攻略", outputs=user_input)
    example_2.click(lambda: "🏠 宿舍生活指南", outputs=user_input)
    example_3.click(lambda: "📚 选课完全攻略", outputs=user_input)
    example_4.click(lambda: "🍜 食堂美食地图", outputs=user_input)
    
    # 绑定快捷按钮
    btn_enrollment.click(
        lambda: handle_quick_button("报到"),
        outputs=[user_input, chatbot]
    )
    
    btn_dormitory.click(
        lambda: handle_quick_button("宿舍"),
        outputs=[user_input, chatbot]
    )
    
    btn_course.click(
        lambda: handle_quick_button("选课"),
        outputs=[user_input, chatbot]
    )
    
    btn_payment.click(
        lambda: handle_quick_button("缴费"),
        outputs=[user_input, chatbot]
    )
    
    btn_nav.click(
        lambda: handle_quick_button("导航"),
        outputs=[user_input, chatbot]
    )
    
    btn_food.click(
        lambda: handle_quick_button("食堂"),
        outputs=[user_input, chatbot]
    )
    
    # 绑定清空按钮
    btn_clear.click(
        handle_clear,
        outputs=[chatbot, user_input, stats_text]
    )

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 CampusFlow 智慧校园助手 - 青春版")
    print("=" * 70)
    print("\n✨ 设计特点：")
    print("   🎨 青春活力配色（靛蓝 + 活力橙）")
    print("   ✍️  圆润友好字体（Fredoka + Nunito）")
    print("   📱 响应式布局（桌面 + 平板 + 手机）")
    print("   🎯 模块化快捷入口")
    print("   💫 流畅微交互")
    print("\n📦 包含内容：")
    print("   • 6 大快捷查询模块")
    print("   • 详细的新生指南")
    print("   • 实时对话统计")
    print("   • 4 个示例问题")
    print("\n🌐 访问地址：")
    print("   http://0.0.0.0:7860")
    print("=" * 70)
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        css=custom_css,
        theme=gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="orange",
            neutral_hue="slate"
        )
    )
