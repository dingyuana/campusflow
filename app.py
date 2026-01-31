"""
Day 9: Gradio 前端应用（简化版）
使用 Gradio 构建流式对话界面
"""

import gradio as gr
from typing import List, Tuple
import os


class CampusAssistant:
    """校园助手类（简化版）"""

    def __init__(self):
        """
        初始化校园助手
        """
        self.messages = []
        self.message_count = 0
        self.query_count = 0
        self.search_count = 0

    def process_message(
        self,
        message: str,
        history: List[Tuple[str, str]]
    ) -> Tuple[str, List[Tuple[str, str]]]:
        """
        处理用户消息（简化版）

        Args:
            message: 用户消息
            history: 对话历史

        Returns:
            (回答, 更新后的历史）
        """
        print(f"\n📝 用户消息: {message}")
        print("-" * 60)

        self.message_count += 1
        self.query_count += 1

        # 简单的响应生成（演示用）
        response = self.generate_response(message)

        # 更新对话历史
        history = history + [(message, response)]

        print(f"✅ 处理完成")
        print(f"   回答: {response[:100]}...")

        return response, history

    def generate_response(self, message: str) -> str:
        """
        生成响应（简化版，用于演示）

        Args:
            message: 用户消息

        Returns:
            响应文本
        """
        # 简单的关键词匹配响应
        message_lower = message.lower()

        if "报到" in message:
            return "关于报到：\n\n✅ 新生报到需要准备以下材料：\n1. 录取通知书\n2. 身份证及复印件\n3. 高考准考证\n4. 近期一寸免冠照片（10张）\n5. 党团组织关系证明\n6. 档案转移凭证\n\n报到时间：9月1日-9月3日\n报到地点：学生服务中心"
        elif "宿舍" in message:
            return "关于宿舍：\n\n✅ 宿舍管理规定：\n1. 每天门禁时间：23:00\n2. 不得使用大功率电器\n3. 每周会进行卫生检查\n4. 外出需向宿管登记\n\n如有紧急情况，请联系宿管阿姨或拨打 110。"
        elif "选课" in message:
            return "关于选课：\n\n✅ 选课流程：\n1. 登录教务系统\n2. 进入选课模块\n3. 查看可选课程列表\n4. 选择心仪课程\n5. 提交选课申请\n\n注意：选课时间为每学期开始前两周，请及时关注教务通知。"
        elif "缴费" in message:
            return "关于缴费：\n\n✅ 缴费项目：\n1. 学费：5000元/年\n2. 住宿费：1200元/年\n3. 教材费：500元/年\n\n缴费方式：\n- 支付宝/微信支付\n- 银行转账\n- 现场缴费\n\n缴费截止时间：9月15日"
        elif "导航" in message:
            return "关于校园导航：\n\n✅ 主要建筑位置：\n1. 教学楼：位于校园中心\n2. 图书馆：北门入口处\n3. 学生宿舍：东校区\n4. 食堂：西区和东区各一个\n\n如需详细路线，请告诉我您的出发地和目的地。"
        elif "同学" in message or "老师" in message:
            return "关于人际关系查询：\n\n⚠️  此功能需要连接知识图谱数据库。\n\n当前版本为简化演示版，如需查询具体的同学、师生关系，请确保：\n1. Neo4j 数据库已启动\n2. 知识图谱数据已导入\n3. 相关查询模块已启用"
        elif "新闻" in message or "最新" in message or "政策" in message:
            self.search_count += 1
            return "关于最新信息：\n\n⚠️  此功能需要网络搜索能力。\n\n当前版本为简化演示版，如需查询最新新闻或政策，请确保：\n1. 网络连接正常\n2. 搜索服务已配置\n3. API 密钥已设置"
        else:
            return "你好！我是智慧校园助手，可以帮你查询以下信息：\n\n📋 报到流程\n🏠 宿舍规定\n📚 选课指南\n💰 缴费信息\n🗺️  校园导航\n\n请告诉我你想了解什么？"

    def get_stats(self) -> str:
        """
        获取使用统计

        Returns:
            统计信息文本
        """
        return f"消息数量: {self.message_count}\n查询次数: {self.query_count}\n搜索次数: {self.search_count}"

    def clear_history(self) -> Tuple[List[Tuple[str, str]], str]:
        """
        清空对话历史

        Returns:
            (空历史, 统计信息)
        """
        self.messages = []
        self.message_count = 0
        self.query_count = 0
        self.search_count = 0
        return [], self.get_stats()


