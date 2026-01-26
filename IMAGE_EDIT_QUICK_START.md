# 图片编辑功能快速使用指南

## 概述

图片编辑功能基于通义千问 qwen-image-edit-plus 模型，提供强大的图片风格转换和编辑能力。支持 8 种艺术风格，自动智能提示词优化，并与 Agent 对话系统无缝集成。

## 支持的编辑风格

| 风格ID | 风格名称 | 描述 | 示例提示词 |
|---------|----------|------|-----------|
| anime | 动漫风格 | 将图片转换为日式动漫风格 | "将图片转换为动漫风格" |
| cartoon | 卡通风格 | 将图片转换为卡通插画风格 | "将图片转换为卡通风格" |
| oil_painting | 油画风格 | 将图片转换为油画艺术风格 | "将图片转换为油画风格" |
| watercolor | 水彩风格 | 将图片转换为水彩画风格 | "将图片转换为水彩画风格" |
| sketch | 素描风格 | 将图片转换为铅笔素描风格 | "将图片转换为素描风格" |
| cyberpunk | 赛博朋克风格 | 将图片转换为赛博朋克科幻风格 | "将图片转换为赛博朋克风格" |
| retro | 复古风格 | 将图片转换为复古胶片风格 | "将图片转换为复古风格" |
| cinematic | 电影风格 | 将图片转换为电影画面风格 | "将图片转换为电影风格" |

## 使用方式

### 方式一：通过 Agent 对话（推荐）

最简单的方式，直接与 Agent 对话即可：

```bash
# 启动对话
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "把这张图转成动漫风格"
  }'
```

**常用的对话示例：**
- "把这张图转成动漫风格"
- "帮我把图片改成卡通风格"
- "我想把照片改成水彩画风格"
- "把这张照片做成油画效果"
- "给我生成一个素描版本"

**注意事项：**
- Agent 会先搜索图片，找到匹配的图片后才会进行编辑
- 如果有多张图片，Agent 会询问要编辑哪一张
- 编辑后的图片会自动保存到画廊

### 方式二：直接调用 API

如果知道图片 ID，可以直接调用 API：

```bash
curl -X POST http://localhost:8000/api/v1/image-edit/edit \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": "308385fb-1792-4e49-93c3-55c8d4ed5eae",
    "prompt": "将图片转换为动漫风格",
    "style_tag": "anime",
    "n": 2
  }'
```

**参数说明：**

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| image_id | string | 是 | - | 要编辑的图片 ID |
| prompt | string | 是 | - | 编辑提示词 |
| negative_prompt | string | 否 | " " | 反向提示词，描述不希望出现的内容 |
| prompt_extend | boolean | 否 | true | 是否开启智能提示词改写（强烈建议开启） |
| n | integer | 否 | 1 | 生成图片数量（1-6） |
| size | string | 否 | - | 输出图片分辨率，格式 "宽*高"，如 "1024*1536" |
| watermark | boolean | 否 | false | 是否添加水印 |
| seed | integer | 否 | - | 随机数种子 |
| style_tag | string | 否 | - | 风格标签，用于元数据记录 |

### 方式三：二次确认模式

对于需要确认的操作，可以使用确认接口：

```bash
# 第一步：Agent 识别意图
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "把这张图转成动漫风格"
  }'

# 第二步：确认并执行
curl -X POST http://localhost:8000/api/v1/image-edit/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "confirmed": true,
    "image_id": "308385fb-1792-4e49-93c3-55c8d4ed5eae",
    "prompt": "将图片转换为动漫风格",
    "style_tag": "anime",
    "n": 2
  }'
```

## API 接口列表

### 1. 获取服务状态

```bash
GET /api/v1/image-edit/status
```

**响应示例：**
```json
{
  "status": "success",
  "message": "操作成功",
  "data": {
    "initialized": true,
    "model_name": "qwen-image-edit-plus",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key_configured": true
  }
}
```

### 2. 获取支持的风格列表

```bash
GET /api/v1/image-edit/styles
```

**响应示例：**
```json
{
  "status": "success",
  "message": "获取风格列表成功",
  "data": {
    "styles": [
      {
        "id": "anime",
        "name": "动漫风格",
        "description": "将图片转换为日式动漫风格",
        "prompt_template": "将图片转换为动漫风格",
        "example": "将图片转换为动漫风格"
      }
    ]
  }
}
```

### 3. 执行图片编辑

```bash
POST /api/v1/image-edit/edit
```

**请求示例：**
```json
{
  "image_id": "308385fb-1792-4e49-93c3-55c8d4ed5eae",
  "prompt": "将图片转换为动漫风格",
  "style_tag": "anime",
  "n": 2,
  "prompt_extend": true
}
```

**响应示例：**
```json
{
  "status": "success",
  "message": "图片编辑成功，生成 2 张图片，已保存 2 张",
  "data": {
    "success": true,
    "saved_images": [
      {
        "image_id": "new-image-id-1",
        "url": "http://localhost:8000/api/v1/storage/images/new-image-id-1",
        "metadata": {
          "source_image_id": "308385fb-1792-4e49-93c3-55c8d4ed5eae",
          "edit_prompt": "将图片转换为动漫风格",
          "edit_style": "anime",
          "edit_model": "qwen-image-edit-plus",
          "edit_time": "2026-01-26T13:00:00.000000",
          "tags": ["anime"]
        }
      }
    ],
    "total_generated": 2,
    "total_saved": 2
  }
}
```

