# 智慧相册（Smart Album）项目上下文

## 项目概述

智慧相册是一个"上传即索引、对话即找图"的多模态智能相册系统，实现了基于自然语言的图片搜索、以图搜图、图文混合检索等功能。项目采用前后端分离架构，集成了向量数据库、多模态大语言模型和ReAct智能体框架。

### 核心特性

- **多模态检索**：支持纯文本、纯图像、图文混合三种检索模式
- **自然语言对话**：通过ReAct智能体理解复杂查询意图
- **灵活日期解析**：支持"1.18"、"去年"、"上个月"等多种日期格式
- **组合检索**：支持语义+元数据+日期的多维度组合查询
- **图片编辑**：集成通义千问图像编辑模型，支持风格转换
- **3D生成**：支持点云生成（预留功能）

### 技术栈

**后端：**
- Python 3.11+、FastAPI、Pydantic v2
- Qdrant向量数据库（本地/Docker/云）
- Qwen3-VL多模态Embedding（本地推理/阿里云API）
- OpenJiuwen ReAct Agent框架
- OpenAI兼容API（通义千问/OpenAI）

**前端：**
- React 19.2.0 + TypeScript
- Vite构建工具
- Ant Design UI组件库
- Zustand状态管理
- React Router DOM路由

## 项目结构

```
ImgEmbedding2VecDB/
├── app/                        # 后端主应用
│   ├── main.py                 # FastAPI应用入口，服务初始化
│   ├── config.py               # 配置管理（Pydantic Settings）
│   ├── models/
│   │   └── schemas.py          # 数据模型定义（298行）
│   ├── routers/                # 路由层
│   │   ├── agent.py            # 智能体路由（901行）
│   │   ├── search.py           # 搜索路由（399行）
│   │   ├── storage.py          # 存储路由（486行）
│   │   ├── embedding.py        # Embedding路由
│   │   ├── vector_db.py        # 向量数据库路由
│   │   ├── social.py           # 社交媒体路由
│   │   ├── image_edit.py       # 图片编辑路由
│   │   ├── image_recommendation.py  # 图片推荐路由
│   │   └── pointcloud.py       # 点云生成路由
│   └── services/               # 服务层（单例模式）
│       ├── agent_service.py    # Agent服务（1247行）
│       ├── search_service.py   # 搜索服务（712行）
│       ├── vector_db_service.py    # 向量数据库服务（606行）
│       ├── embedding_service.py    # Embedding服务
│       ├── storage_service.py      # 存储服务
│       ├── aliyun_embedding_client.py  # 阿里云Embedding客户端
│       ├── image_edit_service.py     # 图片编辑服务
│       ├── image_recommendation_service.py  # 图片推荐服务
│       ├── social_service.py           # 社交服务
│       └── pointcloud_service.py       # 点云生成服务
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── api/                # API客户端层
│   │   │   ├── client.ts       # Axios实例配置
│   │   │   ├── agent.ts        # Agent API
│   │   │   ├── search.ts       # 搜索API
│   │   │   ├── storage.ts      # 存储API
│   │   │   ├── social.ts       # 社交API
│   │   │   ├── image_edit.ts   # 图片编辑API
│   │   │   └── types.ts        # TypeScript类型定义
│   │   ├── components/         # 共享组件
│   │   │   ├── common/         # 通用组件（EmptyState、LoadingSpinner等）
│   │   │   ├── gallery/        # 画廊组件（ImageCard）
│   │   │   ├── layout/         # 布局组件（MainLayout）
│   │   │   └── search/         # 搜索组件（SearchBox、ImageSearchModal）
│   │   ├── pages/              # 页面组件
│   │   │   ├── HomePage.tsx    # 首页
│   │   │   ├── ChatPage.tsx    # 智能对话页面
│   │   │   ├── GalleryPage.tsx # 图片画廊页面
│   │   │   ├── UploadPage.tsx  # 图片上传页面
│   │   │   └── ArchitecturePage.tsx  # 架构说明页面
│   │   └── store/              # 状态管理
│   │       ├── chatStore.ts    # 聊天状态管理
│   │       └── themeStore.ts   # 主题状态管理
│   └── package.json            # 前端依赖配置
├── storage/                    # 图片存储目录
├── qdrant_data/                # Qdrant本地数据
├── requirements.txt            # Python依赖
├── .env.template              # 环境变量模板
├── README.md                  # 项目说明
├── 技术报告.md                 # 详细技术报告
└── AGENTS.md                  # 本文件
```

