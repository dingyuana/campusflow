# Gradio 前端开发指南

## 📋 概述

Gradio 是一个开源的 Python 库，可以快速为机器学习模型、API 或任何 Python 函数创建可共享的用户界面。在 CampusFlow 项目中，Gradio 用于构建智慧校园助手的前端交互界面。

### 为什么选择 Gradio？

| 特性 | 说明 |
|------|------|
| **快速开发** | 几行代码即可创建美观的 Web 界面 |
| **无需前端知识** | 纯 Python 编写，无需 HTML/CSS/JS |
| **实时交互** | 内置流式输出、进度条等交互功能 |
| **自动分享** | 一键生成可分享的链接 |
| **组件丰富** | 30+ 种 UI 组件（文本、图像、音频等） |
| **主题定制** | 支持多种主题和自定义样式 |

---

## 🚀 快速开始

### 1. 安装 Gradio

```bash
# 基础安装
pip install gradio

# 国内镜像加速
pip install gradio --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 第一个 Gradio 应用

```python
import gradio as gr

# 定义处理函数
def greet(name, intensity):
    """问候函数"""
    return "Hello " + name + "!" * int(intensity)

# 创建界面
demo = gr.Interface(
    fn=greet,                    # 处理函数
    inputs=["text", "slider"],   # 输入组件
    outputs="text"               # 输出组件
)

# 启动服务
demo.launch()
```

访问 http://localhost:7860 即可看到界面。

---

## 📦 核心组件

### 1. Interface（简单界面）

适用于单一函数的单页应用。

```python
import gradio as gr

def process(input_text):
    """处理函数"""
    return f"处理结果: {input_text.upper()}"

# 创建简单界面
demo = gr.Interface(
    fn=process,
    inputs=gr.Textbox(label="输入文本", placeholder="请输入..."),
    outputs=gr.Textbox(label="输出结果"),
    title="文本处理器",
    description="输入任意文本，转换为大写",
    examples=["hello", "world", "gradio"],
    theme=gr.themes.Soft()
)

demo.launch()
```

### 2. Blocks（灵活布局）

适用于复杂布局和交互的自定义界面。

```python
import gradio as gr

# 使用 Blocks 创建复杂布局
with gr.Blocks(title="智慧校园助手") as demo:
    # 标题
    gr.Markdown("# 🎓 智慧校园助手")
    gr.Markdown("欢迎使用智能问答系统")
    
    with gr.Row():  # 水平布局
        with gr.Column(scale=3):  # 左侧（占3份）
            # 输入组件
            input_text = gr.Textbox(
                label="您的问题",
                placeholder="请输入您的问题...",
                lines=3
            )
            
            # 按钮
            submit_btn = gr.Button("提交", variant="primary")
            clear_btn = gr.Button("清空")
        
        with gr.Column(scale=1):  # 右侧（占1份）
            # 选项
            gr.Markdown("### 快速选择")
            btn1 = gr.Button("报到流程")
            btn2 = gr.Button("选课指南")
    
    # 输出区域
    output_text = gr.Textbox(label="回答", lines=10)
    
    # 绑定事件
    submit_btn.click(
        fn=lambda x: f"回答: {x}",
        inputs=input_text,
        outputs=output_text
    )
    
    clear_btn.click(
        fn=lambda: "",
        outputs=input_text
    )

demo.launch()
```

---

## 🎨 常用组件详解

### 输入组件

#### Textbox（文本框）

```python
import gradio as gr

# 基础文本框
text_input = gr.Textbox(
    label="输入文本",
    placeholder="请输入...",
    lines=3,                    # 行数（多行文本）
    max_lines=10,               # 最大行数
    value="默认值",             # 默认值
    show_copy_button=True,      # 显示复制按钮
    interactive=True            # 可交互
)

# 密码输入
password_input = gr.Textbox(
    label="密码",
    type="password"             # 密码类型
)
```

#### Dropdown（下拉菜单）

```python
# 单选下拉菜单
dropdown = gr.Dropdown(
    choices=["选项1", "选项2", "选项3"],
    value="选项1",              # 默认值
    label="选择类型",
    interactive=True
)

