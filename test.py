from huggingface_hub import InferenceClient
from PIL import Image
import io

# 1. 初始化客户端
client = InferenceClient(token="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")

print("🚀 正在通过官方 SDK 请求 2026 年最新接口...")

try:
    # 2. 我们选择一个目前在 Hugging Face 上非常热门且稳定的模型
    # 如果 SDXL 依然有问题，SDK 会自动报错提醒
    image = client.text_to_image(
        "A cute fusion of Pikachu and Naruto, high quality anime style, masterpiece",
        model="stabilityai/stable-diffusion-xl-base-1.0"
    )

    # 3. 保存图片
    image.save("success.png")
    print("✨ 终于成功了！快去文件夹里看 success.png")

except Exception as e:
    print(f"❌ 还是出了一点小问题：{e}")