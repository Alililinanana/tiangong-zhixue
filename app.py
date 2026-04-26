import streamlit as st
from openai import OpenAI
import PyPDF2
import docx
import os

# 云端隐藏密钥，全程无明文，零泄露

client = OpenAI(
    api_key=os.environ.get("ARK_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

# 天大能动专属人设
base_prompt = """
你是【天工智学】，天津大学能源与动力工程大一专属AI学习助手。
专注：微积分、大物、化学、理论力学、工程制图。
简洁高效作答，结合上传课件精准答疑。
"""

# 三档难度
level_prompt = {
    "🔹 极简通俗模式（预习/速成）": "大白话精简讲解，步骤少、好理解、快速作答。",
    "🔸 课堂标准模式（作业/考试）": "天大课堂标准，步骤规范，简洁不啰嗦，高效解题。",
    "🔶 深度拔高模式（竞赛/科创）": "适度拓展原理与工程应用，条理清晰，回答紧凑。"
}

# 【极速优化】轻量化读取文档 + 强制压缩字数
def read_upload_file(uploaded_file):
    file_ext = uploaded_file.name.split(".")[-1].lower()
    text = ""
    try:
        if file_ext == "pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if not text.strip():
                return "⚠️ 该PDF为扫描件/加密文件，无法识别文字，请上传可编辑的PDF或Word文档"
        elif file_ext == "docx":
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif file_ext == "txt":
            text = uploaded_file.read().decode("utf-8", errors="ignore")
        else:
            return "❌ 不支持的文件格式，请上传PDF、Word或TXT文件"

        # 只保留前3000字，减少传输压力
        return text[:3000]
    except Exception as e:
        return f"❌ 文档读取异常：{str(e)}"

# 页面配置 + 加速渲染
st.set_page_config(page_title="天工智学", page_icon="📚")
st.title("天工智学")
st.subheader("能动专业 · 课件挂载 | 三档难度快速答疑")

# 侧边栏
with st.sidebar:
    st.title("📚 功能控制台")
    select_level = st.selectbox("选择回答难度", list(level_prompt.keys()))
    upload_file = st.file_uploader("上传 PDF / Word / TXT", type=["txt","pdf","docx"])
    if st.button("🔄 清空对话"):
        st.session_state.msg = []
        st.toast("对话已清空，提速流畅")

# 读取上传文件
file_content = ""
if upload_file:
    with st.spinner("快速加载文档中..."):
        file_content = read_upload_file(upload_file)
    st.sidebar.success("✅ 文档加载完成")

# 初始化对话
if "msg" not in st.session_state:
    st.session_state.msg = []

# 只保留最近3轮对话，防止越用越卡
if len(st.session_state.msg) > 6:
    st.session_state.msg = st.session_state.msg[-6:]

# 历史对话展示
for m in st.session_state.msg:
    st.chat_message(m["role"]).write(m["content"])

# 提问
user_input = st.chat_input("请输入问题...")
if user_input:
    sys_prompt = base_prompt + level_prompt[select_level]
    if file_content:
        sys_prompt += f"\n【参考课件】：{file_content}"

    st.session_state.msg.append({"role":"user", "content":user_input})
    st.chat_message("user").write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("AI快速作答中..."):
            response = client.chat.completions.create(
                model="doubao-seed-2-0-pro-260215",
                messages=[{"role":"system","content":sys_prompt}] + st.session_state.msg,
                timeout=60,   # 缩短超时，杜绝卡死
                max_tokens=3000,  # 限制回答长度，提速
                temperature=0.7
            )
        ans = response.choices[0].message.content
        st.write(ans)
        st.session_state.msg.append({"role":"assistant","content":ans})