# 多选下拉菜单
multi_dropdown = gr.Dropdown(
    choices=["RAG", "知识图谱", "搜索"],
    value=["RAG"],
    label="启用功能",
    multiselect=True            # 多选模式
)
```

#### Slider（滑块）

```python
slider = gr.Slider(
    minimum=0,                  # 最小值
    maximum=100,                # 最大值
    value=50,                   # 默认值
    step=1,                     # 步长
    label="温度参数"
)
```

#### Checkbox（复选框）

```python
checkbox = gr.Checkbox(
    value=True,                 # 默认选中
    label="启用流式输出"
)

# 复选框组
checkbox_group = gr.CheckboxGroup(
    choices=["知识库", "图谱", "搜索"],
    value=["知识库"],
    label="数据来源"
)
```

#### Radio（单选按钮）

```python
radio = gr.Radio(
    choices=["GPT-3.5", "GPT-4", "Claude"],
    value="GPT-3.5",
    label="选择模型"
)
```

#### File（文件上传）

```python
file_input = gr.File(
    label="上传文件",
    file_types=[".pdf", ".docx", ".txt"],  # 限制文件类型
    type="filepath"                         # 返回文件路径
)
```

### 输出组件

#### Textbox（文本输出）

```python
text_output = gr.Textbox(
    label="输出结果",
    lines=10,
    interactive=False,          # 只读
    show_copy_button=True
)
```

#### Chatbot（对话机器人）

```python
import gradio as gr

# 创建 Chatbot
chatbot = gr.Chatbot(
    label="对话历史",
    height=500,
    bubble_full_width=False,    # 气泡宽度自适应
    show_copy_button=True,      # 显示复制按钮
    avatar_images=("user.png", "bot.png")  # 自定义头像
)

# 使用示例
with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="输入消息")
    
    def respond(message, chat_history):
        """处理消息"""
        # 模拟回复
        bot_message = f"你说了: {message}"
        
        # 更新对话历史（OpenAI 格式）
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_message})
        
        return chat_history, ""
    
    msg.submit(respond, [msg, chatbot], [chatbot, msg])

demo.launch()
```

#### Markdown（富文本）

```python
gr.Markdown("""
# 标题
## 副标题

- 列表项1
- 列表项2

**粗体文本** 和 *斜体文本*

[链接文本](https://example.com)
""")
```

#### JSON（JSON 展示）

```python
json_output = gr.JSON(
    label="JSON 数据",
    value={"key": "value"}
)
```

#### Dataframe（表格）

```python
import pandas as pd

df = pd.DataFrame({
    "姓名": ["张三", "李四"],
    "年龄": [20, 21],
    "专业": ["CS", "AI"]
})

table = gr.Dataframe(
    value=df,
    label="学生列表",
    interactive=False
)
```

---

## 🎯 布局管理

### 1. 行列布局

```python
import gradio as gr

with gr.Blocks() as demo:
    # 水平布局（Row）
    with gr.Row():
        with gr.Column(scale=1):   # 占1份
            gr.Textbox(label="输入1")
        with gr.Column(scale=2):   # 占2份
            gr.Textbox(label="输入2")
        with gr.Column(scale=1):   # 占1份
            gr.Button("提交")
    
    # 垂直布局（默认）
    with gr.Column():
        gr.Textbox(label="输入3")
        gr.Textbox(label="输入4")
        gr.Button("提交2")
    
    # Tab 布局
    with gr.Tab("Tab 1"):
        gr.Textbox(label="内容1")
    
    with gr.Tab("Tab 2"):
        gr.Textbox(label="内容2")

demo.launch()
```

### 2. 分组和折叠

```python
import gradio as gr

with gr.Blocks() as demo:
    # 分组（带边框）
    with gr.Group():
        gr.Textbox(label="用户名")
        gr.Textbox(label="密码", type="password")
    
    # 可折叠面板
    with gr.Accordion("高级选项", open=False):
        gr.Slider(label="温度", minimum=0, maximum=1, value=0.7)
        gr.Checkbox(label="启用调试模式")

demo.launch()
```

---

## ⚡ 交互与事件

### 1. 事件绑定

```python
import gradio as gr

def process(input1, input2):
    return f"结果: {input1} + {input2}"

def clear():
    return "", "", ""

