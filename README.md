# 智慧相册后端系统 (Smart Album Backend)

基于语义检索的智能图片管理系统，支持多模态Embedding生成、语义化图片检索、以图搜图等功能。

## 核心特性

- **多模态Embedding生成**: 支持文本、图片、图文混合输入的向量表示生成
- **语义化图片检索**: 通过自然语言描述搜索图片（如「日落时的海滩」）
- **以图搜图**: 查找视觉相似的图片
- **异步索引**: 上传图片后台生成Embedding，响应速度提升10倍
- **智能设备选择**: 自动选择最优推理设备（CUDA > MPS > CPU）
- **存储索引一致性**: 统一ID管理，确保文件与向量数据库同步
- **AI Agent集成**: 为openjiuwen等框架预留标准化接口

## 技术架构

```
ImgEmbedding2VecDB/
├── app/                      # 后端API服务
│   ├── main.py              # FastAPI主应用入口
│   ├── config.py            # 配置管理
│   ├── models/              # Pydantic数据模型
│   ├── services/            # 业务服务层
│   └── routers/             # API路由
├── agent/                   # Agent集成模块（可选）
│   ├── agent_main.py        # OpenJiuwen Agent主程序
│   ├── config.py            # Agent配置
│   └── tools/               # Agent工具集
│       ├── album_tools.py   # 相册管理工具
│       └── search_tools.py  # 搜索工具
├── qwen3-vl-embedding-2B/   # 多模态Embedding模型
├── storage/                 # 图片存储目录
├── qdrant_data/             # Qdrant本地数据
├── start_agent.sh           # Agent一键启动脚本
└── requirements.txt
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置模型路径

系统会自动查找项目根目录下的 `qwen3-vl-embedding-2B/` 模型，无需额外配置。

**如果模型在其他位置**，通过以下任一方式指定：

#### 方式1：环境变量（推荐）
```bash
export MODEL_PATH=/path/to/your/qwen3-vl-embedding-2B
uvicorn app.main:app --reload
```

#### 方式2：.env 文件
```bash
# 项目根目录创建 .env 文件
echo "MODEL_PATH=/path/to/your/qwen3-vl-embedding-2B" > .env
```

#### 方式3：创建软链接
```bash
# 将模型链接到项目目录（适合模型在其他盘符）
ln -s /path/to/your/qwen3-vl-embedding-2B ./qwen3-vl-embedding-2B
```

**模型目录结构示例：**
```
qwen3-vl-embedding-2B/
├── config.json
├── model.safetensors（或 .bin）
├── tokenizer_config.json
├── preprocessor_config.json
└── scripts/
    ├── qwen3_vl_embedding.py
    └── chat_template.jinja
```

### 3. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**启动日志示例：**
```
INFO - ==================================================
INFO - 智慧相册后端系统启动中...
INFO - ==================================================
INFO - 初始化存储服务...
INFO - 初始化向量数据库服务...
INFO - 初始化Embedding服务...
INFO - 正在初始化Embedding模型: ./qwen3-vl-embedding-2B
INFO - 使用CUDA设备进行推理  # 或 MPS / CPU
INFO - Embedding模型初始化完成
INFO - 所有服务初始化完成!
```

### 4. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API接口说明

### Embedding服务 (`/api/v1/embedding`)

| 接口         | 方法 | 说明                                   |
| ------------ | ---- | -------------------------------------- |
| `/generate`  | POST | 生成多模态Embedding向量                |
| `/text`      | POST | 快捷：纯文本Embedding                  |
| `/image`     | POST | 快捷：图片Embedding（支持URL自动存储） |
| `/dimension` | GET  | 获取向量维度                           |

**`/image` 参数说明：**
```python
image_url: str           # 图片URL
auto_store: bool = False # 是否下载并存储图片
auto_index: bool = False # 是否自动索引到向量库（需auto_store=True）
tags: str = None         # 标签，逗号分隔
```

**使用场景：**
```bash
# 场景1：仅生成Embedding（不存储）
curl "http://localhost:8000/api/v1/embedding/image?image_url=https://example.com/img.png"

