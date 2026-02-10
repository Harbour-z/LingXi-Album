# 智慧相册（Smart Album）

一个“上传即索引、对话即找图”的多模态智能相册：

- **语义检索**：输入“海边日落/表格截图/红色跑车”直接找图
- **元数据检索**：按 `created_at/tags/...` 等字段筛选
- **组合检索**：支持“日期 + 语义”混合表达（例如 `1.18 海边`）
- **对话直出图片**：`/agent/chat` 返回 `results.images`，前端聊天直接展示缩略图

## 架构概览

```text
前端（React） ──HTTP──> 后端（FastAPI /api/v1）
                         ├─ Embedding（本地 Qwen3-VL / 阿里云 API，2048d）
                         ├─ Qdrant（向量检索 + payload 过滤）
                         ├─ Storage（本地落盘 + 预览）
                         └─ Agent（ReAct + OpenAI兼容 fallback）
```

## 快速开始

### 方案一：Docker 部署（推荐）

**最简单的方式**，无需配置 Python 环境，一键启动：

#### 前置要求
- 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)
- 准备阿里云 API Keys（3个）

#### 启动步骤

1. **配置 API Keys**
```bash
cp .env.template .env
vim .env  # 填入以下三个 Key
```

需要配置：
- `ALIYUN_EMBEDDING_API_KEY` - 图片向量化
- `OPENAI_API_KEY` - 智能对话
- `VISION_MODEL_API_KEY` - 视觉理解

2. **一键启动**
```bash
# macOS/Linux
./start-docker.sh

# Windows
start-docker.bat
```

3. **访问应用**
- 主页: http://localhost:7860
- API文档: http://localhost:7860/docs

#### 常用命令
```bash
docker-compose ps              # 查看状态
docker-compose logs -f         # 查看日志
docker-compose restart         # 重启服务
docker-compose down            # 停止服务
```

#### 数据持久化
以下目录会自动挂载，数据不会丢失：
- `./storage` - 上传的图片
- `./qdrant_data` - 向量数据库

**详细说明见 [DOCKER.md](DOCKER.md)**

---

### 方案二：本地开发

#### 1) 后端（FastAPI）

#### 环境要求

- Python 3.10+
- 16GB+ 内存（首次加载模型较慢）
- 可选：CUDA 或 Apple Silicon（MPS）加速

#### 安装依赖

```bash
pip install -r requirements.txt
```

#### 配置 `.env`

复制模板并按需修改：

```bash
cp .env.template .env
```

关键变量：

- `EMBEDDING_API_PROVIDER`：选择 Embedding 服务提供方式（`local` 或 `aliyun`）
  - `local`：使用本地 qwen3-vl-embedding-2B 模型（需要 16GB+ 内存）
  - `aliyun`：使用阿里云 DashScope qwen3-vl-embedding API 服务（推荐，无需本地模型）
- `ALIYUN_EMBEDDING_API_KEY`：阿里云 DashScope API Key（仅当 `EMBEDDING_API_PROVIDER=aliyun` 时需要）
- `ALIYUN_EMBEDDING_MODEL_NAME`：模型名称（默认 `qwen3-vl-embedding`）
- `ALIYUN_EMBEDDING_DIMENSION`：向量维度（支持 2560, 2048, 1536, 1024, 768, 512, 256，默认 2560）
- `OPENAI_API_KEY/OPENAI_BASE_URL/OPENAI_MODEL_NAME`：启用 Agent（OpenJiuwen / OpenAI兼容工具调用）时需要

#### 启动后端

推荐使用 factory 方式：

```bash
uvicorn app.main:create_app --reload --host 0.0.0.0 --port 8000
```

API 文档：

- Swagger: `http://localhost:8000/docs`

#### 2) 前端（React + Vite）

```bash
cd frontend
npm install
npm run dev
```

打开：`http://localhost:5173/`（已配置代理 `/api -> http://localhost:8000`）。

---

## Dockerfile vs Docker Compose

**理解它们的关系：**

| 工具 | 作用 | 类比 |
|------|------|------|
| **Dockerfile** | 定义单个镜像的构建步骤 | 单个菜品的菜谱 |
| **docker-compose.yml** | 编排多个容器协同工作 | 完整的菜单和上菜流程 |

**工作流程：**
```
1. Dockerfile → 构建镜像（定义应用环境）
2. docker-compose → 使用镜像 → 启动服务（配置端口、卷、网络）
```

**本项目包含：**
- `Dockerfile.user` - 用户版镜像构建文件
- `docker-compose.yml` - 服务编排配置
- `start-docker.sh/.bat` - 一键启动脚本

---

## 关键用法

### 1) 上传并索引

- 页面：`/upload`
- 接口：`POST /api/v1/storage/upload`（支持异步索引）

### 2) 对话找图（推荐入口）

- 页面：`/chat`
- 接口：`POST /api/v1/agent/chat`

对话返回结构包含 `results.images`，前端会自动展示缩略图：

```json
{
  "answer": "...",
  "results": {"total": 3, "images": [{"id": "...", "preview_url": "/api/v1/storage/images/..."}]}
}
```

### 3) 画廊语义检索

- 页面：`/gallery`
- 接口：`GET /api/v1/search/text?query=...&top_k=...`

## 测试

```bash
python -m unittest -q
```

## 常见问题

- **首次搜索/对话很慢**：首次加载 embedding 模型耗时较长；后续会明显加快。
- **OpenAI兼容接口报 400: you must provide a model parameter**：检查 `.env` 的 `OPENAI_MODEL_NAME` 是否为空。
- **对话/检索提示网络错误但后端有日志**：通常是前端超时取消（已在聊天请求中将超时适配为更长时间）。

## TODO LIST

- [x] 完善以图搜图功能，支持用户上传图片后，根据图片内容检索出相关图片；
- [x] 图像生成模型加入 pipeline，实现动漫风格生成；
- [x] 前端加入图像生成功能，用户上传图片后，生成动漫风格图片并索引；
- [x] 朋友圈文案生成功能，搜索出相关图片后，根据图片内容生成符合要求的文案；
- [x] 3DGS 模型加入 pipeline，实现 3D 模型生成；
- [x] 图像编辑功能，qwen3-image-edit 模型加入 pipeline，实现图像编辑功能；