### 4. 确认并执行编辑

```bash
POST /api/v1/image-edit/confirm
```

**请求示例：**
```json
{
  "confirmed": true,
  "image_id": "308385fb-1792-4e49-93c3-55c8d4ed5eae",
  "prompt": "将图片转换为动漫风格",
  "style_tag": "anime"
}
```

## 响应格式

所有 API 响应都遵循统一格式：

```json
{
  "status": "success|error",
  "message": "操作结果描述",
  "data": {
    // 具体的响应数据
  }
}
```

**状态码：**
- `success` - 操作成功
- `error` - 操作失败

## 查看编辑结果

### 1. 通过 API 获取图片列表

```bash
GET /api/v1/storage/images?page=1&page_size=10
```

### 2. 通过 ID 获取图片

```bash
GET /api/v1/storage/images/{image_id}
```

### 3. 直接访问图片

```
http://localhost:8000/api/v1/storage/images/{image_id}
```

### 4. 通过元数据筛选

```bash
POST /api/v1/search/meta
```

**请求示例：**
```json
{
  "tags": ["anime"],
  "page": 1,
  "page_size": 10
}
```

## 错误处理

### 常见错误及解决方案

#### 1. 服务未初始化

```json
{
  "status": "error",
  "message": "图片编辑服务未初始化，请检查配置"
}
```

**解决方案：** 检查 `.env` 文件中的 `OPENAI_API_KEY` 是否配置正确

#### 2. 图片不存在

```json
{
  "status": "error",
  "message": "图片不存在: xxx-xxx-xxx"
}
```

**解决方案：** 确认图片 ID 是否正确，或先上传图片

#### 3. API 调用失败

```json
{
  "success": false,
  "error": "HTTP 错误: 401",
  "details": "认证失败"
}
```

**解决方案：** 检查 API Key 是否有效，是否有足够的配额

#### 4. 生成失败

```json
{
  "success": false,
  "error": "模型处理失败"
}
```

**解决方案：** 
- 检查提示词是否合理
- 确认图片格式是否支持
- 尝试降低生成数量

## 高级用法

### 1. 自定义输出分辨率

```json
{
  "image_id": "xxx",
  "prompt": "将图片转换为动漫风格",
  "size": "1024*1536"
}
```

支持的分辨率范围：512-2048 像素

### 2. 使用反向提示词

```json
{
  "image_id": "xxx",
  "prompt": "将图片转换为动漫风格",
  "negative_prompt": "模糊，多余的手指，低质量"
}
```

### 3. 固定随机种子

```json
{
  "image_id": "xxx",
  "prompt": "将图片转换为动漫风格",
  "seed": 123456
}
```

使用相同的种子可以生成相对稳定的结果

### 4. 批量生成多张图片

```json
{
  "image_id": "xxx",
  "prompt": "将图片转换为动漫风格",
  "n": 4
}
```

生成 4 张不同变体的图片

## 性能优化建议

1. **提示词优化**：开启 `prompt_extend=true` 可以自动优化简单描述
2. **生成数量**：根据需求设置合理的生成数量，避免浪费
3. **分辨率控制**：默认分辨率通常足够，除非有特殊需求
4. **批量处理**：需要编辑多张图片时，建议分批处理

## 注意事项

1. **API 配额**：图片编辑会消耗 API 配额，请注意使用量
2. **URL 有效期**：生成的图片 URL 有效期为 24 小时
3. **文件大小**：单张图片文件大小不得超过 10MB
4. **图片格式**：支持 JPG、JPEG、PNG、BMP、TIFF、WEBP 和 GIF
5. **分辨率建议**：建议图像宽高在 384-3072 像素之间

## 完整示例

### 示例 1：通过 Agent 编辑图片

```bash
# 1. 搜索图片
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "找到柴犬的照片"
  }'

# 2. 编辑图片
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "把第一张图转成动漫风格"
  }'

# 3. 查看结果
curl http://localhost:8000/api/v1/storage/images?page=1&page_size=10
```

### 示例 2：直接 API 调用

```bash
# 1. 上传图片
curl -X POST http://localhost:8000/api/v1/storage/upload \
  -F "file=@photo.jpg" \
  -F "tags=personal,vacation"

# 2. 编辑图片
curl -X POST http://localhost:8000/api/v1/image-edit/edit \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": "your-image-id",
    "prompt": "将图片转换为动漫风格",
    "style_tag": "anime",
    "n": 2
  }'

# 3. 查看结果
curl http://localhost:8000/api/v1/storage/images/edited-image-id
```

## 支持

如有问题或需要帮助，请：
1. 查看 API 文档：http://localhost:8000/docs
2. 检查修复报告：IMAGE_EDIT_FIX_REPORT.md
3. 查看测试日志：test_image_edit_complete.py

---

**最后更新**：2026-01-26  
**功能状态**：✓ 已完成并验证  
