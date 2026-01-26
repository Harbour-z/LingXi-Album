# Embedding 服务迁移到阿里云 DashScope API

## 概述

本文档描述了将 Embedding 服务从本地模型推理迁移到阿里云 DashScope API 的完整过程。

## 变更内容

### 1. 新增配置项

在 `.env` 文件中新增以下配置：

```
# Embedding Service Configuration (API-based)
EMBEDDING_API_PROVIDER="aliyun"  # 选择 aliyun 使用 API 服务
ALIYUN_EMBEDDING_API_KEY="your-api-key"  # DashScope API Key
ALIYUN_EMBEDDING_MODEL_NAME="qwen3-vl-embedding"  # 模型名称
ALIYUN_EMBEDDING_DIMENSION=2560  # 向量维度
```

**支持的向量维度**：2560, 2048, 1536, 1024, 768, 512, 256

### 2. 新增代码文件

- [`app/services/aliyun_embedding_client.py`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/services/aliyun_embedding_client.py)：阿里云 DashScope Embedding API 客户端

### 3. 修改的文件

- [`app/config.py`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/config.py)：新增阿里云 Embedding 配置项
- [`app/services/embedding_service.py`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/services/embedding_service.py)：支持 API 客户端初始化和调用
- [`app/main.py`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/main.py)：更新 Embedding 服务初始化逻辑
- [`.env`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/.env)：更新配置
- [`.env.template`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/.env.template)：更新配置模板
- [`README.md`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/README.md)：更新文档

## API 调用方式

使用 DashScope SDK 进行多模态融合向量生成：

```python
import dashscope
from http import HTTPStatus

# 多模态融合向量
input_data = [
    {
        "text": "这是一段测试文本",
        "image": "https://example.com/image.jpg"
    }
]

resp = dashscope.MultiModalEmbedding.call(
    api_key="your-api-key",
    model="qwen3-vl-embedding",
    input=input_data,
    parameters={"dimension": 2048}
)

if resp.status_code == HTTPStatus.OK:
    embedding = resp.output.embeddings[0].embedding
    print(f"向量维度: {len(embedding)}")
```

## 接口兼容性

所有现有的 Embedding 服务接口保持不变：

- `generate_embedding(text, image, instruction, normalize)` - 生成单个 Embedding
- `generate_embeddings_batch(inputs, normalize)` - 批量生成 Embedding
- `vector_dimension` - 获取向量维度
- `is_initialized` - 检查初始化状态

## 使用方式

### 本地模型（原有方式）

```bash
EMBEDDING_API_PROVIDER="local"
# 需要本地 qwen3-vl-embedding-2B 模型
```

### 阿里云 API（新方式）

```bash
EMBEDDING_API_PROVIDER="aliyun"
ALIYUN_EMBEDDING_API_KEY="your-dashscope-api-key"
ALIYUN_EMBEDDING_MODEL_NAME="qwen3-vl-embedding"
ALIYUN_EMBEDDING_DIMENSION=2048
```

## 优势

1. **无需本地模型**：节省 16GB+ 内存，降低硬件要求
2. **API 服务稳定**：使用阿里云官方服务，无需担心模型加载和推理
3. **多模态融合**：支持文本、图片、视频的融合向量生成
4. **灵活配置**：支持多种向量维度选择
5. **接口兼容**：完全兼容原有接口，无需修改业务代码

## 测试

运行测试脚本验证配置：

```bash
python test_embedding_api.py
```

## 注意事项

1. 需要有效的 DashScope API Key
2. API 调用需要网络连接
3. 向量维度需与 Qdrant 配置保持一致（默认 2048）
4. API 调用可能产生费用，请查看阿里云定价

## 参考资料

- [阿里云 DashScope 多模态向量 API 文档](https://bailian.console.aliyun.com/cn-beijing/?tab=api#/api/?type=model&url=2712517)
- [DashScope Python SDK](https://github.com/aliyun/dashscope)