## 构建和运行

### 后端（FastAPI）

#### 环境要求
- Python 3.10+
- 16GB+ 内存（本地模型模式）
- 可选：CUDA 或 Apple Silicon（MPS）加速

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 配置环境变量
```bash
cp .env.template .env
# 编辑 .env 文件，配置必要参数
```

**关键配置项：**
- `EMBEDDING_API_PROVIDER`: 选择 Embedding 服务（`local` 或 `aliyun`）
  - `local`: 使用本地 Qwen3-VL-Embedding-2B 模型（需要16GB+内存）
  - `aliyun`: 使用阿里云 DashScope API（推荐）
- `ALIYUN_EMBEDDING_API_KEY`: 阿里云 API Key
- `ALIYUN_EMBEDDING_DIMENSION`: 向量维度（2560/2048/1536/1024/768/512/256）
- `QDRANT_MODE`: Qdrant部署模式（`local`/`docker`/`cloud`）
- `OPENAI_API_KEY`: Agent功能的API Key（通义千问或OpenAI）
- `OPENAI_BASE_URL`: API基础URL（通义千问：`https://dashscope.aliyuncs.com/compatible-mode/v1`）
- `OPENAI_MODEL_NAME`: 模型名称（如 `qwen3-max`）

#### 启动后端
```bash
# 开发模式（带热重载）
uvicorn app.main:create_app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:create_app --host 0.0.0.0 --port 8000 --workers 4
```

**API文档：**
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 前端（React）

#### 安装依赖
```bash
cd frontend
npm install
```

#### 启动开发服务器
```bash
npm run dev
```
访问：`http://localhost:5173/`

#### 构建生产版本
```bash
npm run build
npm run preview
```

### 测试
```bash
# 后端测试
python -m unittest -q

# 前端测试
cd frontend
npm run test
```

## 开发约定

### 后端开发规范

1. **架构模式**：采用分层架构（Router → Service → Data），使用依赖注入
2. **单例模式**：所有服务类使用单例模式，通过 `get_xxx_service()` 获取实例
3. **异步编程**：所有I/O操作使用 `async/await`，充分利用FastAPI的异步特性
4. **类型注解**：使用 Pydantic 模型定义所有请求/响应数据，提供完整类型提示
5. **错误处理**：使用全局异常处理器统一处理错误，返回标准化错误响应
6. **日志记录**：使用 Python `logging` 模块，结构化日志格式
7. **环境变量**：所有配置通过环境变量管理，使用 `pydantic-settings` 加载

### 前端开发规范

1. **组件结构**：组件按功能分类（common/gallery/layout/search/pages）
2. **状态管理**：使用 Zustand 管理全局状态（chatStore、themeStore）
3. **API调用**：统一使用 Axios，配置拦截器处理错误和超时
4. **TypeScript**：所有文件使用 TypeScript，定义清晰的接口类型
5. **样式方案**：使用 Ant Design 组件库 + Tailwind CSS
6. **路由管理**：使用 React Router DOM v7，采用声明式路由

### 代码风格

- **命名约定**：
  - Python: snake_case（函数/变量）、PascalCase（类）
  - TypeScript: camelCase（变量/函数）、PascalCase（类/组件）
- **注释规范**：中文注释，解释"为什么"而非"是什么"
- **导入顺序**：标准库 → 第三方库 → 本地模块
- **文件大小**：单个文件控制在1000行以内，超出考虑拆分

### Git提交规范

- 提交信息格式：`<type>(<scope>): <subject>`
  - `type`: feat/fix/docs/style/refactor/test/chore
  - `scope`: 模块名称（如 backend/frontend/agent）
  - `subject`: 简短描述（中文）
- 示例：`feat(agent): 新增图片推荐工具`

## 核心API端点

### 智能体（Agent）
- `POST /api/v1/agent/chat` - 智能对话（核心入口）
- `POST /api/v1/agent/session/create` - 创建会话
- `POST /api/v1/agent/recommendation/delete` - 根据推荐删除图片

### 搜索（Search）
- `POST /api/v1/search` - 统一搜索接口
- `GET /api/v1/search/text` - 文本语义搜索
- `POST /api/v1/search/image` - 上传图片搜索
- `GET /api/v1/search/image/{image_id}` - 按图片ID搜索
- `POST /api/v1/search/hybrid` - 图文混合搜索
- `GET /api/v1/search/meta` - 元数据搜索

