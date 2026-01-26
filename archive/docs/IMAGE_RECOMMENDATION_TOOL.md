# 智能图片推荐工具集成文档

## 概述

智能图片推荐工具是一个集成到Agent工具集合中的功能模块，使用多模态AI模型（qwen3-max + qwen3-vl-plus）对多张照片进行深度分析，从艺术与内容维度进行评估，并推荐最佳照片。

## 系统架构

### 职责划分

**后端服务职责：**
- AI模型调用（qwen3-max、qwen3-vl-plus）
- 图片分析处理
- 推荐逻辑运算
- 工具接口暴露

**前端界面职责：**
- 图片上传
- 结果展示
- 用户交互

**工具模块：**
- 封装为符合Agent框架规范的格式
- 可被动态加载和调用

## 核心功能流程

```
用户上传多张备选图片
    ↓
后端调用qwen3-max模型生成优化提示词
    ↓
使用qwen3-vl-plus模型进行多模态分析
    ↓
从艺术维度进行深度评估
    ↓
返回推荐结果和详细分析
```

## 评估维度

### 强制要求的评价维度

1. **构图美学** (25%权重)
   - 构图法则遵循（黄金分割、三分法、引导线等）
   - 主体位置和画面平衡
   - 视觉焦点和层次感
   - 前景、中景、背景的协调性

2. **色彩搭配** (20%权重)
   - 色调和谐统一性
   - 色彩饱和度、明度适中
   - 主色调与辅助色配合
   - 色彩对比或渐变效果

3. **光影运用** (15%权重)
   - 光线方向、质量（顺光、逆光、侧光、漫射光）
   - 光影层次感和立体感
   - 高光和阴影处理
   - 光斑、曝光问题

4. **主题表达清晰度** (15%权重)
   - 主题明确突出
   - 画面传达的意图
   - 主体与背景关系
   - 视觉干扰元素

5. **情感传达强度** (10%权重)
   - 情感共鸣能力
   - 情绪氛围营造
   - 画面故事感和代入感
   - 独特情感表达

6. **创意独特性** (8%权重)
   - 视角新颖性（鸟瞰、低角度、微距等）
   - 拍摄手法创新
   - 独特视觉元素或构图
   - 避免常见俗套

7. **故事性** (7%权重)
   - 完整或引人遐想的故事
   - 视觉叙事连贯性
   - 引人深思的细节
   - 画面元素的叙事性组合

### 严格禁止的评价维度

- ❌ 仅基于分辨率（像素数量）
- ❌ 仅基于文件大小
- ❌ 仅基于压缩质量
- ❌ 仅基于EXIF参数
- ❌ 仅基于技术规格

## 技术实现

### 1. 服务模块

**文件：** `app/services/image_recommendation_service.py`

核心类：`ImageRecommendationService`

主要方法：
- `initialize(settings)`: 初始化服务
- `_generate_analysis_prompt(image_count, user_preference)`: 使用qwen3-max生成优化提示词
- `_analyze_images_with_vl(images_data, prompt, image_ids)`: 使用qwen3-vl-plus分析图片
- `recommend_images(images, image_ids, user_preference)`: 智能推荐主流程

### 2. API路由

**文件：** `app/routers/image_recommendation.py`

端点：

1. **POST /api/v1/image-recommendation/analyze**
   - 根据图片ID列表进行推荐
   - 请求体：
     ```json
     {
       "images": ["id1", "id2", "id3"],
       "user_preference": "我更喜欢构图好的照片"
     }
     ```

2. **POST /api/v1/image-recommendation/upload-analyze**
   - 直接上传图片并推荐
   - 支持 `multipart/form-data` 上传多张图片
   - 参数：
     - `files`: 图片文件列表（最多10张）
     - `user_preference`: 用户偏好（可选）

3. **GET /api/v1/image-recommendation/health**
   - 健康检查端点

### 3. Agent工具注册

**文件：** `app/services/agent_service.py`

工具名称：`recommend_images`

工具描述：
```
智能图片推荐工具。使用多模态AI模型（qwen3-max + qwen3-vl-plus）对多张照片进行深度分析，
从构图美学、色彩搭配、光影运用、主题表达、情感传达、创意独特性、故事性等艺术维度进行评估，
并推荐最佳照片。适用于用户询问'哪一张拍的最好'、'帮我选一张最好的'、'推荐最佳照片'等场景。
严禁仅基于分辨率、文件大小等技术参数进行评价。
```

