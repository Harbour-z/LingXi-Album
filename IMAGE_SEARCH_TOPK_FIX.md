# 前端"以图搜图"功能 top_k 参数传递问题修复

## 问题描述

在前端"以图搜图"核心功能中，存在搜索数量与前端选择数量不匹配的问题，或者 `top_k` 参数未能正确传入，导致核心功能无法有效实现。

## 问题分析

### 1. 前端代码分析

**文件**: [frontend/src/api/search.ts](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/frontend/src/api/search.ts#L58-L80)

```typescript
export async function searchByUploadedImage(
    file: File,
    topK: number = 10,
    scoreThreshold?: number,
    tags?: string[]
): Promise<SearchResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('top_k', topK.toString());  // ← top_k 作为 FormData 字段发送
    if (scoreThreshold) {
        formData.append('score_threshold', scoreThreshold.toString());
    }
    if (tags && tags.length > 0) {
        tags.forEach(tag => formData.append('tags', tag));
    }

    const response = await client.post('/search/image', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response as unknown as SearchResponse;
}
```

前端使用 `FormData` 发送请求，`top_k` 参数作为 **form 字段**（multipart/form-data）发送。

### 2. 后端代码分析（修复前）

**文件**: [app/routers/search.py](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/routers/search.py#L185-L193)（修复前）

```python
async def search_by_uploaded_image(
    file: UploadFile = File(..., description="上传的查询图片"),
    instruction: Optional[str] = Query(None, description="自定义指令"),
    top_k: int = Query(10, ge=1, le=100, description="返回数量"),  # ← 问题：期望是 Query 参数！
    score_threshold: Optional[float] = Query(
        None, ge=0, le=1, description="相似度阈值"),
    tags: Optional[List[str]] = Query(None, description="标签过滤"),
    search_svc: SearchService = Depends(get_service)
):
```

后端使用 `Query` 参数来接收参数，期望这些参数出现在 **URL 查询字符串**中（如 `/search/image?top_k=20`）。

### 3. 问题根源

- **前端发送方式**: `top_k` 作为 FormData 字段发送（multipart/form-data）
- **后端接收方式**: `top_k` 期望作为 Query 参数接收（URL 参数）
- **结果**: FormData 中的 `top_k` 字段被后端忽略，始终使用默认值 10

## 解决方案

### 修复内容

将后端 `/search/image` 接口的参数从 `Query` 改为 `Form`，使其能够正确接收 FormData 中的字段。

### 修复后的代码

**文件**: [app/routers/search.py](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/routers/search.py#L185-L193)

```python
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form  # ← 添加 Form 导入

@router.post(
    "/image",
    response_model=SearchResponse,
    summary="上传图片搜索",
    description="上传图片进行以图搜图"
)
async def search_by_uploaded_image(
    file: UploadFile = File(..., description="上传的查询图片"),
    instruction: Optional[str] = Form(None, description="自定义指令"),  # ← 改为 Form
    top_k: int = Form(10, ge=1, le=100, description="返回数量"),  # ← 改为 Form
    score_threshold: Optional[float] = Form(  # ← 改为 Form
        None, ge=0, le=1, description="相似度阈值"),
    tags: Optional[List[str]] = Form(None, description="标签过滤"),  # ← 改为 Form
    search_svc: SearchService = Depends(get_service)
):
```

## 技术要点

### FastAPI 参数类型

1. **Query 参数**: 用于从 URL 查询字符串中获取参数（如 `?key=value`）
2. **Form 参数**: 用于从 multipart/form-data 或 application/x-www-form-urlencoded 中获取参数
3. **File 参数**: 用于从 multipart/form-data 中获取上传的文件

### 参数接收匹配

当使用 `FormData` 发送文件和参数时：
- 文件使用 `File` 接收
- 普通参数使用 `Form` 接收（而不是 `Query`）

## 验证步骤

### 1. 启动后端服务

```bash
python -m app.main
```

### 2. 运行测试脚本

```bash
python check_backend.py
```

### 3. 测试前端功能

1. 打开前端页面
2. 选择"以图搜图"功能
3. 调整"显示结果数量"滑块（例如设置为 20）
4. 上传图片进行搜索
5. 验证返回的搜索结果数量是否为 20

## 修改文件列表

1. [app/routers/search.py](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/routers/search.py)
   - 添加 `Form` 导入
   - 将 `top_k`、`instruction`、`score_threshold`、`tags` 参数从 `Query` 改为 `Form`

## 测试文件

1. [check_backend.py](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/check_backend.py) - 检查后端服务状态并测试 top_k 参数
2. [test_image_search_topk.py](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/test_image_search_topk.py) - 完整的测试脚本

## 注意事项

1. **服务重启**: 修改后端代码后，需要重启服务才能生效
   - 如果使用 `uvicorn --reload`，会自动重载
   - 否则需要手动重启服务

2. **前端无需修改**: 前端代码已经正确地使用 FormData 发送参数，无需修改

3. **参数验证**: `Form` 参数支持与 `Query` 参数相同的验证规则（如 `ge=1, le=100`）

4. **向后兼容**: 修复后的接口仍然支持不传递 `top_k` 参数的情况，会使用默认值 10

## 相关文档

- FastAPI Request Forms 文档: https://fastapi.tiangolo.com/tutorial/request-forms/
- FastAPI File Uploads 文档: https://fastapi.tiangolo.com/tutorial/request-files/