# 场景2：下载+存储+索引（一步到位）
curl "http://localhost:8000/api/v1/embedding/image?image_url=https://example.com/img.png&auto_store=true&auto_index=true&tags=风景"
```

### 向量数据库 (`/api/v1/vectors`)

| 接口                    | 方法   | 说明              |
| ----------------------- | ------ | ----------------- |
| `/upsert`               | POST   | 插入/更新向量记录 |
| `/upsert/batch`         | POST   | 批量插入/更新     |
| `/{vector_id}`          | GET    | 获取向量记录      |
| `/{vector_id}`          | DELETE | 删除向量记录      |
| `/{vector_id}/metadata` | PATCH  | 更新元数据        |
| `/`                     | GET    | 列出向量记录      |
| `/stats/info`           | GET    | 集合统计信息      |

### 智能搜索 (`/api/v1/search`)

| 接口                | 方法 | 说明             |
| ------------------- | ---- | ---------------- |
| `/`                 | POST | 统一搜索接口     |
| `/text`             | GET  | 文本语义搜索     |
| `/image/{image_id}` | GET  | 以图搜图（按ID） |
| `/image`            | POST | 上传图片搜索     |
| `/hybrid`           | POST | 图文混合搜索     |

**示例请求:**
```json
POST /api/v1/search/
{
  "query_text": "日落时的海滩",
  "top_k": 10,
  "score_threshold": 0.5
}
```

### 图片存储 (`/api/v1/storage`)

| 接口                      | 方法   | 说明                           |
| ------------------------- | ------ | ------------------------------ |
| `/upload`                 | POST   | 上传图片（支持异步/同步索引）  |
| `/upload/batch`           | POST   | 批量上传                       |
| `/images/{image_id}`      | GET    | 获取图片文件                   |
| `/images/{image_id}/info` | GET    | 获取图片信息                   |
| `/images/{image_id}`      | DELETE | 删除图片（同步清理向量数据库） |
| `/images`                 | GET    | 列出图片                       |
| `/index/{image_id}`       | POST   | 手动索引单张图片               |
| `/index/all`              | POST   | 批量索引所有未索引图片         |

**上传参数说明：**
```python
auto_index: bool = True      # 是否自动索引
async_index: bool = True     # 是否异步索引（推荐）
tags: str = "风景,海滩"      # 标签，逗号分隔
description: str = "..."     # 图片描述
```

**性能对比：**
- 异步模式：~200ms 响应，后台处理
- 同步模式：~2-5s 响应，立即可搜索

### Agent集成 (`/api/v1/agent`)

| 接口       | 方法 | 说明             |
| ---------- | ---- | ---------------- |
| `/actions` | GET  | 获取可用动作列表 |
| `/execute` | POST | 执行Agent动作    |
| `/status`  | GET  | 获取系统状态     |
| `/schema`  | GET  | 获取API Schema   |

## 配置说明

可通过环境变量或 `.env` 文件配置：

| 配置项             | 默认值                    | 说明                           |
| ------------------ | ------------------------- | ------------------------------ |
| `MODEL_PATH`       | `./qwen3-vl-embedding-2B` | Embedding模型路径              |
| `QDRANT_MODE`      | `local`                   | Qdrant模式：local/docker/cloud |
| `QDRANT_HOST`      | `localhost`               | Qdrant主机（docker/cloud模式） |
| `QDRANT_PORT`      | `6333`                    | Qdrant端口                     |
| `QDRANT_PATH`      | `./qdrant_data`           | 本地存储路径（local模式）      |
| `STORAGE_PATH`     | `./storage/images`        | 图片存储路径                   |
| `VECTOR_DIMENSION` | `2048`                    | 向量维度                       |

## Docker部署

切换到Docker模式部署Qdrant：

```bash
# 启动Qdrant容器
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant

# 设置环境变量
export QDRANT_MODE=docker
export QDRANT_HOST=localhost
export QDRANT_PORT=6333

# 启动应用
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 使用示例

### Python客户端示例

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. 上传图片
with open("photo.jpg", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/storage/upload",
        files={"file": f},
        data={"auto_index": True, "tags": "风景,海滩"}
    )
    image_id = response.json()["data"]["id"]

# 2. 文本搜索
results = requests.get(
    f"{BASE_URL}/search/text",
    params={"query": "蓝天白云", "top_k": 5}
).json()["data"]

# 3. 以图搜图
similar = requests.get(
    f"{BASE_URL}/search/image/{image_id}",
    params={"top_k": 10}
).json()["data"]

# 4. 从URL下载并索引图片（新增）
result = requests.post(
    f"{BASE_URL}/embedding/image",
    params={
        "image_url": "https://example.com/photo.jpg",
        "auto_store": True,
        "auto_index": True,
        "tags": "风景"
    }
).json()
stored_id = result.get("stored_image_id")
```

### cURL示例

```bash
# 上传图片
curl -X POST "http://localhost:8000/api/v1/storage/upload" \
  -F "file=@photo.jpg" \
  -F "auto_index=true" \
  -F "tags=风景,海滩"

# 文本搜索
curl "http://localhost:8000/api/v1/search/text?query=蓝天白云&top_k=5"

# 获取系统状态
curl "http://localhost:8000/status"
```

## Agent集成指南

系统提供两种 Agent 集成方式：

### 方式1：HTTP API调用（推荐）

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 搜索图片
results = requests.get(
    f"{BASE_URL}/search/text",
    params={"query": "进一张有猫的照片", "top_k": 5}
).json()["data"]

# 上传图片
with open("cat.jpg", "rb") as f:
    result = requests.post(
        f"{BASE_URL}/storage/upload",
        files={"file": f},
        data={"auto_index": True, "tags": "动物,猫"}
    ).json()["data"]
```

### 方式2：OpenJiuwen 框架集成

项目已内置 Agent 工具集，支持 OpenJiuwen 等框架：

```bash
# 一键启动（后端 + Agent）
./start_agent.sh

# 或分步启动
# 终端1：后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 终端2：Agent
cd agent && python agent_main.py
```

**可用工具：**
- `album_tools.py`: 上传、删除、查看图片
- `search_tools.py`: 文本搜索、以图搜图、混合搜索

**配置示例：**
```python
# agent/config.py
ALBUM_API_BASE_URL = "http://localhost:8000/api/v1"
LLM_MODEL = "qwen-plus"
LLM_API_KEY = "your-api-key"  # 华为云API密钥
```

## 系统要求

- Python 3.10+
- PyTorch 2.0+
- 推理设备（按优先级）：
  - NVIDIA GPU (CUDA) - 最快
  - Apple Silicon (MPS) - 次之
  - CPU - 可用但较慢
- 16GB+ 内存（加载模型）

## License

MIT License