工具参数：
- `images`: 图片ID列表（数组，必需，最多10张）
- `user_preference`: 用户偏好（字符串，可选）

### 4. 错误处理和重试机制

使用 `tenacity` 库实现自动重试：

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((TimeoutException, HTTPStatusError)),
    reraise=True
)
```

重试配置：
- 最大重试次数：3次
- 退避策略：指数退避
- 最小等待时间：2秒
- 最大等待时间：10秒
- 重试条件：超时或HTTP错误

## 配置说明

### 环境变量

在 `.env` 文件中配置：

```env
# LLM模型（qwen3-max，用于生成提示词）
OPENAI_MODEL_NAME="qwen3-max"

# 视觉模型（qwen3-vl-plus，用于图片分析）
VISION_MODEL_NAME="qwen3-vl-plus"

# API配置
OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
OPENAI_API_KEY="your-api-key"
```

### 服务初始化

在 `app/main.py` 中初始化：

```python
# 初始化图片推荐服务
logger.info("初始化图片推荐服务...")
image_recommendation_service = get_image_recommendation_service()
image_recommendation_service.initialize(settings)
```

## 数据格式

### 请求格式

**根据ID推荐：**
```json
{
  "images": ["uuid-1", "uuid-2", "uuid-3"],
  "user_preference": "我更喜欢色彩搭配好的照片"
}
```

**上传推荐：**
```http
POST /api/v1/image-recommendation/upload-analyze
Content-Type: multipart/form-data

files: [file1.jpg, file2.jpg, file3.jpg]
user_preference: "我更喜欢构图好的照片"
```

### 响应格式

```json
{
  "status": "success",
  "message": "图片推荐完成",
  "data": {
    "success": true,
    "analysis": {
      "image_1": {
        "id": "uuid-1",
        "composition_score": 8.5,
        "composition_analysis": "构图分析详细描述...",
        "color_score": 9.0,
        "color_analysis": "色彩分析详细描述...",
        "lighting_score": 8.0,
        "lighting_analysis": "光影分析详细描述...",
        "theme_score": 8.5,
        "theme_analysis": "主题表达分析详细描述...",
        "emotion_score": 9.0,
        "emotion_analysis": "情感传达分析详细描述...",
        "creativity_score": 7.5,
        "creativity_analysis": "创意独特性分析详细描述...",
        "story_score": 8.0,
        "story_analysis": "故事性分析详细描述...",
        "overall_score": 8.35,
        "overall_analysis": "综合评价总结..."
      },
      "image_2": {...},
      "image_3": {...}
    },
    "recommendation": {
      "best_image_id": "uuid-2",
      "recommendation_reason": "推荐理由详细说明...",
      "alternative_image_ids": ["uuid-1", "uuid-3"],
      "key_strengths": ["主要优势点1", "主要优势点2"],
      "potential_improvements": ["可改进点1", "可改进点2"]
    },
    "model_used": "qwen3-vl-plus",
    "total_images": 3
  }
}
```

## 使用示例

### 1. 通过Agent使用

用户提问：
```
"帮我从这3张照片中选一张最好的"
```

Agent会自动调用 `recommend_images` 工具：
```
ReAct iteration 1
Thought: 用户想要从3张照片中选择最好的一张，我应该使用智能图片推荐工具
Action: recommend_images
Action Input: {"images": ["id1", "id2", "id3"]}
```

### 2. 直接调用API

```python
import requests

# 根据图片ID推荐
response = requests.post(
    "http://localhost:8000/api/v1/image-recommendation/analyze",
    json={
        "images": ["id1", "id2", "id3"],
        "user_preference": "我更喜欢构图好的照片"
    }
)

