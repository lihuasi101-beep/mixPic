import streamlit as st
import requests
import io
import time
import random

# --- 1. 核心配置 ---
# 云端会自动从 Secrets 读取，本地会从 .streamlit/secrets.toml 读取
HF_TOKEN = st.secrets["HF_TOKEN"]

# 使用你刚刚本地跑通的模型和路径协议
MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"
API_URL = f"https://router.huggingface.co/hf-inference/v1/models/{MODEL_ID}"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
    "x-use-cache": "false"
}

# --- 2. 初始化历史记录存储 ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- 3. UI 界面 ---
st.set_page_config(page_title="IP Fusion Pro 2026", layout="wide", page_icon="🎨")
st.title("🚀 跨界 IP 融合专业版")

with st.sidebar:
    st.header("控制台")
    sel_pokemon = st.selectbox("选择宝可梦", ["Pikachu", "Charizard", "Gengar", "Lucario", "Snorlax", "Mewtwo"])
    sel_char = st.text_input("输入动漫角色", "Goku")
    sel_style = st.selectbox("画风", ["Anime style", "3D Render", "Ukiyo-e", "Cyberpunk"])
    num_images = st.slider("生成数量", 1, 4, 1)
    
    if st.button("🗑️ 清空历史记录"):
        st.session_state.history = []
        st.rerun()

# --- 4. 核心请求函数 ---
def query_image(payload):
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    
    # 自动处理路径抖动
    if response.status_code == 404:
        alt_url = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"
        response = requests.post(alt_url, headers=headers, json=payload, timeout=60)
    
    # 模型唤醒
    if response.status_code == 503:
        with st.status("🚀 正在唤醒远程 GPU 节点...", expanded=False):
            time.sleep(10)
            return query_image(payload)
            
    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")
    return response.content

# --- 5. 生成逻辑 ---
if st.button(f"✨ 立即融合并生成", type="primary", use_container_width=True):
    cols = st.columns(num_images)
    for i in range(num_images):
        prompt = f"A unique fusion of {sel_pokemon} and {sel_char}, {sel_style}, masterpiece, 8k"
        with cols[i]:
            with st.spinner(f"正在渲染..."):
                try:
                    image_bytes = query_image({"inputs": prompt})
                    st.image(image_bytes, use_container_width=True)
                    
                    # 保存到历史
                    st.session_state.history.insert(0, {
                        "image": image_bytes,
                        "label": f"{sel_pokemon} x {sel_char}",
                        "time": time.strftime("%H:%M:%S")
                    })
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")

# --- 6. 历史展示 ---
if st.session_state.history:
    st.divider()
    gallery_cols = st.columns(4)
    for idx, item in enumerate(st.session_state.history):
        with gallery_cols[idx % 4]:
            st.image(item["image"], caption=item["label"], use_container_width=True)