import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Card, theme, FloatButton } from 'antd';

const markdownContent = `
# 🏗️ 智慧相册产品架构设计方案

## 1. 系统概览 🌟

智慧相册是一个**基于多模态 AI 技术的智能图片管理平台**,实现了"上传即索引、对话即找图"的创新交互模式。系统采用前后端分离架构，集成了向量数据库、大语言模型和智能体框架，为用户提供语义检索、以图搜图、智能对话等多种功能。

### 1.1 核心定位
- **产品定位**: 多模态智能相册系统
- **核心价值**: 通过自然语言对话实现图片的精准检索和管理
- **技术特色**: 融合向量搜索、ReAct 智能体、多模态 Embedding

### 1.2 主要功能
- ✅ **语义检索**: 基于自然语言的图片搜索
- ✅ **以图搜图**: 通过相似度查找相似图片
- ✅ **图文混合搜索**: 结合文本和图片的多模态检索
- ✅ **元数据检索**: 基于日期、标签的结构化过滤
- ✅ **智能对话**: 通过自然语言交互完成复杂查询
- ✅ **图像编辑**: 基于 AI 的图片风格转换
- ✅ **社交媒体文案生成**: 自动生成朋友圈配文
- ✅ **智能图片推荐**: 基于用户意图的图片推荐

\`\`\`
┌─────────────────────────────────────────────────────────────────────────┐
│                           用户层 (User Layer)                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │   智能相册用户     │  │   管理员用户      │  │   API 调用方      │     │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘     │
└───────────┼──────────────────────┼──────────────────────┼──────────────┘
            └──────────────────────┼──────────────────────┘
                                   ↓
┌──────────────────────────────────┼──────────────────────────────────────┐
│                          前端层 (Frontend Layer)                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    React 19.2.0 应用                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │ UnifiedHome  │  │ GalleryPage  │  │ UploadPage   │          │   │
│  │  │  (统一首页)   │  │  (图片画廊)   │  │  (图片上传)   │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  │  ┌──────────────┐  ┌──────────────┐                            │   │
│  │  │Conversations │  │ Architecture │                            │   │
│  │  │ (对话历史)    │  │   (产品架构)  │                            │   │
│  │  └──────────────┘  └──────────────┘                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              状态管理层 (Zustand + IndexedDB)                     │   │
│  │  - unifiedStore: 搜索状态、topK、搜索结果                         │   │
│  │  - chatStore: 对话消息、会话状态                                  │   │
│  │  - conversationStore: 对话历史 (IndexedDB 持久化)                  │   │
│  │  - themeStore: 主题模式 (亮/暗)                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                  API 客户端层 (Axios)                             │   │
│  │  - baseURL: /api/v1, timeout: 600s                               │   │
│  │  - 拦截器：请求/响应错误处理、超时取消、重试逻辑                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │ HTTP/HTTPS (RESTful API)
┌──────────────────────────────────▼──────────────────────────────────────┐
│                          后端层 (Backend Layer)                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   FastAPI 应用 (main.py)                          │   │
│  │  - Lifespan 管理：初始化所有服务                                   │   │
│  │  - 路由注册：8 个路由模块                                          │   │
│  │  - 中间件：全局异常处理、请求日志                                  │   │
│  │  - 端点：/status, /health                                        │   │
│  └────────────────────────────┬────────────────────────────────────┘   │
│                               │                                         │
│  ┌────────────────────────────┼────────────────────────────────────┐   │
│  │                            ↓                                      │   │
│  │  ┌───────────────────────────────────────────────────────────┐  │   │
│  │  │                    路由层 (Routers)                        │  │   │
│  │  │  - agent.py (901 行): /agent/chat, /agent/session/*        │  │   │
│  │  │  - search.py (399 行): /search/*                           │  │   │
│  │  │  - storage.py (486 行): /storage/*                         │  │   │
│  │  │  - social.py: /social/caption                              │  │   │
│  │  │  - image_edit.py: /image-edit/edit                         │  │   │
│  │  │  - image_recommendation.py: /image-recommendation/recommend│  │   │
│  │  │  - asr.py: /asr/realtime (WebSocket)                       │  │   │
│  │  │  - pointcloud.py: /pointcloud/generate                     │  │   │
│  │  └───────────────────────────────────────────────────────────┘  │   │
│  └────────────────────────────┬────────────────────────────────────┘   │
│                               │                                         │
│  ┌────────────────────────────▼────────────────────────────────────┐   │
│  │                   服务层 (Services - 单例模式)                     │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │ EmbeddingService (单例)                                  │   │   │
│  │  │  - Qwen3-VL-Embedding-2B (2560 维)                        │   │   │
│  │  │  - 支持本地推理 + 阿里云 DashScope API                       │   │   │
│  │  │  - 指令："Represent this text/image for retrieval."      │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │ VectorDBService (单例)                                   │   │   │
│  │  │  - Qdrant 客户端 (本地/Docker/云)                          │   │   │
│  │  │  - COSINE 距离，query_points() 方法                        │   │   │
│  │  │  - payload 索引：tags(关键词), created_at(日期)             │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │ SearchService (单例)                                     │   │   │
│  │  │  - search_by_text: 语义搜索                               │   │   │
│  │  │  - search_by_date_text: 日期解析 (1.18, 1 月 18 日，2026-01-18)│   │   │
│  │  │  - search_by_meta: 元数据检索                             │   │   │
│  │  │  - search_by_text_with_meta: 组合检索                     │   │   │
│  │  │  - search_by_image: 图像相似度搜索                        │   │   │
│  │  │  - search_hybrid: 图文混合检索                            │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │ AgentService (单例)                                      │   │   │
│  │  │  - Openjiuwen ReActAgent 集成                             │   │   │
│  │  │  - 9 个工具：semantic_search, search_by_image, meta_search │   │   │
│  │  │  - ConstrainConfig(max_iteration=6)                       │   │   │
│  │  │  - 会话管理：_sessions[session_id]                        │   │   │
│  │  │  - ContextVar: current_conversation_id                    │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │ StorageService (单例)                                    │   │   │
│  │  │  - 本地文件系统存储 (按日期分层：YYYY/MM/DD)               │   │   │
│  │  │  - UUID 命名 (安全性设计)                                  │   │   │
│  │  │  - 支持格式：jpg, jpeg, png, gif, webp, bmp               │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────┬────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────┐
│                        智能体层 (Agent Layer)                          │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │               Openjiuwen ReAct Agent                           │   │
│  │  - ReActAgentConfig: ModelConfig + ConstrainConfig            │   │
│  │  - System Prompt: 人设 + 任务目标 + 当前日期 + 约束限制         │   │
│  │  - ReAct 循环：Thought → Action → Observation → Thought ...   │   │
│  │  - 工具注册 (9 个工具):                                         │   │
│  │    1. semantic_search_images (语义搜索)                        │   │
│  │    2. search_by_image_id (按 ID 搜索)                           │   │
│  │    3. meta_search_images (元数据搜索)                          │   │
│  │    4. meta_search_hybrid (元数据 + 语义组合)                    │   │
│  │    5. agent_execute_action (执行操作)                          │   │
│  │    6. get_current_time (获取当前时间)                          │   │
│  │    7. get_photo_meta_schema (获取元数据字段定义)               │   │
│  │    8. generate_social_media_caption (朋友圈文案生成)          │   │
│  │    9. recommend_images (智能图片推荐)                          │   │
│  └───────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────┬────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────┐
│                         数据层 (Data Layer)                            │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                  Qdrant 向量数据库                              │   │
│  │  - Collection: image_embeddings                                │   │
│  │  - Vector: 2560 维 (Qwen3-VL-Embedding-2B)                     │   │
│  │  - Distance: COSINE                                            │   │
│  │  - Payload: ImageMetadata (id, filename, file_path, tags,     │   │
│  │           description, created_at, width, height, format)      │   │
│  │  - Payload Indexes:                                            │   │
│  │    * tags (keyword type) - 用于标签过滤                         │   │
│  │    * created_at (datetime type) - 用于日期范围过滤              │   │
│  │  - 查询方式：query_points() with filters                       │   │
│  └───────────────────────────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                  本地文件存储 (Storage)                        │   │
│  │  - 路径结构：./storage/YYYY/MM/DD/{uuid}.{ext}                │   │
│  │  - 示例：./storage/2026/01/26/a1b2c3d4-....jpg                │   │
│  └───────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────┬────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────┐
│                  基础设施/部署层 (Infrastructure Layer)                │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                  配置管理 (config.py)                          │   │
│  │  - Pydantic Settings                                          │   │
│  │  - EMBEDDING_API_PROVIDER: local/aliyun                       │   │
│  │  - VECTOR_DIMENSION: 2560                                     │   │
│  │  - QDRANT_MODE: local/docker/cloud                             │   │
│  │  - OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL_NAME          │   │
│  │  - ALIYUN_EMBEDDING_API_KEY, ALIYUN_EMBEDDING_MODEL_NAME       │   │
│  └───────────────────────────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                  数据模型 (models/schemas.py)                   │   │
│  │  - 298 行完整定义                                                │   │
│  │  - ImageMetadata, VectorRecord, SearchRequest/Response        │   │
│  │  - ChatRequest/Response, ImageRecommendation                  │   │
│  └───────────────────────────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                  外部服务                                      │   │
│  │  - 阿里云 DashScope (Embedding)                               │   │
│  │  - OpenAI 兼容 API 服务 (LLM/Agent)                             │   │
│  │  - Qdrant 云服务 (可选)                                         │   │
│  └───────────────────────────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                  部署模式                                      │   │
│  │  - 本地开发 (单机)                                             │   │
│  │  - Docker 部署 (容器化)                                         │   │
│  │  - 云服务部署 (可扩展)                                         │   │
│  └───────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────┘
\`\`\`

## 2. 前端架构 (Frontend) 🎨

### 2.1 核心技术栈详解

⚛️ **React 19.2.0**: 采用最新版本的 React 框架，引入了 useOptimistic、useActionState 等新特性，优化了异步 UI 状态管理。

📘 **TypeScript**: 全项目采用严格模式，通过静态类型检查确保组件 Props 和 API 响应数据的类型安全，大幅降低运行时错误。

🎨 **Ant Design 6.2.0**: 企业级 UI 组件库，提供丰富的组件和设计规范，基于 Design Token 的 CSS-in-JS 动态主题系统。

🌀 **Zustand 5.0.10**: 轻量级状态管理库，用于管理聊天会话状态、统一状态、主题状态等。

⚡ **Vite**: 高性能的构建工具，提供快速的开发体验和热模块替换 (HMR)。

🛣️ **React Router DOM 7.12.0**: 管理前端路由和导航，支持 URL 参数管理和浏览器历史。

📦 **Yet Another React Lightbox**: 图片预览组件，支持缩放、旋转等功能。

📝 **React Markdown**: Markdown 渲染组件，用于展示 AI 回复中的格式化内容。

🎨 **Tailwind CSS 4**: 实用优先的 CSS 框架，提供灵活的样式定制能力。

### 2.2 核心模块

📐 **Layout**: 响应式侧边栏布局，支持深色模式切换和侧边栏折叠。

📄 **Pages**:
  - 🏠 \`UnifiedHomePage\`: 统一首页，集成搜索、对话、搜索结果三种模式 (通过 ModeSwitcher 切换)
  - 💬 \`ChatPage\`: 智能对话界面 (已合并到 UnifiedHomePage)
  - 🖼️ \`GalleryPage\`: 图片瀑布流展示，支持无限滚动和网格/列表视图切换
  - 📤 \`UploadPage\`: 图片上传，支持拖拽和批量上传
  - 📚 \`ConversationListPage\`: 对话历史列表页面
  - 🏛️ \`ArchitecturePage\`: 产品架构说明页面

🗄️ **Store**:
  - 💭 \`chatStore\`: 管理对话消息、会话状态、加载状态
  - 🔄 \`unifiedStore\`: 管理搜索词、topK、搜索结果、最后搜索查询
  - 📚 \`conversationStore\`: 管理对话历史 (IndexedDB 持久化)
  - 🎙️ \`voiceStore\`: 管理语音识别状态（连接、录音、转录等）
  - 🌓 \`themeStore\`: 管理主题模式 (亮/暗)

### 2.3 数据流设计

\`\`\`
用户交互 👆 
    ↓
组件触发 Action 🔄
    ↓
Store 更新状态 / API 调用 🔧
    ↓
后端响应 📡
    ↓
Store 更新 💾
    ↓
UI 重新渲染 🎨
\`\`\`

### 2.4 前端项目结构

\`\`\`
frontend/src/
├── api/              # API 客户端层
│   ├── client.ts     # Axios 实例配置
│   ├── agent.ts      # 智能体相关 API
│   ├── search.ts     # 搜索相关 API
│   ├── storage.ts    # 存储相关 API
│   ├── social.ts     # 社交媒体 API
│   ├── image_edit.ts # 图片编辑 API
│   ├── voiceService.ts # 语音识别服务（WebSocket）
│   └── types.ts      # TypeScript 类型定义
├── components/       # 共享组件
│   ├── common/       # 通用组件
│   │   ├── AudioWaveform.tsx  # 语音波形可视化
│   │   ├── VoiceInput.tsx     # 语音输入组件
│   │   ├── EmptyState.tsx      # 空状态提示
│   │   ├── LoadingSpinner.tsx  # 加载动画
│   │   ├── MarkdownRenderer.tsx # Markdown 渲染器
│   │   ├── TypewriterEffect.tsx # 打字机效果
│   │   └── ScaledImage.tsx     # 缩放图片组件
│   ├── gallery/      # 画廊组件
│   │   └── ImageCard.tsx
│   ├── layout/       # 布局组件
│   │   └── MainLayout.tsx
│   ├── search/       # 搜索组件
│   │   ├── SearchBox.tsx
│   │   └── ImageSearchModal.tsx
│   ├── unified/      # 统一页面组件
│   │   ├── HomePageView.tsx    # 首页视图
│   │   ├── ChatView.tsx        # 对话视图
│   │   ├── SearchResultsView.tsx # 搜索结果视图
│   │   ├── ModeSwitcher.tsx    # 模式切换器
│   │   └── VirtualImageGrid.tsx # 虚拟滚动图片网格
│   ├── chat/         # 聊天组件
│   │   └── InputBubble.tsx
│   └── conversation/ # 对话历史组件
│       └── ConversationHistory.tsx
├── pages/            # 页面组件
│   ├── UnifiedHomePage.tsx    # 统一首页（包含三种模式）
│   ├── ChatPage.tsx           # 智能对话页面（已合并到UnifiedHomePage）
│   ├── GalleryPage.tsx        # 图片画廊页面
│   ├── UploadPage.tsx         # 图片上传页面
│   ├── ConversationListPage.tsx # 对话历史列表页面
│   └── ArchitecturePage.tsx   # 产品架构页面
├── store/            # 状态管理
│   ├── chatStore.ts
│   ├── unifiedStore.ts
│   ├── conversationStore.ts
│   ├── voiceStore.ts
│   └── themeStore.ts
├── hooks/            # 自定义 Hooks
│   ├── useDebounce.ts                # 防抖 Hook
│   ├── usePerformanceMonitor.ts       # 性能监控 Hook
│   ├── useUnifiedDataFlow.ts         # 统一数据流 Hook
│   └── useUnifiedDataPersistence.ts  # 数据持久化 Hook
├── services/         # 服务层
│   └── conversationStorage.ts  # IndexedDB 对话历史存储服务
├── types/            # 类型定义
│   └── conversation.ts       # 对话相关类型
└── App.tsx           # 主应用组件
\`\`\`

## 3. 后端架构 (Backend) ⚙️

### 3.1 核心服务技术详解

🚀 **FastAPI**: 现代化的异步 Web 框架，基于 Python 3.8+。自动生成 OpenAPI 文档，内置依赖注入系统，原生支持异步编程。

🧠 **Qwen3-VL (多模态大模型)**: 
  - 🔍 **核心能力**: 能够同时理解文本和图像输入的视觉语言模型。
  - 🎯 **应用场景**: 用于生成图片的高维语义向量 (Embedding),以及理解用户的复杂自然语言查询意图。
  - 📏 **向量维度**: 2560 维

💎 **Qdrant (向量数据库)**:
  - 💾 **存储引擎**: 专为向量搜索优化的数据库，支持 HNSW(Hierarchical Navigable Small World) 算法，实现亿级数据的毫秒级检索。
  - 🔀 **混合检索**: 支持 Vector Search(语义相似度) 与 Payload Filter(元数据过滤) 的组合查询。
  - 📊 **查询方法**: 使用 query_points() 方法 (替代已废弃的 search() 方法)

🛡️ **Pydantic v2**: 强大的数据验证库，确保进入系统的数据符合预定义的 Schema，自动处理类型转换和错误提示。

🔥 **Uvicorn**: 基于 uvloop 的高性能 ASGI 服务器，作为 FastAPI 的生产级运行容器。

🤖 **Openjiuwen ReAct Agent**: 智能体框架，通过"思考 - 行动 - 观察"的循环逐步完成复杂查询。

### 3.2 业务分层架构

🌐 **Routers (API 层)**: 处理 HTTP 请求，参数校验 (\`app/routers\`).

💼 **Services (业务层)**: 核心业务逻辑封装 (\`app/services\`).
  - 🔢 \`EmbeddingService\`: 调用本地模型或阿里云 API 生成向量。
  - 🗃️ \`VectorDBService\`: 封装 Qdrant 数据库操作。
  - 📁 \`StorageService\`: 管理本地文件存储。
  - 🔍 \`SearchService\`: 整合搜索逻辑 (文本/图片/混合/元数据)。
  - 🤖 \`AgentService\`: 处理自然语言意图识别与对话。
  - 🎙️ \`AsrService\`: 处理实时语音识别 (WebSocket)。
  - 🎨 \`ImageEditService\`: 处理图片编辑功能。
  - 💡 \`ImageRecommendationService\`: 处理智能图片推荐。
  - 📱 \`SocialService\`: 处理社交媒体文案生成。
  - 🌐 \`PointcloudService\`: 处理 3D 点云生成。

📊 **Models (数据层)**: Pydantic 数据模型定义 (\`app/models\`).

### 3.3 核心组件交互

**📤 上传流程**:
\`\`\`
API → StorageService (保存文件 📥) 
    → EmbeddingService (生成向量 🔢) 
    → VectorDBService (存入 Qdrant 💾)
    → 返回结果 ✅
\`\`\`

**🔍 搜索流程**:
\`\`\`
API → EmbeddingService (Query 向量化 🔢) 
    → VectorDBService (相似度检索 🔍) 
    → StorageService (获取图片信息 📥) 
    → 返回结果 ✅
\`\`\`

**💬 智能对话流程**:
\`\`\`
用户："查找去年的海边照片"
    ↓
POST /api/v1/agent/chat
    ↓
AgentService.chat()
    ↓
ReAct Agent 推理过程:
┌─────────────────────────────────┐
│ Iteration 1:                    │
│ Thought: 需要确定"去年"的时间范围 │
│ Action: get_current_time()      │
│ Observation: 2026-01-26         │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ Iteration 2:                    │
│ Thought: "去年"是 2025 年，需要按日期 │
│         和关键词搜索           │
│ Action: meta_search_hybrid(     │
│   text="海边",                  │
│   start_date="2025-01-01",     │
│   end_date="2025-12-31"        │
│ )                               │
│ Observation: 返回 15 张海边照片  │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ Iteration 3:                    │
│ Thought: 已有足够信息，生成回答 │
│ Final Answer: "我为您找到了 15 张 │
│             去年的海边照片..." │
└─────────────────────────────────┘
    ↓
提取 images 和 recommendation
    ↓
返回 ChatResponse
    ↓
前端：ChatPage 渲染消息
\`\`\`

### 3.4 数据存储方案

- **结构化数据 & 向量数据**: Qdrant (存储 Image ID, Embedding, Tags, Metadata) 💎
- **非结构化数据 (图片)**: 本地文件系统 (\`storage/images\`) 📁
- **对话历史**: IndexedDB (前端浏览器本地存储) 💾

### 3.5 后端项目结构

\`\`\`
app/
├── main.py                 # FastAPI 应用主入口
├── config.py               # 配置管理 (Pydantic Settings)
├── models/
│   └── schemas.py          # 数据模型定义 (298 行)
├── routers/                # 路由层
│   ├── agent.py            # 智能体路由 (901 行)
│   ├── search.py           # 搜索路由 (399 行)
│   ├── storage.py          # 存储路由 (486 行)
│   ├── embedding.py        # Embedding 路由
│   ├── vector_db.py        # 向量数据库路由
│   ├── asr.py              # 语音识别路由 (WebSocket)
│   ├── social.py           # 社交媒体路由
│   ├── image_edit.py       # 图片编辑路由
│   ├── image_recommendation.py  # 图片推荐路由
│   └── pointcloud.py       # 点云生成路由
└── services/               # 服务层 (单例模式)
    ├── agent_service.py    # Agent 服务 (1247 行)
    ├── search_service.py   # 搜索服务 (712 行)
    ├── vector_db_service.py    # 向量数据库服务 (606 行)
    ├── embedding_service.py    # Embedding 服务
    ├── storage_service.py      # 存储服务
    ├── asr_service.py          # 语音识别服务 (DashScope SDK)
    ├── aliyun_embedding_client.py  # 阿里云 Embedding 客户端
    ├── image_edit_service.py     # 图片编辑服务
    ├── image_recommendation_service.py  # 图片推荐服务
    ├── social_service.py           # 社交服务
    └── pointcloud_service.py       # 点云生成服务
\`\`\`

## 4. 关键技术亮点 ✨

### 4.1 多模态融合架构
- 🎨 **统一的向量空间**: 使用 Qwen3-VL 多模态 Embedding 模型，将文本和图像映射到同一向量空间
- 🔀 **跨模态检索**: 支持"用文本搜图片"、"用图片搜图片"、"图文混合搜图片"三种模式
- 🤖 **智能体理解**: ReAct Agent 能够理解模糊、复杂的自然语言查询，自动分解为多个工具调用

### 4.2 "对话即找图"交互范式
- 💭 **ReAct 推理**: 智能体通过"思考 - 行动 - 观察"的循环逐步完成复杂查询
- 🛠️ **工具编排**: 智能体能够组合多个工具 (搜索、过滤、推荐) 完成复合任务
- 📚 **上下文记忆**: 支持多轮对话，智能体能够理解上下文中的指代关系

### 4.3 灵活的日期解析与检索
- 📅 **多格式支持**: M.D、M 月 D 日、YYYY-MM-DD 等多种格式
- ⏰ **相对时间**: 支持"去年"、"上个月"、"最近一周"等相对表达
- 🧠 **智能推导**: 根据当前时间自动推导相对时间范围

### 4.4 组合检索能力
- 📊 **Payload 索引**: 为 tags 和 created_at 创建索引，支持高效过滤
- 🔀 **组合查询**: search_by_text_with_meta 结合语义和元数据
- 🎯 **灵活过滤**: 支持 tags 过滤、日期范围过滤、ID 过滤等多种条件

### 4.5 智能图片推荐
- 💡 **意图理解**: ReAct Agent 分析用户的潜在意图
- 📏 **相似度计算**: 基于向量相似度推荐相关图片
- 🎨 **多维度推荐**: 考虑语义、视觉特征、元数据等多个维度

### 4.6 技术架构优势
- 🔒 **类型安全**: TypeScript + Pydantic 双重保障，减少运行时错误
- ⚡ **异步处理**: 全异步端点，图片上传与索引过程解耦，提升响应速度
- 🎯 **精准检索**: HNSW 算法 + Payload 过滤，实现高效混合检索
- 🌓 **主题切换**: 动态 Design Token 系统，支持亮/暗主题无缝切换
- 🏗️ **单例模式**: 所有服务类采用单例模式，避免重复初始化和资源浪费
- 💉 **依赖注入**: FastAPI 的 Depends 机制实现服务依赖管理
- 🔐 **安全性设计**: UUID 命名、输入验证、会话隔离等多层安全机制

## 5. 部署架构 🚀

### 5.1 部署模式

**本地开发模式**:
- 前端：Vite 开发服务器
- 后端：Uvicorn 开发服务器
- 数据库：Qdrant 本地模式
- Embedding: 本地模型推理

**Docker 部署模式**:
- 前端：Nginx 容器
- 后端：FastAPI + Uvicorn 容器
- 数据库：Qdrant Docker 容器
- Embedding: 阿里云 API

**云服务部署模式**:
- 前端：静态文件托管 (如 Vercel)
- 后端：云服务器 (如阿里云 ECS)
- 数据库：Qdrant 云服务
- Embedding: 阿里云 DashScope

### 5.2 配置管理

通过\`.env\` 文件管理环境变量:
\`\`\`
EMBEDDING_API_PROVIDER=aliyun
QDRANT_MODE=docker
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL_NAME=qwen3.5-plus
ALIYUN_EMBEDDING_API_KEY=sk-xxx
ALIYUN_EMBEDDING_MODEL_NAME=qwen3-vl-embedding
\`\`\`

## 6. 参考文档 📚

- [Qdrant 官方文档](https://qdrant.tech/documentation/)
- [ReAct Prompting 指南](https://www.promptingguide.ai/techniques/react)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [React 19 文档](https://react.dev/blog/2024/12/05/react-19)
- [Openjiuwen 文档](https://github.com/openjiuwen/openjiuwen)
- [通义千问 API](https://help.aliyun.com/zh/dashscope/)
`;

