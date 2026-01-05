import streamlit as st
import requests
import io
import time
import random

# --- 1. 核心配置 ---
# 请确保在 Streamlit Cloud 的 Secrets 中设置了 HF_TOKEN
HF_TOKEN = st.secrets["HF_TOKEN"]

# 使用更现代的模型，它在 2026 年的路由支持最稳定
MODEL_ID = "stabilityai/stable-diffusion-2-1"

# 【2026 最新路由规范地址】
# 注意：router.huggingface.co 后面的路径必须精准匹配模型 ID
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "x-use-cache": "false"  # 强制获取新图，避免缓存错误
}

# --- 2. 初始化历史记录存储 ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- 3. UI 界面 ---
st.set_page_config(page_title="IP Fusion Pro 2026", layout="wide", page_icon="🎨")
st.title("🚀 跨界 IP 融合专业版")
st.caption(f"当前运行模型: {MODEL_ID} (通过 HF Router 部署)")

with st.sidebar:
    st.header("控制台")
    sel_pokemon = st.selectbox("选择宝可梦", ["Pikachu", "Charizard", "Gengar", "Lucario", "Snorlax", "Mewtwo"])
    sel_char = st.text_input("输入动漫角色", "Goku")
    sel_style = st.selectbox("画风", ["Anime style", "3D Render", "Ukiyo-e", "Cyberpunk"])
    num_images = st.slider("批量生成数量", 1, 4, 1)
    
    if st.button("🗑️ 清空历史记录"):
        st.session_state.history = []
        st.rerun()

# --- 4. 核心请求函数 ---
def query_image(payload):
    """
    直接使用 requests 绕过 SDK 的 StopIteration Bug
    """
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    
    # 情况 A：模型正在启动 (503)
    if response.status_code == 503:
        with st.status("🚀 模型正在从深层存储中唤醒，请稍候...", expanded=False):
            time.sleep(10)
            return query_image(payload)
            
    # 情况 B：成功返回 (200)
    if response.status_code == 200:
        return response.content
        
    # 情况 C：报错处理
    raise Exception(f"API 状态码 {response.status_code}: {response.text}")

# --- 5. 生成按钮逻辑 ---
if st.button(f"✨ 立即融合并生成 {num_images} 张方案", type="primary", use_container_width=True):
    cols = st.columns(num_images)
    
    for i in range(num_images):
        # 构造提示词
        random_seed = random.randint(1, 1000000)
        current_prompt = (
            f"A unique fusion of {sel_pokemon} and {sel_char}, {sel_style}, "
            f"masterpiece, high quality, 8k, seed {random_seed}"
        )
        
        with cols[i]:
            with st.spinner(f"正在构思第 {i+1} 张..."):
                try:
                    # 发起请求
                    image_bytes = query_image({"inputs": current_prompt})
                    
                    # 验证并显示图片
                    st.image(image_bytes, use_container_width=True)
                    
                    # 保存到历史记录
                    st.session_state.history.insert(0, {
                        "image": image_bytes,
                        "label": f"{sel_pokemon} x {sel_char}",
                        "time": time.strftime("%H:%M:%S")
                    })
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")

# --- 6. 创意画廊展示 ---
if st.session_state.history:
    st.divider()
    st.subheader("🖼️ 历史实验画廊 (本会话)")
    gallery_cols = st.columns(4)
    for idx, item in enumerate(st.session_state.history):
        with gallery_cols[idx % 4]:
            st.image(item["image"], caption=f"{item['label']} @ {item['time']}", use_container_width=True)
            st.download_button(
                label="💾 下载",
                data=item["image"],
                file_name=f"fusion_{idx}.png",
                mime="image/png",
                key=f"dl_{idx}"
            )