# 创建助手实例
assistant = CampusAssistant()


# Gradio 界面定义
with gr.Blocks(title="🎓 智慧校园助手") as demo:
    gr.Markdown(
        """
        ## 欢迎使用智慧校园助手

        我是一个基于 LangGraph 的多智能体校园助手，可以帮您：
        - 📚 查询校园知识（报到、选课、宿舍等）
        - 🕸️  查询复杂关系（同学、教师等）
        - 🌐 搜索最新信息（政策、新闻等）
        - 💾 记住我们的对话历史
        """
    )

    with gr.Row():
        with gr.Column(scale=3):
            # 对话历史
            chatbot = gr.Chatbot(
                label="对话历史",
                height=500,
                show_label=False
            )

        with gr.Column(scale=1):
            # 控制面板
            gr.Markdown("### 🎛️  快捷操作")

            with gr.Accordion("常用查询", open=True):
                btn_enrollment = gr.Button("📋 报到流程")
                btn_course = gr.Button("📚 选课指南")
                btn_dormitory = gr.Button("🏠 宿舍规定")
                btn_search = gr.Button("🔍 实时搜索")

            gr.Markdown("### ⚙️  设置")
            btn_clear = gr.Button("🗑️ 清空历史")

            gr.Markdown("### 📊 统计")
            stats = gr.Textbox(
                label="使用统计",
                value=assistant.get_stats(),
                interactive=False,
                lines=3
            )

    # 输入区域
    with gr.Row():
        user_input = gr.Textbox(
            label="输入您的问题",
            placeholder="例如：新生报到需要准备什么材料？",
            scale=9
        )
        submit_btn = gr.Button("发送", variant="primary", scale=1)

    gr.Markdown("### 💡 示例问题")
    example_questions = gr.Examples(
        examples=[
            ["新生报到需要准备什么材料？"],
            ["宿舍有哪些管理规定？"],
            ["如何进行选课？"],
            ["缴费项目和截止时间？"],
            ["校园主要建筑在哪里？"],
            ["我的同学有哪些？"]
        ],
        inputs=user_input,
        label="点击示例快速输入"
    )

    # 回调函数
    def handle_message(message, history):
        """处理用户消息"""
        response, updated_history = assistant.process_message(message, history)
        return updated_history, "", assistant.get_stats()

    def handle_example(example):
        """处理示例问题"""
        return example, []

    def handle_clear():
        """清空历史"""
        return [], "", assistant.get_stats()

    def handle_enrollment():
        """处理报到查询"""
        return "新生报到需要准备什么材料？", []

    def handle_course():
        """处理选课查询"""
        return "如何进行选课？", []

    def handle_dormitory():
        """处理宿舍查询"""
        return "宿舍有哪些管理规定？", []

    def handle_search():
        """处理搜索请求"""
        return "今天校园有什么新闻？", []

    # 绑定事件
    submit_btn.click(
        handle_message,
        inputs=[user_input, chatbot],
        outputs=[chatbot, user_input, stats]
    )

    user_input.submit(
        handle_message,
        inputs=[user_input, chatbot],
        outputs=[chatbot, user_input, stats]
    )

    btn_clear.click(
        handle_clear,
        outputs=[chatbot, user_input, stats]
    )

    btn_enrollment.click(
        handle_enrollment,
        outputs=[user_input, chatbot]
    )

    btn_course.click(
        handle_course,
        outputs=[user_input, chatbot]
    )

    btn_dormitory.click(
        handle_dormitory,
        outputs=[user_input, chatbot]
    )

    btn_search.click(
        handle_search,
        outputs=[user_input, chatbot]
    )


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 启动智慧校园助手（Gradio 简化版）")
    print("=" * 60)
    print("\n✅ 前端功能：")
    print("   - 流式对话界面")
    print("   - 对话历史记录")
    print("   - 快捷操作按钮")
    print("   - 使用统计")
    print("\n⚠️  注意：此版本为简化演示版，不包含以下功能：")
    print("   - RAG 向量检索")
    print("   - 知识图谱查询")
    print("   - 网络搜索")
    print("   - LangGraph 智能体")
    print("\n📝 后续改进：")
    print("   - 集成真实的 RAG 功能")
    print("   - 连接 Neo4j 知识图谱")
    print("   - 添加网络搜索能力")
    print("   - 实现完整的 LangGraph 工作流")
    print("=" * 60)
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        theme=gr.themes.Soft()
    )