### 存储（Storage）
- `POST /api/v1/storage/upload` - 上传图片（支持自动索引）
- `GET /api/v1/storage/images/{image_id}` - 获取图片
- `DELETE /api/v1/storage/images/{image_id}` - 删除图片
- `GET /api/v1/storage/images` - 列出所有图片

### 图片编辑（Image Edit）
- `POST /api/v1/image-edit/edit` - 图片风格编辑

### 社交（Social）
- `POST /api/v1/social/caption` - 生成朋友圈文案

### 图片推荐（Image Recommendation）
- `POST /api/v1/image-recommendation/recommend` - 智能图片推荐

### 点云生成（Pointcloud）
- `POST /api/v1/pointcloud/generate` - 生成3D点云模型

### 系统状态（System）
- `GET /` - API根路由
- `GET /health` - 健康检查
- `GET /status` - 系统状态（包括图片/向量数量）

## 数据模型

### 向量维度配置

**Qwen3-VL-Embedding 模型：**
- 本地模型：2560维
- 阿里云API：支持 2560/2048/1536/1024/768/512/256 维

### 图片元数据（ImageMetadata）
```python
{
    "id": "uuid",
    "filename": "original.jpg",
    "file_path": "storage/images/2026/01/26/uuid.jpg",
    "width": 1920,
    "height": 1080,
    "format": "JPEG",
    "created_at": "2026-01-26T10:00:00",
    "tags": ["海边", "日落"],
    "description": "海边日落照片"
}
```

### 搜索响应（SearchResponse）
```python
{
    "results": [
        {
            "id": "uuid",
            "score": 0.95,
            "metadata": {...},
            "preview_url": "/api/v1/storage/images/uuid"
        }
    ],
    "total": 10,
    "query_type": "text"
}
```

### Agent对话响应（ChatResponse）
```python
{
    "answer": "我为您找到了10张红色跑车的照片...",
    "images": [
        "/api/v1/storage/images/uuid1",
        "/api/v1/storage/images/uuid2"
    ],
    "recommendation": {
        "image_ids": ["uuid3", "uuid4"],
        "reason": "基于您的搜索结果推荐"
    }
}
```

## 关键技术实现

### 1. 多模态Embedding

**模型：** Qwen3-VL-Embedding-2B
- **向量维度：** 2560
- **输入类型：** 文本、图像、图文混合
- **指令工程：**
  - 文本检索：`"Represent this text for retrieval."`
  - 图像检索：`"Represent this image for retrieval."`
  - 多模态：融合文本和图像的联合表示

**部署方式：**
- 本地推理：使用Transformers库（需要16GB+内存）
- 阿里云API：通过DashScope SDK调用（推荐）

### 2. 向量数据库（Qdrant）

**索引策略：**
- HNSW索引：用于高效近似最近邻搜索
- Payload索引：
  - `tags`（keyword类型）：用于标签过滤
  - `created_at`（datetime类型）：用于日期范围过滤

**查询方法：**
- 使用最新API `query_points()`（已废弃 `search()`）
- 支持余弦相似度（COSINE）距离度量
- 支持payload过滤和组合查询

### 3. ReAct智能体

**框架：** OpenJiuwen ReActAgent
**配置：**
```python
ReActAgentConfig(
    model=ModelConfig(
        base_url=settings.OPENAI_BASE_URL,
        api_key=settings.OPENAI_API_KEY,
        model_name=settings.OPENAI_MODEL_NAME
    ),
    constrain=ConstrainConfig(
        max_iteration=6  # 最大迭代次数
    )
)
```

**注册工具：**
1. `semantic_search_images` - 语义搜索
2. `search_by_image_id` - 按ID搜索
3. `meta_search_images` - 元数据搜索
4. `meta_search_hybrid` - 元数据+语义组合
5. `agent_execute_action` - 执行操作
6. `get_current_time` - 获取当前时间
7. `get_photo_meta_schema` - 获取元数据字段定义
8. `generate_social_media_caption` - 生成朋友圈文案
9. `recommend_images` - 智能图片推荐

**会话管理：**
- 使用 `_sessions` 字典存储会话状态
- 使用 `ContextVar` 管理当前对话ID
- 不同会话完全隔离，避免状态污染

