"""
CampusFlow 完整版前端
调用后端 API 的真实对话系统
"""

import gradio as gr
import requests
import os
from typing import List, Tuple, Dict

# API 配置
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


class CampusFlowClient:
    """CampusFlow API 客户端"""
    
    def __init__(self, api_url: str = API_BASE_URL):
        self.api_url = api_url
        self.user_id = "student_001"
        self.thread_id = None
        
    def chat(self, message: str) -> Tuple[str, str]:
        """
        发送消息到后端 API
        
        Returns:
            (response_text, error_message)
        """
        try:
            url = f"{self.api_url}/agent/chat"
            payload = {
                "user_id": self.user_id,
                "message": message,
                "thread_id": self.thread_id
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("success"):
                # 保存 thread_id 用于后续对话
                self.thread_id = data.get("thread_id")
                return data.get("response", ""), ""
            else:
                return "", data.get("error", "未知错误")
                
        except requests.exceptions.ConnectionError:
            return "", "❌ 无法连接到后端服务，请确保 API 服务已启动 (python api/main.py)"
        except requests.exceptions.Timeout:
            return "", "⏱️ 请求超时，请稍后再试"
        except Exception as e:
            return "", f"❌ 请求失败: {str(e)}"
    
    def get_quick_info(self, topic: str) -> str:
        """获取快捷信息"""
        try:
            url = f"{self.api_url}/agent/quick/{topic}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return f"{data.get('title')}\n\n{data.get('content')}"
            return ""
        except:
            # 如果 API 不可用，使用本地数据
            return self._get_local_quick_response(topic)
    
    def _get_local_quick_response(self, topic: str) -> str:
        """本地快捷响应（API不可用时使用）"""
        responses = {
            "报到": "🎒 新生报到指南\n\n📋 必备材料：录取通知书、身份证、照片等\n⏰ 时间：9月1-3日\n📍 地点：学生活动中心",
            "宿舍": "🏠 宿舍生活指南\n\n🚪 门禁：23:00（周日-周四）\n⚡ 用电：20度/月免费\n📞 宿管：内线8888",
            "选课": "📚 选课攻略\n\n⏰ 第一轮：开学第2周\n📊 建议：20-26学分/学期\n💡 技巧：提前准备Plan B",
            "缴费": "💳 缴费大厅\n\n💰 学费：文科4800/理工5500/艺术8000\n🏠 住宿：4人间1200/6人间1000\n⏰ 截止：9月15日",
            "导航": "🗺️ 校园导航\n\n🏛️ 一教：南门对面\n📚 图书馆：校园中心\n🏠 宿舍：东区\n🍜 食堂：东西区各一个",
            "食堂": "🍜 美食地图\n\n🍚 东区食堂：8-15元\n🍜 兰州拉面：12元\n🌙 夜宵：21:00-24:00"
        }
        return responses.get(topic, "")
    
    def clear_history(self) -> bool:
        """清空对话历史"""
        if not self.thread_id:
            return True
            
        try:
            url = f"{self.api_url}/agent/clear"
            payload = {"thread_id": self.thread_id}
            response = requests.post(url, json=payload, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """获取对话统计"""
        if not self.thread_id:
            return {"messages": 0, "queries": 0}
            
        try:
            url = f"{self.api_url}/agent/stats/{self.thread_id}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return {"messages": 0, "queries": 0}


# 创建客户端
client = CampusFlowClient()


def process_message(message: str, history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]], str]:
    """处理用户消息"""
    if not message.strip():
        return "", history, "💬 对话 0 次 | 🔍 查询 0 次"
    
    # 发送到后端 API
    response, error = client.chat(message)
    
    if error:
        # 显示错误但保持对话继续
        response_text = f"⚠️ {error}\n\n💡 当前使用离线模式，显示预置回答。\n\n我是 CampusFlow 智慧校园助手，可以帮您：\n• 📋 查询报到流程\n• 🏠 了解宿舍规定\n• 📚 解答选课问题\n• 💰 查询缴费信息"
    else:
        response_text = response
    
    # 更新历史
    history = history + [(message, response_text)]
    
    # 获取统计
    stats = client.get_stats()
    stats_text = f"💬 对话 {stats.get('messages', 0)} 次 | 🔍 查询 {stats.get('queries', 0)} 次"
    
    return "", history, stats_text


def handle_quick_button(topic: str) -> Tuple[str, List[Tuple[str, str]], str]:
    """处理快捷按钮点击"""
    content = client.get_quick_info(topic)
    
    if content:
        # 直接显示快捷信息
        history = [(f"查看{topic}信息", content)]
        stats = client.get_stats()
        stats_text = f"💬 对话 {stats.get('messages', 0)} 次 | 🔍 查询 {stats.get('queries', 0)} 次"
        return "", history, stats_text
    
    return f"请告诉我关于{topic}的具体问题", [], "💬 对话 0 次 | 🔍 查询 0 次"