with gr.Blocks() as demo:
    with gr.Row():
        input1 = gr.Textbox(label="输入1")
        input2 = gr.Textbox(label="输入2")
    
    output = gr.Textbox(label="输出")
    
    submit_btn = gr.Button("提交")
    clear_btn = gr.Button("清空")
    
    # 点击事件
    submit_btn.click(
        fn=process,
        inputs=[input1, input2],
        outputs=output
    )
    
    # 清空事件
    clear_btn.click(
        fn=clear,
        outputs=[input1, input2, output]
    )
    
    # 输入框回车事件
    input1.submit(
        fn=process,
        inputs=[input1, input2],
        outputs=output
    )
    
    # 输入变化事件（实时响应）
    input1.change(
        fn=lambda x: x.upper(),
        inputs=input1,
        outputs=output
    )

demo.launch()
```

### 2. 流式输出

```python
import gradio as gr
import time

def stream_response(message):
    """流式生成响应"""
    response = f"正在处理: {message}\n"
    
    # 模拟流式输出
    for i in range(5):
        time.sleep(0.5)  # 模拟处理时间
        response += f"步骤 {i+1} 完成...\n"
        yield response
    
    response += "✅ 处理完成！"
    yield response

with gr.Blocks() as demo:
    input_box = gr.Textbox(label="输入")
    output_box = gr.Textbox(label="输出", lines=10)
    btn = gr.Button("提交")
    
    # 使用 yield 实现流式输出
    btn.click(
        fn=stream_response,
        inputs=input_box,
        outputs=output_box
    )

demo.launch()
```

### 3. 异步函数

```python
import gradio as gr
import asyncio

async def async_process(text):
    """异步处理函数"""
    await asyncio.sleep(2)  # 模拟异步操作
    return f"异步处理结果: {text}"

with gr.Blocks() as demo:
    input_box = gr.Textbox()
    output_box = gr.Textbox()
    btn = gr.Button("提交")
    
    btn.click(
        fn=async_process,
        inputs=input_box,
        outputs=output_box
    )

demo.launch()
```

---

## 🎭 主题和样式

### 1. 内置主题

```python
import gradio as gr

# 可用主题
# - gr.themes.Default()      # 默认
# - gr.themes.Soft()         # 柔和
# - gr.themes.Monochrome()   # 单色
# - gr.themes.Glass()        # 玻璃
# - gr.themes.Origin()       # 原始
# - gr.themes.Citrus()       # 柑橘

demo = gr.Interface(
    fn=lambda x: x,
    inputs="text",
    outputs="text",
    theme=gr.themes.Soft()  # 使用柔和主题
)

demo.launch()
```

### 2. 自定义主题

```python
import gradio as gr

# 创建自定义主题
custom_theme = gr.themes.Default(
    primary_hue="blue",
    secondary_hue="indigo",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Roboto"), "Arial", "sans-serif"]
).set(
    body_background_fill="*neutral_50",
    body_text_color="*neutral_900",
    button_primary_background_fill="*primary_500",
    button_primary_text_color="white"
)

with gr.Blocks(theme=custom_theme) as demo:
    gr.Markdown("# 自定义主题示例")
    gr.Button("按钮", variant="primary")

demo.launch()
```

### 3. CSS 自定义

```python
import gradio as gr

custom_css = """
#component-1 {  /* 组件 ID */
    border: 2px solid blue;
    border-radius: 10px;
}

.input-box {  /* 自定义类名 */
    background-color: #f0f0f0;
}
"""

with gr.Blocks(css=custom_css) as demo:
    gr.Textbox(elem_id="component-1", label="自定义样式")
    gr.Textbox(elem_classes="input-box", label="自定义类名")

demo.launch()
```

---

## 🌐 部署和分享

### 1. 本地部署

```python
import gradio as gr

demo = gr.Interface(
    fn=lambda x: x,
    inputs="text",
    outputs="text"
)

# 本地启动
demo.launch(
    server_name="0.0.0.0",      # 监听所有网络接口
    server_port=7860,           # 端口号
    share=False,                # 不生成分享链接
    show_error=True,            # 显示错误信息
    quiet=False                 # 显示启动信息
)
```

### 2. 生成分享链接

```python
import gradio as gr

demo = gr.Interface(
    fn=lambda x: x,
    inputs="text",
    outputs="text"
)

# 生成 72 小时有效的分享链接
demo.launch(share=True)
```

### 3. 嵌入其他网页

```python
import gradio as gr

demo = gr.Interface(
    fn=lambda x: x,
    inputs="text",
    outputs="text"
)

# 生成嵌入代码
demo.launch(share=True)