### 4. 日期解析

**支持的格式：**
- `1.18` → 当前年份1月18日
- `1月18日` → 当前年份1月18日
- `2026-01-18` → 精确日期
- `去年` → 2025年（2025-01-01 至 2025-12-31）
- `上个月` → 上个月的日期范围

**实现方式：**
- 正则匹配 `r"(\d{1,2})\.(\d{1,2})"` 匹配 "M.D" 格式
- 使用 `datetime.strptime()` 解析多种ISO格式
- 计算当前时间并推导相对日期范围

### 5. 安全性设计

**文件命名：**
- 使用UUID自动生成，禁止外部指定
- 避免路径遍历攻击

**输入验证：**
- 扩展名白名单：`{jpg, jpeg, png, gif, webp, bmp}`
- 文件大小限制：50MB

**会话隔离：**
- 不同会话的上下文完全隔离
- 使用 `ContextVar` 确保线程安全

## 常见问题

### 1. 首次搜索/对话很慢
**原因：** 首次加载embedding模型耗时较长
**解决：** 后续请求会明显加快；推荐使用阿里云API模式

### 2. OpenAI兼容接口报错 "you must provide a model parameter"
**原因：** `.env` 中 `OPENAI_MODEL_NAME` 为空
**解决：** 设置 `OPENAI_MODEL_NAME=qwen3-max`（或其它模型）

### 3. 对话/检索提示网络错误但后端有日志
**原因：** 前端请求超时（默认120秒）
**解决：** 前端已配置更长超时，复杂查询可能需要更长时间

### 4. 向量维度不匹配
**原因：** 本地模型（2560维）与阿里云API配置不一致
**解决：** 确保 `.env` 中 `ALIYUN_EMBEDDING_DIMENSION=2560`

### 5. Qdrant连接失败
**原因：** Qdrant服务未启动或端口配置错误
**解决：**
- 本地模式：检查 `qdrant_data/` 目录权限
- Docker模式：`docker run -p 6333:6333 qdrant/qdrant`
- 云模式：检查 `QDRANT_HOST`、`QDRANT_PORT`、`QDRANT_API_KEY`

## 扩展功能

### 已实现
- ✅ 多模态Embedding（文本/图像/图文混合）
- ✅ 语义检索、以图搜图、图文混合检索
- ✅ ReAct智能体对话
- ✅ 灵活日期解析
- ✅ 组合检索（语义+元数据+日期）
- ✅ 图片风格编辑（通义千问图像编辑）
- ✅ 社交媒体文案生成
- ✅ 智能图片推荐

### 开发中（TODO）
- ⏳ 以图搜图功能完善
- ⏳ 图像生成模型（动漫风格）
- ⏳ 前端图像生成功能
- ⏳ 朋友圈文案生成完善
- ⏳ 3DGS模型生成
- ⏳ 图像编辑功能完善

## 性能优化建议

1. **向量索引：** 为高频过滤字段创建payload索引
2. **批量处理：** 批量生成embedding和插入向量
3. **缓存策略：** 缓存常见文本的embedding向量
4. **异步I/O：** 使用 `asyncio.create_task()` 执行后台任务
5. **并发请求：** 前端使用 `AbortController` 处理超时和取消

## 参考资源

- **Qdrant文档：** https://qdrant.tech/documentation/
- **ReAct Prompting：** https://www.promptingguide.ai/techniques/react
- **FastAPI文档：** https://fastapi.tiangolo.com/
- **React 19文档：** https://react.dev/blog/2024/12/05/react-19
- **OpenJiuwen：** https://github.com/openjiuwen/openjiuwen
- **通义千问API：** https://help.aliyun.com/zh/dashscope/

## 项目特色

1. **创新交互范式：** "对话即找图"降低使用门槛
2. **多模态融合：** 统一向量空间支持文本、图像、混合检索
3. **灵活日期解析：** 支持多种格式和相对时间表达
4. **组合检索能力：** 语义、元数据、日期等多维度组合
5. **智能图片推荐：** 基于意图的主动推荐
6. **单例模式：** 避免重复初始化，资源共享
7. **类型安全：** Pydantic + TypeScript提供完整类型保障
8. **异步优化：** 充分利用FastAPI异步特性
9. **安全性设计：** UUID命名、输入验证、会话隔离
10. **分层架构：** 高内聚低耦合，易于维护扩展