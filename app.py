import streamlit as st
import openai
import os

# 1. 页面基本配置
st.set_page_config(page_title="AI小红书文案生成器", page_icon="📝", layout="centered")

# 初始化 Session State（用于限制单次访问的免费试用次数）
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0

# 最大免费额度
MAX_FREE_LIMIT = 3

# 2. 侧边栏配置：方便用户测试或配置 API
st.sidebar.title("设置")
# 优先读取系统环境变量，若无则允许在侧边栏手动输入
api_key = os.environ.get("OPENAI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("请输入您的 OpenAI API Key", type="password")

st.sidebar.markdown("""
---
### 💡 商业化说明
当用户使用次数达到限制时，侧边栏或主界面会展示付费引导。
""")

# 3. 主界面布局
st.title("📝 AI小红书爆款文案生成器")
st.write("输入关键词，一键生成符合小红书算法与用户喜好的高转化文案。")

# 模板定义
TEMPLATES = {
    "情绪种草型 (强调体验与后悔没早买)": """
你是一个小红书10万粉的种草博主。请帮我写一篇极具情绪价值的情绪种草文案。
要求：
- 语气极度口语化，多用感叹号，像在和闺蜜分享。
- 强调痛点：“我真的后悔没早点知道这个……”
- 突出使用前后的强烈对比。
- 字数在 200 字左右。
""",
    "干货分享型 (结构清晰、步骤详实)": """
你是一个行业干货博主。请帮我写一篇结构清晰、可以直接照做的干货分享文案。
要求：
- 采用 1、2、3 步骤分点阐述，逻辑清晰。
- 语言简练，直奔主题，多用 emoji 图标作为序号。
- 结尾给出明确的行动建议。
- 字数在 300 字左右。
""",
    "对比测评型 (理性客观、突出优势)": """
你是一个测评博主。请帮我写一篇对比测评文案。
要求：
- 采用“传统方式 vs 本产品”或“同类对比”的视角。
- 逻辑客观，但要巧妙地突出我们产品的核心优势。
- 适合理性消费人群。
- 字数在 250 字左右。
"""
}

# 用户输入组件
selected_template_name = st.selectbox("第一步：选择文案风格/模板", list(TEMPLATES.keys()))
keyword = st.text_input("第二步：输入您的产品/场景关键词（例如：极简保温杯、打工人避坑指南）", placeholder="如：Streamlit零基础开发")

# 显示剩余免费次数
remaining = max(0, MAX_FREE_LIMIT - st.session_state.usage_count)
st.write(f"当前会话剩余免费次数：**{remaining}** 次")

# 4. 生成逻辑
if st.button("开始一键生成", type="primary"):
    if not api_key:
        st.error("请先在左侧输入您的 OpenAI API Key 或配置环境变量。")
    elif not keyword.strip():
        st.warning("请输入关键词。")
    elif st.session_state.usage_count >= MAX_FREE_LIMIT:
        # 次数用尽，显示付费提示
        st.error("⚠️ 您今天的免费额度已用完！")
        st.info("""
        ### 🎉 解锁无限次使用
        如需继续体验，请扫码订阅（19.9/月）：
        *(此处可在实际部署时放置您的微信/支付宝收款码图片)*
        """)
        # 也可以在这里放置 Notion 或外部支付页面的链接
        st.markdown("[👉 点击开通 VIP 无限使用权益](#)")
    else:
        with st.spinner("AI 正在深度思考并撰写，请稍候..."):
            try:
                # 组合 Prompt
                system_instruction = TEMPLATES[selected_template_name]
                user_prompt = f"""
                主题关键词：{keyword}
                
                请严格按照以下格式输出：
                ---
                【爆款标题】
                (给出3个不同风格的吸引人标题，含常用小红书emoji)
                
                【正文内容】
                (正式的文案内容，符合所选模板风格，排版多换行，易于阅读)
                
                【热门标签】
                (生成5个相关的热门标签，格式为 #标签名)
                ---
                """
                
                # 调用 API
                client = openai.OpenAI(
                    api_key=api_key, 
                    base_url="https://api.deepseek.com" # 指向 DeepSeek 服务器
                )
                response = client.chat.completions.create(
                    model="deepseek-chat",              # 使用 DeepSeek 的对话模型
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )
                
                result = response.choices[0].message.content
                
                # 增加计数
                st.session_state.usage_count += 1
                
                # 展示结果
                st.success("生成成功！")
                st.markdown(result)
                
            except Exception as e:
                st.error(f"调用 API 过程中出现错误: {str(e)}")