export const ArchitecturePage: React.FC = () => {
  const { token } = theme.useToken();

  return (
    <div style={{ 
      maxWidth: 1000, 
      margin: '0 auto', 
      padding: '24px 16px' 
    }}>
      <Card 
        variant="borderless"
        style={{
          boxShadow: '0 8px 32px rgba(0,0,0,0.08)', 
          borderRadius: 16,
          background: token.colorBgContainer,
          // backdropFilter: 'blur(12px)', // 如果背景是半透明的
        }}
      >
        <div className="markdown-body" style={{ color: token.colorText }}>
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              h1: ({ ...props }) => <h1 style={{ color: token.colorPrimary, borderBottom: `1px solid ${token.colorBorderSecondary}`, paddingBottom: 16, marginBottom: 24 }} {...props} />,
              h2: ({ ...props }) => <h2 style={{ color: token.colorTextHeading, marginTop: 32, marginBottom: 16 }} {...props} />,
              h3: ({ ...props }) => <h3 style={{ color: token.colorTextHeading, marginTop: 24, marginBottom: 12 }} {...props} />,
              p: ({ ...props }) => <p style={{ color: token.colorText, lineHeight: 1.8, marginBottom: 16 }} {...props} />,
              li: ({ ...props }) => <li style={{ color: token.colorText, lineHeight: 1.8, marginBottom: 8 }} {...props} />,
              pre: ({ ...props }) => (
                <pre style={{ 
                    background: token.colorFillAlter, 
                    padding: 16, 
                    borderRadius: 8, 
                    overflow: 'auto', 
                    marginBottom: 16,
                    border: `1px solid ${token.colorBorderSecondary}`
                }} {...props} />
              ),
              code: (props: React.HTMLAttributes<HTMLElement> & { inline?: boolean }) => {
                const { inline, ...rest } = props;
                if (inline) {
                   return (
                      <code 
                          style={{ 
                              background: token.colorFillAlter, 
                              padding: '2px 6px', 
                              borderRadius: 4, 
                              color: token.colorError, 
                              fontFamily: 'monospace',
                              fontSize: '0.9em'
                          }} 
                          {...rest} 
                      />
                  )
                }
                return <code style={{ fontFamily: 'monospace', color: 'inherit' }} {...rest} />;
              }
            }}
          >
            {markdownContent}
          </ReactMarkdown>
        </div>
      </Card>
      <FloatButton.BackTop />
    </div>
  );
};
