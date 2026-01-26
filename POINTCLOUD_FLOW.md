# 3DGS点云生成服务调用流程

本文档详细描述了从前端发起请求到最终返回3DGS结果的完整调用流程。

## 目录

- [完整调用流程](#完整调用流程)
- [流程图](#流程图)
- [关键时间点](#关键时间点)
- [异步处理优势](#异步处理优势)
- [API接口说明](#api接口说明)
- [配置说明](#配置说明)

---

## 完整调用流程

### 1. 前端发起请求

**用户操作：**
- 在聊天界面输入：`"帮我把这张图片转换成3D"`
- 或者：`"生成3D点云"`

**前端请求：**
```typescript
// frontend/src/api/agent.ts
POST /api/v1/agent/chat
{
  "query": "帮我把这张图片转换成3D",
  "session_id": "xxx"
}
```

### 2. 后端接收请求

**路由层：** `app/routers/agent.py`
```python
@router.post("/chat")
async def chat(request: AgentRequest):
    # 转发给 AgentService
    result = await agent_service.chat(request.query, request.session_id)
    return result
```

### 3. Agent服务处理

**服务层：** `app/services/agent_service.py`

#### 3.1 意图识别

Agent接收到查询后，通过以下方式处理：

**方式A：ReActAgent（优先）**
```python
# 如果配置了OpenAI API，使用ReActAgent
result = await self._agent.invoke({
    "query": "帮我把这张图片转换成3D",
    "conversation_id": "xxx"
})
```

**方式B：OpenAI兼容模式（回退）**
```python
# 如果ReActAgent不可用，使用OpenAI兼容接口
answer = await self._chat_openai_compatible(query, session_id)
```

#### 3.2 工具选择

Agent分析用户意图，从可用工具中选择 `generate_pointcloud`：

**工具定义：**
```python
{
    "name": "generate_pointcloud",
    "description": "将图片转换为3D点云(PLY格式)。适用于用户要求将图片转换成3D、生成3D模型、生成点云的场景。需要先找到图片ID。"
}
```

#### 3.3 参数解析

Agent识别到需要图片ID，但用户没有提供。Agent会：

1. **先搜索图片**：调用 `semantic_search_images` 或 `meta_search_images`
2. **获取图片ID**：从搜索结果中提取图片ID
3. **调用点云生成**：使用图片ID调用 `generate_pointcloud`

**工具调用序列：**
```
1. semantic_search_images(query="这张图片")
   → 返回图片列表 [{"id": "img_123", ...}]

2. generate_pointcloud(image_id="img_123", quality="medium")
   → 返回点云任务ID
```

### 4. 点云生成服务

**服务层：** `app/services/pointcloud_service.py`

#### 4.1 创建任务
```python
async def generate_pointcloud(image_id, image_path, quality, async_mode):
    pointcloud_id = self._generate_id()  # 生成UUID

    # 初始化任务状态
    pointcloud_info = {
        "pointcloud_id": pointcloud_id,
        "status": "pending",
        "source_image_id": image_id,
        ...
    }

    if async_mode:
        # 异步生成（推荐）
        asyncio.create_task(self._generate_pointcloud_async(...))
    else:
        # 同步生成
        await self._generate_pointcloud_async(...)
```

#### 4.2 调用外部3DGS服务
```python
async def _call_3dgs_service(image_path, quality):
    # 读取图片
    with open(image_path, "rb") as f:
        image_data = f.read()

    # 构造HTTP请求（使用 ML-Sharp API 格式）
    url = f"{self._service_url}/api/v1/generate"
    files = {"image": (f"image{ext}", image_data, mime_type)}
    data = {
        "quality": quality,  # 'balanced' 或 'fast'
        "return_format": "url",  # 获取下载 URL
        "simplify_ply": "true"  # 使用简化格式
    }

    # 发送请求到3DGS服务
    async with aiohttp.ClientSession() as session:
        async with session.post(url, files=files, data=data) as response:
            if response.status == 200:
                response_data = await response.json()
                if response_data.get("success"):
                    # 从返回的 URL 下载 PLY 文件
                    download_url = response_data.get("download_url")
                    ply_data, point_count = await self._download_ply_file(
                        session, 
                        f"{self._service_url}{download_url}"
                    )
                    return {
                        "success": True, 
                        "ply_data": ply_data, 
                        "point_count": point_count,
                        "metadata": response_data.get("metadata", {})
                    }
```

#### 4.3 保存PLY文件
```python
# 保存到 storage/pointclouds/YYYY/MM/DD/{pointcloud_id}.ply
ply_path = self._get_pointcloud_path(pointcloud_id)
with open(ply_path, "wb") as f:
    f.write(ply_data)

# 更新任务状态
pointcloud_info.update({
    "status": "completed",
    "file_path": str(ply_path.relative_to(self._storage_path)),
    "point_count": point_count
})
```

### 5. 返回结果给Agent

**点云服务返回：**
```python
{
    "pointcloud_id": "pc_abc123",
    "status": "completed",
    "download_url": "/api/v1/pointcloud/download/pc_abc123",
    "point_count": 150000
}
```

### 6. Agent组织回复

**Agent生成自然语言回复：**
```python
{
    "answer": "已成功将图片转换为3D点云！生成了150,000个点，您可以点击链接下载PLY文件。",
    "images": [],
    "pointcloud": {
        "id": "pc_abc123",
        "download_url": "/api/v1/pointcloud/download/pc_abc123"
    }
}
```

### 7. 返回给前端

**后端响应：**
```json
POST /api/v1/agent/chat
{
  "status": "success",
  "data": {
    "answer": "已成功将图片转换为3D点云！...",
    "images": [],
    "pointcloud": {
      "id": "pc_abc123",
      "download_url": "/api/v1/pointcloud/download/pc_abc123",
      "view_url": "http://localhost:5000/view/output_abc123.ply",
      "preview_api_url": "/api/v1/pointcloud/pc_abc123/preview"
    }
  }
}
```

### 8. 前端展示

**前端处理：**
```typescript
// 显示Agent回复
<div>{answer}</div>

// 显示点云下载链接
<a href={pointcloud.download_url} download="pointcloud.ply">
  下载PLY文件
</a>

// 可选：3D预览
<PointCloudViewer url={pointcloud.download_url} />
```

---

## 流程图

```
用户输入
   ↓
前端: POST /api/v1/agent/chat
   ↓
后端路由: agent.py
   ↓
AgentService.chat()
   ↓
[意图识别] → "generate_pointcloud"
   ↓
[参数解析] → 需要image_id
   ↓
[工具调用1] → semantic_search_images()
   ↓
[工具调用2] → generate_pointcloud(image_id)
   ↓
PointCloudService.generate_pointcloud()
   ↓
[异步任务] → _generate_pointcloud_async()
   ↓
[HTTP请求] → POST {POINTCLOUD_SERVICE_URL}/api/v1/generate
   ↓
[3DGS服务] → 返回PLY文件
   ↓
[保存文件] → storage/pointclouds/...
   ↓
[返回结果] → pointcloud_id + download_url + view_url
   ↓
Agent组织回复
   ↓
返回前端
   ↓
前端展示（可点击预览或下载）
   ↓
[可选] 调用预览接口 → POST /api/v1/pointcloud/{id}/preview
   ↓
浏览器打开 3D 预览页面
```

---

## 关键时间点

1. **T0**: 用户发起请求
2. **T1**: Agent识别意图（~1-2秒，取决于LLM）
3. **T2**: 搜索图片（~0.5秒）
4. **T3**: 创建点云任务（~0.1秒）
5. **T4**: 返回任务ID给用户（~0.1秒）
6. **T5**: 3DGS服务生成点云（~30-300秒，异步进行）
7. **T6**: 用户查询任务状态（可选）
8. **T7**: 用户下载PLY文件

---

## 异步处理优势

- **快速响应**：用户立即获得任务ID，不需要等待生成完成
- **后台处理**：3DGS生成耗时较长，不会阻塞其他请求
- **状态查询**：用户可以随时查询生成进度
- **失败重试**：生成失败不影响其他功能

---

## API接口说明

### 点云生成接口

#### POST /api/v1/pointcloud/generate

生成3D点云（支持异步和同步模式）

**请求体：**
```json
{
  "image_id": "img_123",
  "quality": "balanced",
  "async_mode": true
}
```

**响应：**
```json
{
  "status": "success",
  "message": "点云生成任务已创建",
  "data": {
    "pointcloud_id": "pc_abc123",
    "status": "pending",
    "source_image_id": "img_123",
    "download_url": "/api/v1/pointcloud/download/pc_abc123",
    "created_at": "2026-01-25T10:00:00"
  }
}
```

### 点云查询接口

#### GET /api/v1/pointcloud/{pointcloud_id}

获取点云生成状态和详细信息

**响应：**
```json
{
  "status": "success",
  "message": "获取成功",
  "data": {
    "pointcloud_id": "pc_abc123",
    "status": "completed",
    "source_image_id": "img_123",
    "file_path": "2026/01/25/pc_abc123.ply",
    "download_url": "/api/v1/pointcloud/download/pc_abc123",
    "view_url": "http://localhost:5000/view/output_abc123.ply",
    "created_at": "2026-01-25T10:00:00",
    "completed_at": "2026-01-25T10:05:00",
    "file_size": 12345678,
    "point_count": 150000
  }
}
```

### 点云预览接口

#### POST /api/v1/pointcloud/{pointcloud_id}/preview

在浏览器中打开点云的3D预览页面

**响应：**
```json
{
  "status": "success",
  "message": "已在浏览器中打开预览"
}
```

**说明：**
- 此接口会自动在默认浏览器中打开 3DGS 服务提供的预览页面
- 预览页面使用 WebGL 渲染 3D 点云，支持交互式查看
- 需要确保 3DGS 服务正在运行且文件存在

### 点云下载接口

#### GET /api/v1/pointcloud/download/{pointcloud_id}

下载PLY格式的点云文件

**响应：**
- Content-Type: application/octet-stream
- Content-Disposition: attachment; filename="{pointcloud_id}.ply"
- Body: PLY文件二进制数据

---

## 配置说明

### 环境变量配置

在 `.env` 文件中添加以下配置：

```env
# 3DGS Point Cloud Service Configuration
POINTCLOUD_SERVICE_URL="http://localhost:5000"
POINTCLOUD_SERVICE_TIMEOUT=300
```

### 配置参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `POINTCLOUD_SERVICE_URL` | ML-Sharp 3DGS服务的基础URL | `http://localhost:5000` |
| `POINTCLOUD_SERVICE_TIMEOUT` | 请求超时时间（秒） | `300` |
| `POINTCLOUD_STORAGE_PATH` | 点云文件存储路径 | `storage/pointclouds` |

### 3DGS服务接口规范（ML-Sharp API）

你的3DGS服务需要实现以下接口（基于 ML-Sharp API 规范）：

**POST /api/v1/generate**

**请求：**
- Content-Type: multipart/form-data
- 参数：
  - `image`: 图片文件
  - `quality`: 生成质量 (`balanced` 高质量 或 `fast` 快速模式)
  - `return_format`: 返回格式 (`url` 或 `file`)
  - `simplify_ply`: 是否使用简化 PLY 格式 (`true` 或 `false`)

**响应：**
- 成功（200）：
  ```json
  {
    "success": true,
    "filename": "output.ply",
    "download_url": "/api/v1/download/output.ply",
    "view_url": "/view/output.ply",
    "metadata": {
      "width": 1920,
      "height": 1080,
      "focal_length": 1536.0,
      "quality": "balanced",
      "simplified": true,
      "device": "cuda"
    }
  }
  ```
- 失败（4xx/5xx）：
  ```json
  {
    "error": "错误信息"
  }
  ```

**GET /api/v1/download/<filename>**

下载生成的 PLY 文件。

**响应：**
- 成功（200）：
  - Content-Type: application/octet-stream
  - Body: PLY文件二进制数据
- 失败（404）：
  ```json
  {
    "error": "File not found"
  }
  ```

**GET /health**

健康检查接口。

**响应：**
```json
{
  "status": "healthy",
  "device": "cuda",
  "model_loaded": true
}
```

---

## 相关文件

- `app/config.py` - 配置管理
- `app/models/schemas.py` - 数据模型定义
- `app/services/pointcloud_service.py` - 点云服务实现
- `app/routers/pointcloud.py` - API路由定义
- `app/services/agent_service.py` - Agent服务（含工具定义）
- `app/main.py` - 应用入口（路由注册）

---

## 常见问题

### Q1: 如何判断点云生成是否完成？

A: 调用 `GET /api/v1/pointcloud/{pointcloud_id}` 查询状态，`status` 字段为 `completed` 表示完成。

### Q2: 异步模式下如何获取结果？

A: 保存返回的 `pointcloud_id`，然后轮询查询接口，或者在前端实现定时轮询。

### Q3: 点云文件存储在哪里？

A: 存储在 `storage/pointclouds/YYYY/MM/DD/` 目录下，按日期分层。

### Q4: 如何处理生成失败的情况？

A: 查询接口会返回 `status: "failed"` 和 `error_message` 字段，可以根据错误信息进行重试或提示用户。

### Q5: 如何在浏览器中查看 3D 点云？

A: 有两种方式：
1. **直接访问 view_url**：从点云信息中获取 `view_url`，在浏览器中打开该 URL
2. **调用预览接口**：调用 `POST /api/v1/pointcloud/{pointcloud_id}/preview`，系统会自动在浏览器中打开预览页面

**预览页面控制：**
- WASD 键：移动视角
- 鼠标拖拽：旋转视角
- Q/E 键：上下移动
- 滚轮：调整移动速度
- SBS 3D 模式按钮：切换立体视角

### Q6: 预览功能需要什么条件？

A: 需要满足以下条件：
1. 3DGS 服务（ML-Sharp）正在运行
2. 点云生成状态为 `completed`
3. 点云文件在 3DGS 服务的输出目录中存在
4. 浏览器支持 WebGL

---

## 更新日志

- 2026-01-25: 初始版本，完成3DGS点云生成服务集成