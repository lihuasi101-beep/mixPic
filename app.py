import streamlit as st
from huggingface_hub import InferenceClient
import io
import random
import time

# --- 1. 核心配置 ---
# 建议：如果是为了发布到网上，Token 最好通过 st.secrets 读取（见下文部署建议）
HF_TOKEN = st.secrets["HF_TOKEN"]
# HF_TOKEN = "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" 
client = InferenceClient(token=HF_TOKEN)
MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"

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
    num_images = st.slider("批量生成数量", 1, 4, 4)
    
    if st.button("🗑️ 清空历史记录"):
        st.session_state.history = []
        st.rerun()

# --- 4. 生成逻辑 ---
if st.button(f"✨ 立即融合并生成 {num_images} 张方案", type="primary", use_container_width=True):
    cols = st.columns(num_images)
    
    for i in range(num_images):
        # 【功能一：微调提示词】
        # 加入随机种子和动态描述，确保每张图都不一样
        variation_keywords = ["action pose", "close-up portrait", "dramatic lighting", "scenic background"]
        random_seed = random.randint(1, 1000000)
        current_prompt = (
            f"A unique fusion of {sel_pokemon} and {sel_char}, {random.choice(variation_keywords)}, "
            f"detailed {sel_style}, masterpiece, 8k, seed {random_seed}"
        )
        
        with cols[i]:
            with st.spinner(f"正在构思第 {i+1} 张..."):
                try:
                    image = client.text_to_image(current_prompt, model=MODEL_ID)
                    st.image(image, use_column_width=True)
                    
                    # 【功能二：自动保存历史记录】
                    # 将图片转为字节流存入 session_state
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    
                    # 保存到历史列表的最前面
                    st.session_state.history.insert(0, {
                        "image": img_byte_arr.getvalue(),
                        "label": f"{sel_pokemon} x {sel_char}",
                        "time": time.strftime("%H:%M:%S")
                    })
                    
                except Exception as e:
                    st.error(f"生成失败: {e}")

# --- 5. 创意画廊展示 ---
if st.session_state.history:
    st.divider()
    st.subheader("🖼️ 历史实验画廊 (本会话)")
    # 每行显示 4 张历史图片
    gallery_cols = st.columns(4)
    for idx, item in enumerate(st.session_state.history):
        with gallery_cols[idx % 4]:
            st.image(item["image"], caption=f"{item['label']} @ {item['time']}", use_column_width=True)
            st.download_button("💾 下载", item["image"], file_name=f"history_{idx}.png", key=f"dl_{idx}")