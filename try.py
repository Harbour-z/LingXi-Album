
import dashscope
import json
import os
from http import HTTPStatus

# 多模态融合向量：将文本、图片、视频融合成一个融合向量
# 适用于跨模态检索、图搜等场景
text = "这是一段测试文本，用于生成多模态融合向量"
image = "https://dashscope.oss-cn-beijing.aliyuncs.com/images/256_1.png"
video = "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250107/lbcemt/new+video.mp4"

# 输入包含文本、图片、视频，模型会将它们融合成一个融合向量
input_data = [
    {
        "text": text,
        "image": image,
        "video": video
    }
]

# 使用 qwen3-vl-embedding 生成融合向量
resp = dashscope.MultiModalEmbedding.call(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key="sk-910f592a3659402db9c17ac7f8c59fd9",
    model="qwen3-vl-embedding",
    input=input_data,
    parameters={"dimension": 2048}
    # 可选参数：指定向量维度（支持 2560, 2048, 1536, 1024, 768, 512, 256，默认 2560）
    # parameters={"dimension": 1024}
)

print(json.dumps(resp.output, indent=4))
actual_dim = len(resp.output['embeddings'][0]['embedding'])
print(f"向量维度: {actual_dim}")