# 上传图片推荐
files = [
    ("files", open("photo1.jpg", "rb")),
    ("files", open("photo2.jpg", "rb")),
    ("files", open("photo3.jpg", "rb"))
]
response = requests.post(
    "http://localhost:8000/api/v1/image-recommendation/upload-analyze",
    files=files,
    data={"user_preference": "我更喜欢构图好的照片"}
)
```

## 依赖说明

### Python依赖

```txt
fastapi
httpx
tenacity
pillow
pydantic
python-multipart
```

### 服务依赖

- **阿里云DashScope API**: qwen3-max 和 qwen3-vl-plus 模型
- **存储服务**: 用于读取图片文件
- **Agent框架**: Openjiuwen ReAct Agent

## 日志记录

服务会记录以下关键信息：

- 服务初始化状态
- 提示词生成完成
- 图片分析开始和完成
- 分析结果解析成功/失败
- 推荐结果（最佳图片ID）
- 错误和异常详情

示例日志：
```
2026-01-26 02:04:41 - app.services.image_recommendation_service - INFO - 图片推荐服务初始化完成 (LLM: qwen3-max, VL: qwen3-vl-plus)
2026-01-26 02:05:00 - app.services.image_recommendation_service - INFO - 开始智能图片推荐: 图片数量=3, 用户偏好=我更喜欢构图好的照片
2026-01-26 02:05:00 - app.services.image_recommendation_service - INFO - 步骤1: 使用qwen3-max生成分析提示词...
2026-01-26 02:05:05 - app.services.image_recommendation_service - INFO - 提示词生成完成，长度: 1234 字符
2026-01-26 02:05:05 - app.services.image_recommendation_service - INFO - 步骤2: 使用qwen3-vl-plus进行多模态分析...
2026-01-26 02:05:30 - app.services.image_recommendation_service - INFO - qwen3-vl-plus分析完成，返回3567字符
2026-01-26 02:05:30 - app.services.image_recommendation_service - INFO - 步骤3: 解析分析结果...
2026-01-26 02:05:31 - app.services.image_recommendation_service - INFO - 分析结果解析成功: 推荐图片=image_2
```

## 性能优化

### 1. 连接复用

使用 `httpx.AsyncClient` 进行HTTP请求，支持连接池和连接复用。

### 2. 超时配置

- API请求超时：120秒
- 适应大模型推理时间

### 3. 重试机制

自动重试失败的请求，提高可靠性。

### 4. 批量处理

支持一次性分析最多10张图片，减少API调用次数。

## 错误处理

### 常见错误

1. **服务未初始化**
   - 错误：`RuntimeError: 图片推荐服务未初始化`
   - 解决：检查服务是否在 `app/main.py` 中正确初始化

2. **图片数量超限**
   - 错误：`ValueError: 最多支持分析10张图片`
   - 解决：减少图片数量或分批处理

3. **模型调用失败**
   - 错误：`TimeoutException` 或 `HTTPStatusError`
   - 解决：自动重试最多3次，检查网络连接和API密钥

4. **JSON解析失败**
   - 错误：`JSONDecodeError`
   - 解决：检查模型返回格式，尝试提取JSON片段

### 错误响应格式

```json
{
  "success": false,
  "error": "错误描述",
  "details": "详细信息"
}
```

## 测试验证

### 运行测试

```bash
# 简单测试
python test_image_recommendation_simple.py

# 完整测试（需要AI模型调用）
python test_image_recommendation_tool.py
```

### 测试覆盖

- ✓ 健康检查
- ✓ API文档验证
- ✓ Agent工具注册
- ✓ 上传图片推荐
- ✓ 错误处理和重试

## 安全性

1. **API密钥管理**
   - 通过环境变量配置
   - 不在代码中硬编码

2. **输入验证**
   - 图片数量限制（最多10张）
   - 参数类型验证
   - 文件格式检查

3. **错误信息**
   - 不泄露敏感信息
   - 提供有用的错误提示

## 扩展性

### 添加新的评估维度

在 `_generate_analysis_prompt` 方法中添加新的维度描述和权重配置。

### 支持更多模型

修改 `initialize` 方法，添加对其他多模态模型的支持。

### 自定义提示词

通过 `user_preference` 参数传入自定义偏好，系统会将其集成到提示词中。

## 总结

智能图片推荐工具已成功集成到Agent框架中，提供：

- ✓ 多模态AI模型集成（qwen3-max + qwen3-vl-plus）
- ✓ 7个艺术维度的深度评估
- ✓ 严格禁止技术参数评价
- ✓ 自动重试和错误处理
- ✓ 结构化的JSON响应
- ✓ Agent工具集成
- ✓ 完整的API接口
- ✓ 详细的日志记录

工具已准备就绪，可以立即使用！
