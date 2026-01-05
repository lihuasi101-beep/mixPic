import streamlit as st
from huggingface_hub import InferenceClient
import io
import random
import time
from PIL import Image

# --- 1. 核心配置 ---
# 确保在 Streamlit Cloud 的 Advanced Settings -> Secrets 中已设置 HF_TOKEN
HF_TOKEN = st.secrets["HF_TOKEN"]
MODEL_ID = "runwayml/stable-diffusion-v1-5"

# 初始化客户端
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

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
    num_images = st.slider("批量生成数量", 1, 4, 1) # 默认改为1，省点额度
    
    if st.button("🗑️ 清空历史记录"):
        st.session_state.history = []
        st.rerun()

# --- 4. 生成逻辑 ---
if st.button(f"✨ 立即融合并生成 {num_images} 张方案", type="primary", use_container_width=True):
    cols = st.columns(num_images)
    
    for i in range(num_images):
        variation_keywords = ["action pose", "close-up portrait", "dramatic lighting", "scenic background"]
        random_seed = random.randint(1, 1000000)
        current_prompt = (
            f"A unique fusion of {sel_pokemon} and {sel_char}, {random.choice(variation_keywords)}, "
            f"detailed {sel_style}, masterpiece, 8k, seed {random_seed}"
        )
        
        with cols[i]:
            with st.spinner(f"正在构思第 {i+1} 张..."):
                try:
                    # 【核心修复】：显式调用并确保获取图像对象
                    # 使用较通用的参数调用方式
                    image = client.text_to_image(
                        current_prompt,
                        model=MODEL_ID
                    )
                    
                    # 检查返回是否有效
                    if image:
                        # 显示图片
                        st.image(image, use_container_width=True)
                        
                        # 将图片转为字节流保存
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='PNG')
                        img_data = img_byte_arr.getvalue()
                        
                        # 保存到历史记录
                        st.session_state.history.insert(0, {
                            "image": img_data,
                            "label": f"{sel_pokemon} x {sel_char}",
                            "time": time.strftime("%H:%M:%S")
                        })
                    else:
                        st.error("模型未能生成图像，请重试。")
                        
                except Exception as e:
                    # 打印更详细的错误便于调试
                    st.error(f"生成失败详情: {type(e).__name__} - {str(e)}")

# --- 5. 创意画廊展示 ---
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