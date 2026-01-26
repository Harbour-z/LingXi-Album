# 前端"以图搜图"功能 top_k 参数传递问题修复总结

## 问题

前端"以图搜图"功能中，搜索数量与前端选择不匹配，`top_k` 参数未能正确传入后端。

## 根本原因

**参数传递方式不匹配**:
- 前端使用 `FormData` 发送请求，`top_k` 作为 form 字段
- 后端使用 `Query` 参数接收，期望 URL 查询参数
- 结果：FormData 中的 `top_k` 被忽略，始终使用默认值 10

## 解决方案

将后端 `/search/image` 接口的参数从 `Query` 改为 `Form`。

### 修改文件

[app/routers/search.py](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/routers/search.py)

**修改前**:
```python
async def search_by_uploaded_image(
    file: UploadFile = File(...),
    instruction: Optional[str] = Query(None),
    top_k: int = Query(10, ge=1, le=100),
    score_threshold: Optional[float] = Query(None, ge=0, le=1),
    tags: Optional[List[str]] = Query(None),
    search_svc: SearchService = Depends(get_service)
):
```

**修改后**:
```python
from fastapi import Form  # 添加导入

async def search_by_uploaded_image(
    file: UploadFile = File(...),
    instruction: Optional[str] = Form(None),  # 改为 Form
    top_k: int = Form(10, ge=1, le=100),  # 改为 Form
    score_threshold: Optional[float] = Form(None, ge=0, le=1),  # 改为 Form
    tags: Optional[List[str]] = Form(None),  # 改为 Form
    search_svc: SearchService = Depends(get_service)
):
```

## 验证步骤

1. **重启后端服务**:
   ```bash
   python -m app.main
   ```

2. **运行测试脚本**:
   ```bash
   python check_backend.py
   ```

3. **测试前端功能**:
   - 打开前端页面
   - 选择"以图搜图"
   - 调整"显示结果数量"滑块（例如设置为 20）
   - 上传图片搜索
   - 验证返回结果数量是否为 20

## 测试文件

- [check_backend.py](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/check_backend.py) - 快速测试脚本
- [test_image_search_topk.py](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/test_image_search_topk.py) - 完整测试脚本

## 关键技术点

- **Query 参数**: 从 URL 查询字符串获取（`?key=value`）
- **Form 参数**: 从 FormData 获取（multipart/form-data）
- **File 参数**: 从 FormData 获取上传的文件

当使用 FormData 发送文件和参数时，普通参数应使用 `Form` 而不是 `Query`。

## 前端无需修改

前端代码已经正确使用 FormData 发送参数，无需任何修改。

## 向后兼容

修复后的接口仍然支持不传递 `top_k` 参数，会使用默认值 10。

## 详细文档

完整的技术分析请参考：[IMAGE_SEARCH_TOPK_FIX.md](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/IMAGE_SEARCH_TOPK_FIX.md)
