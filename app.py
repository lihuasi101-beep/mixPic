import streamlit as st
import requests
import io
import time
import random

# --- 1. 核心配置 ---
# --- 1. 核心配置 ---
HF_TOKEN = st.secrets["HF_TOKEN"]

# 【关键修改】：使用全新的 2026 路由地址
# 格式为：https://router.huggingface.co/hf-inference/models/模型ID
MODEL_ID = "runwayml/stable-diffusion-v1-5"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# --- 2. 初始化历史记录存储 ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- 3. UI 界面 ---
st.set_page_config(page_title="IP Fusion Pro", layout="wide", page_icon="🎨")
st.title("🚀 跨界 IP 融合专业版")

with st.sidebar:
    st.header("控制台")
    sel_pokemon = st.selectbox("选择宝可梦", ["Pikachu", "Charizard", "Gengar", "Lucario", "Snorlax", "Mewtwo"])
    sel_char = st.text_input("输入动漫角色", "Goku")
    sel_style = st.selectbox("画风", ["Anime style", "3D Render", "Ukiyo-e", "Cyberpunk"])
    num_images = st.slider("批量生成数量", 1, 4, 1)
    
    if st.button("🗑️ 清空历史记录"):
        st.session_state.history = []
        st.rerun()

# --- 4. 生成函数 (底层请求) ---
def query_image(payload):
    # 现在请求会发送到 https://router.huggingface.co...
    response = requests.post(API_URL, headers=headers, json=payload)
    
    # 如果遇到 503，说明模型正在加载，需要重试
    if response.status_code == 503:
        time.sleep(5)
        return query_image(payload)
        
    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")
    return response.content

# --- 5. 生成逻辑 ---
if st.button(f"✨ 立即融合并生成 {num_images} 张方案", type="primary", use_container_width=True):
    cols = st.columns(num_images)
    
    for i in range(num_images):
        random_seed = random.randint(1, 1000000)
        current_prompt = (
            f"A unique fusion of {sel_pokemon} and {sel_char}, detailed {sel_style}, "
            f"masterpiece, 8k, seed {random_seed}"
        )
        
        with cols[i]:
            with st.spinner(f"正在构思第 {i+1} 张..."):
                try:
                    # 直接获取二进制数据，避开 SDK 的迭代器 Bug
                    image_bytes = query_image({"inputs": current_prompt})
                    
                    # 显示图片
                    st.image(image_bytes, use_container_width=True)
                    
                    # 保存到历史记录
                    st.session_state.history.insert(0, {
                        "image": image_bytes,
                        "label": f"{sel_pokemon} x {sel_char}",
                        "time": time.strftime("%H:%M:%S")
                    })
                        
                except Exception as e:
                    st.error(f"生成失败详情: {str(e)}")

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