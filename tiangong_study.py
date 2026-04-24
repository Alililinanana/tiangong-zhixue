import streamlit as st
from openai import OpenAI


client = OpenAI(
    api_key="ark-ecd73d74-8dce-4ef1-b0a5-a56e92a70bac-a3133",
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

# 天工智学 大一能动专属设定
sys_prompt = """
你是天工智学，能源与动力工程大一专属学习助手。
主攻大一课程：微积分、大学物理、大学化学、理论力学、工程制图。
专门给大一新生讲基础、讲例题、梳理难点、做学习规划、整理资料总结。
讲解简单易懂，不使用高深专业内容，贴合大一学习进度。
"""

# 网页界面
st.set_page_config(page_title="天工智学")
st.title("天工智学")
st.subheader("能动大一 · 个性化智能学习平台")

# 侧边栏
st.sidebar.title("功能列表")
st.sidebar.text("1. 基础课程答疑")
st.sidebar.text("2. 学习资料总结")
st.sidebar.text("3. 定制学习规划")
st.sidebar.text("4. 工科入门指导")

# 聊天记录
if "msg" not in st.session_state:
    st.session_state.msg = [{"role":"system","content":sys_prompt}]

# 输入框
user_text = st.chat_input("请输入你的问题")
if user_text:
    st.session_state.msg.append({"role":"user","content":user_text})
    st.chat_message("user").write(user_text)

    with st.chat_message("assistant"):
        res = client.chat.completions.create(
            model="doubao-seed-2-0-pro-260215",
            messages=st.session_state.msg
        )
        ans = res.choices[0].message.content
        st.write(ans)
    st.session_state.msg.append({"role":"assistant","content":ans})