# 在其他网页中嵌入
"""
<script
	type="module"
	src="https://gradio.s3-us-west-2.amazonaws.com/4.0.0/gradio.js"
></script>
<gradio-app src="https://xxxx.gradio.live"></gradio-app>
"""
```

---

## 🎓 CampusFlow 实战示例

### 智慧校园助手界面

```python
"""
CampusFlow Gradio 前端
智慧校园助手对话界面
"""

import gradio as gr
from typing import List, Tuple, Dict
import time

class CampusAssistantUI:
    """校园助手 UI 类"""
    
    def __init__(self):
        self.conversation_count = 0
        self.query_stats = {
            "rag": 0,
            "graph": 0,
            "search": 0
        }
    
    def create_interface(self):
        """创建主界面"""
        
        with gr.Blocks(
            title="🎓 智慧校园助手",
            theme=gr.themes.Soft(),
            css="""
            .chatbot { height: 500px; }
            .input-box { border-radius: 20px; }
            """
        ) as demo:
            
            # 标题
            gr.Markdown("""
            # 🎓 智慧校园助手
            
            基于 LangGraph 的多智能体校园助手，可以帮您：
            - 📚 查询校园知识（报到、选课、宿舍等）
            - 🕸️ 查询复杂关系（同学、教师等）
            - 🌐 搜索最新信息（政策、新闻等）
            - 💾 记住我们的对话历史
            """)
            
            with gr.Row():
                # 左侧：对话区域
                with gr.Column(scale=3):
                    # 对话历史（使用新版 Chatbot 格式）
                    chatbot = gr.Chatbot(
                        label="对话历史",
                        height=500,
                        show_label=False,
                        bubble_full_width=False
                    )
                    
                    # 输入区域
                    with gr.Row():
                        user_input = gr.Textbox(
                            label="输入您的问题",
                            placeholder="例如：新生报到需要准备什么材料？",
                            scale=9,
                            elem_classes="input-box"
                        )
                        submit_btn = gr.Button(
                            "🚀 发送",
                            variant="primary",
                            scale=1
                        )
                
                # 右侧：控制面板
                with gr.Column(scale=1):
                    gr.Markdown("### 🎛️ 快捷操作")
                    
                    with gr.Accordion("常用查询", open=True):
                        btn_enrollment = gr.Button("📋 报到流程")
                        btn_course = gr.Button("📚 选课指南")
                        btn_dormitory = gr.Button("🏠 宿舍规定")
                        btn_search = gr.Button("🔍 实时搜索")
                    
                    gr.Markdown("### ⚙️ 设置")
                    
                    # 功能开关
                    enable_rag = gr.Checkbox(
                        label="启用知识库",
                        value=True
                    )
                    enable_graph = gr.Checkbox(
                        label="启用知识图谱",
                        value=True
                    )
                    enable_search = gr.Checkbox(
                        label="启用网络搜索",
                        value=False
                    )
                    
                    # 清空按钮
                    btn_clear = gr.Button("🗑️ 清空历史", variant="secondary")
                    
                    gr.Markdown("### 📊 统计")
                    
                    stats_text = gr.Textbox(
                        label="使用统计",
                        value=self._get_stats_text(),
                        interactive=False,
                        lines=4
                    )
            
            # 示例问题
            gr.Markdown("### 💡 示例问题")
            examples = gr.Examples(
                examples=[
                    ["新生报到需要准备什么材料？"],
                    ["宿舍有哪些管理规定？"],
                    ["如何进行选课？"],
                    ["缴费项目和截止时间？"],
                    ["校园主要建筑在哪里？"],
                    ["我的同学有哪些？"],
                    ["今天校园有什么新闻？"]
                ],
                inputs=user_input,
                label="点击示例快速输入"
            )
            
            # ========== 事件绑定 ==========
            
            # 提交按钮
            submit_btn.click(
                fn=self._handle_message,
                inputs=[
                    user_input,
                    chatbot,
                    enable_rag,
                    enable_graph,
                    enable_search
                ],
                outputs=[chatbot, user_input, stats_text]
            )
            
            # 回车提交
            user_input.submit(
                fn=self._handle_message,
                inputs=[
                    user_input,
                    chatbot,
                    enable_rag,
                    enable_graph,
                    enable_search
                ],
                outputs=[chatbot, user_input, stats_text]
            )
            
            # 快捷按钮
            btn_enrollment.click(
                fn=lambda: "新生报到需要准备什么材料？",
                outputs=user_input
            )
            
            btn_course.click(
                fn=lambda: "如何进行选课？",
                outputs=user_input
            )
            
            btn_dormitory.click(
                fn=lambda: "宿舍有哪些管理规定？",
                outputs=user_input
            )
            
            btn_search.click(
                fn=lambda: "今天校园有什么新闻？",
                outputs=user_input
            )
            
            # 清空历史
            btn_clear.click(
                fn=self._clear_history,
                outputs=[chatbot, user_input, stats_text]
            )
            
            return demo
    
    def _handle_message(
        self,
        message: str,
        history: List[Dict[str, str]],
        enable_rag: bool,
        enable_graph: bool,
        enable_search: bool
    ) -> Tuple[List[Dict[str, str]], str, str]:
        """
        处理用户消息
        
        返回：
        - 更新后的对话历史（OpenAI 格式）
        - 清空输入框
        - 更新统计信息
        """
        if not message.strip():
            return history, "", self._get_stats_text()
        
        self.conversation_count += 1
        
        # 模拟处理（实际应调用后端 API）
        response = self._generate_response(
            message,
            enable_rag,
            enable_graph,
            enable_search
        )
        
        # 转换为 OpenAI 格式的消息列表
        messages = []
        
        # 添加历史消息
        if history:
            for msg in history:
                messages.append(msg)
        
        # 添加新消息
        messages.append({"role": "user", "content": message})
        messages.append({"role": "assistant", "content": response})
        
        return messages, "", self._get_stats_text()
    
    def _generate_response(
        self,
        message: str,
        enable_rag: bool,
        enable_graph: bool,
        enable_search: bool
    ) -> str:
        """生成响应（模拟）"""
        # 根据关键词返回模拟响应
        message_lower = message.lower()
        
        if "报到" in message:
            if enable_rag:
                self.query_stats["rag"] += 1
            return """关于报到：

✅ 新生报到需要准备以下材料：
1. 录取通知书
2. 身份证及复印件
3. 高考准考证
4. 近期一寸免冠照片（10张）
5. 党团组织关系证明

报到时间：9月1日-9月3日
报到地点：学生服务中心"""
        
        elif "同学" in message or "老师" in message:
            if enable_graph:
                self.query_stats["graph"] += 1
            return """关于关系查询：

🕸️ 根据知识图谱查询结果：
- 张三（CS2401班）
  - 同班同学：李四、王五、赵六
  - 班主任：李老师
  - 辅导员：王老师

您可以进一步询问某位同学或老师的详细信息。"""
        
        elif "新闻" in message or "最新" in message:
            if enable_search:
                self.query_stats["search"] += 1
            return """关于最新信息：

🌐 实时搜索结果：
1. 2025校园科技节将于3月15日举行
2. 图书馆延长开放时间至晚上10点
3. 新增"人工智能伦理"选修课

信息来源：校园官网、教务处通知"""
        
        else:
            return """您好！我是智慧校园助手，可以帮您：

📋 查询报到流程和材料
🏠 了解宿舍管理规定
📚 获取选课指南
💰 查询缴费信息
🗺️ 校园导航
👥 查询同学/老师关系
🔍 搜索最新校园动态

请告诉我您想了解什么？"""
    
    def _clear_history(self) -> Tuple[List, str, str]:
        """清空历史"""
        self.conversation_count = 0
        self.query_stats = {"rag": 0, "graph": 0, "search": 0}
        return [], "", self._get_stats_text()
    
    def _get_stats_text(self) -> str:
        """获取统计信息文本"""
        return f"""对话次数: {self.conversation_count}
知识库查询: {self.query_stats['rag']}
关系查询: {self.query_stats['graph']}
搜索查询: {self.query_stats['search']}"""


# 启动应用
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 启动智慧校园助手（Gradio 前端）")
    print("=" * 60)
    
    ui = CampusAssistantUI()
    demo = ui.create_interface()
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
```

---

## 📚 学习资源

### 官方文档
- Gradio 官方文档：https://www.gradio.app/docs
- Gradio 指南：https://www.gradio.app/guides
- Gradio 示例：https://www.gradio.app/playground

### 推荐阅读
- 《Gradio 实战：快速构建 ML 界面》
- 《Python Web 界面开发》
- 《零前端知识构建 AI 应用》

---

**文档创建时间**：2026-01-30
**文档维护者**：CampusFlow 项目组