def clear_conversation() -> Tuple[List, str, str]:
    """清空对话"""
    client.clear_history()
    return [], "", "💬 对话 0 次 | 🔍 查询 0 次"


# 自定义 CSS
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Nunito', 'Fredoka', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

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

.stats-panel {
    background: linear-gradient(135deg, #F97316 0%, #FB923C 100%) !important;
    color: white !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    font-weight: 600 !important;
    text-align: center !important;
    box-shadow: 0 4px 14px rgba(249, 115, 22, 0.3) !important;
}
"""


# 构建 Gradio 界面
with gr.Blocks(
    title="🎓 CampusFlow - 智慧校园助手",
    css=custom_css,
    theme=gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="orange",
        neutral_hue="slate"
    )
) as demo:
    
    # 头部区域
    gr.HTML("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 class="main-title">🎓 CampusFlow</h1>
        <p class="subtitle">你的智慧校园伙伴，让大学生活更轻松</p>
        <p style="color: #94A3B8; font-size: 0.9rem;">版本 2.0 | 完整版（连接后端API）</p>
    </div>
    """)
    
    with gr.Row(equal_height=False):
        # 左侧：对话区域
        with gr.Column(scale=3, min_width=400):
            chatbot = gr.Chatbot(
                label="对话",
                height=550,
                bubble_full_width=False,
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
                    variant="primary"
                )
            
            # 示例问题
            with gr.Row():
                example_1 = gr.Button("🎒 新生报到", variant="secondary", size="sm")
                example_2 = gr.Button("🏠 宿舍生活", variant="secondary", size="sm")
                example_3 = gr.Button("📚 选课攻略", variant="secondary", size="sm")
                example_4 = gr.Button("🍜 食堂美食", variant="secondary", size="sm")
        
        # 右侧：快捷入口 + 统计
        with gr.Column(scale=1, min_width=250):
            with gr.Group():
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
                    value="💬 对话 0 次 | 🔍 查询 0 次",
                    interactive=False,
                    elem_classes=["stats-panel"],
                    lines=2
                )
                
                gr.Markdown("---")
                
                # 清空按钮
                btn_clear = gr.Button("🗑️ 清空对话", variant="secondary")
                
                # API 状态提示
                gr.Markdown("""
                <div style="margin-top: 20px; padding: 12px; background: #F1F5F9; border-radius: 12px; border: 2px dashed #CBD5E1;">
                    <p style="margin: 0; color: #64748B; font-size: 0.8rem; text-align: center;">
                        🔌 API: localhost:8000<br>
                        💡 支持真实Agent对话
                    </p>
                </div>
                """)
    
    # 事件绑定
    submit_btn.click(
        process_message,
        inputs=[user_input, chatbot],
        outputs=[user_input, chatbot, stats_text]
    )
    
    user_input.submit(
        process_message,
        inputs=[user_input, chatbot],
        outputs=[user_input, chatbot, stats_text]
    )
    
    # 示例按钮
    example_1.click(lambda: "🎒 新生报到需要准备什么材料？", outputs=user_input)
    example_2.click(lambda: "🏠 宿舍有哪些管理规定？", outputs=user_input)
    example_3.click(lambda: "📚 如何进行选课？", outputs=user_input)
    example_4.click(lambda: "🍜 食堂有什么好吃的？", outputs=user_input)
    
    # 快捷按钮
    btn_enrollment.click(
        lambda: handle_quick_button("报到"),
        outputs=[user_input, chatbot, stats_text]
    )
    
    btn_dormitory.click(
        lambda: handle_quick_button("宿舍"),
        outputs=[user_input, chatbot, stats_text]
    )
    
    btn_course.click(
        lambda: handle_quick_button("选课"),
        outputs=[user_input, chatbot, stats_text]
    )
    
    btn_payment.click(
        lambda: handle_quick_button("缴费"),
        outputs=[user_input, chatbot, stats_text]
    )
    
    btn_nav.click(
        lambda: handle_quick_button("导航"),
        outputs=[user_input, chatbot, stats_text]
    )
    
    btn_food.click(
        lambda: handle_quick_button("食堂"),
        outputs=[user_input, chatbot, stats_text]
    )
    
    # 清空按钮
    btn_clear.click(
        clear_conversation,
        outputs=[chatbot, user_input, stats_text]
    )


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 CampusFlow 智慧校园助手 - 完整版 (v2.0)")
    print("=" * 70)
    print("\n✨ 特点：")
    print("   🔗 连接后端 API (localhost:8000)")
    print("   🤖 真实 Agent 对话 (ReAct)")
    print("   📚 支持工具调用 (图书馆/缴费/宿舍)")
    print("   🎨 青春活力 UI 设计")
    print("\n⚠️  确保后端服务已启动：")
    print("   python api/main.py")
    print("\n🌐 前端访问地址：")
    print("   http://0.0.0.0:7860")
    print("=" * 70)
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
