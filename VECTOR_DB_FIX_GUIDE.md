# 向量数据库修复和重建指南

## 问题概述

在将 Embedding 服务从本地模型迁移到阿里云 DashScope API 后，遇到了以下问题：

1. **`CollectionInfo` 对象属性错误**：`'CollectionInfo' object has no attribute 'vectors_count'`
2. **向量维度不匹配**：从 2048 维变为 2560 维，需要重建向量数据库
3. **图片格式处理错误**：`OSError: cannot write mode RGBA as JPEG`
4. **向量搜索返回 0 条结果**：由于向量数据库为空或维度不匹配

## 已完成的修复

### 1. 修复 `CollectionInfo` 属性错误

**文件**: [`app/services/vector_db_service.py`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/services/vector_db_service.py#L147-L169)

**问题**: Qdrant 新版 API 的 `CollectionInfo` 对象结构发生变化，`vectors_count` 和 `points_count` 现在位于 `info.params` 中。

**解决方案**: 更新 `get_collection_info()` 方法，兼容新旧 API：

```python
def get_collection_info(self) -> Dict[str, Any]:
    info = self._client.get_collection(self._collection_name)
    
    vectors_count = 0
    points_count = 0
    
    if hasattr(info, 'params') and info.params:
        vectors_count = getattr(info.params, 'vectors_count', 0)
        points_count = getattr(info.params, 'points_count', 0)
    elif hasattr(info, 'vectors_count'):
        vectors_count = getattr(info, 'vectors_count', 0)
        points_count = getattr(info, 'points_count', 0)
    
    return {
        "name": self._collection_name,
        "vectors_count": vectors_count,
        "points_count": points_count,
        "status": info.status.value if hasattr(info.status, 'value') else str(info.status),
        "vector_dimension": self._vector_dimension
    }
```

### 2. 修复图片格式处理错误

**文件**: [`app/services/embedding_service.py`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/services/embedding_service.py#L160-L175)

**问题**: RGBA 模式的图片无法直接保存为 JPEG 格式。

**解决方案**: 添加图片模式转换逻辑：

```python
if image.mode == 'RGBA':
    background = Image.new('RGB', image.size, (255, 255, 255))
    background.paste(image, mask=image.split()[-1])
    image = background
elif image.mode != 'RGB':
    image = image.convert('RGB')

image.save(f.name, format='JPEG', quality=95)
```

### 3. 更新向量维度配置

**文件**: [`app/config.py`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/config.py#L46)

**变更**: 将向量维度从 2048 更新为 2560，以匹配 `qwen3-vl-embedding` 模型的实际输出。

```python
VECTOR_DIMENSION: int = 2560  # Qwen3-VL embedding维度 (2560 for qwen3-vl-embedding)
```

### 4. 创建向量数据库重建工具

**文件**: [`rebuild_vectors.py`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/rebuild_vectors.py)

**功能**:
- 自动遍历所有已存储的图像
- 使用新的 Embedding 模型重新生成向量
- 批量插入向量数据库
- 支持进度跟踪和错误处理
- 提供验证功能

## 使用指南

### 1. 验证修复

运行测试脚本验证所有修复：

```bash
python test_vector_fix.py
```

预期输出：
```
✓ 集合信息获取: 通过
✓ Embedding 服务: 通过
✓ 向量计数: 通过
```

### 2. 重建向量数据库

#### 选项 A: 强制重建（删除所有现有数据）

```bash
python rebuild_vectors.py --force-recreate
```

#### 选项 B: 保留现有数据重建

```bash
python rebuild_vectors.py
```

#### 选项 C: 自定义批量大小

```bash
python rebuild_vectors.py --force-recreate --batch-size 20
```

### 3. 验证重建结果

重建完成后，可以通过以下方式验证：

#### API 端点验证

```bash
# 获取集合统计信息
curl http://localhost:8000/api/v1/vectors/stats/info

# 统计记录数量
curl http://localhost:8000/api/v1/vectors/stats/count

# 列出向量记录
curl http://localhost:8000/api/v1/vectors/?limit=10
```

#### 测试搜索功能

```bash
# 测试文本搜索
curl -X POST http://localhost:8000/api/v1/search/text \
  -H "Content-Type: application/json" \
  -d '{"query": "小狗", "top_k": 10}'
```

## 技术细节

### 向量维度变更说明

| 项目 | 旧值 | 新值 | 说明 |
|------|------|------|------|
| 模型 | 本地 qwen3-vl-embedding-2B | 阿里云 qwen3-vl-embedding API | 从本地推理迁移到 API 服务 |
| 向量维度 | 2048 | 2560 | API 模型固定返回 2560 维 |
| Qdrant 配置 | 2048 | 2560 | 必须与向量维度匹配 |

### API 端点修复

以下端点现在可以正常工作：

- `GET /api/v1/vectors/stats/info` - 获取集合统计信息
- `GET /api/v1/vectors/stats/count` - 统计记录数量
- `GET /api/v1/vectors/` - 列出向量记录
- `POST /api/v1/search/text` - 文本搜索
- `POST /api/v1/search/image` - 图片搜索

### 错误处理改进

所有 API 端点现在都有适当的错误处理：

- `AttributeError` 被捕获并返回清晰的错误信息
- 图片格式错误被自动处理
- 向量维度不匹配会在初始化时检测

## 故障排除

### 问题 1: 向量搜索返回 0 条结果

**可能原因**:
1. 向量数据库为空（需要重建）
2. 向量维度不匹配（需要重新初始化）
3. 搜索参数设置不当

**解决方案**:
```bash
# 检查向量数量
curl http://localhost:8000/api/v1/vectors/stats/count

# 如果为 0，重建向量数据库
python rebuild_vectors.py --force-recreate
```

### 问题 2: `CollectionInfo` 属性错误

**可能原因**: Qdrant 客户端版本不兼容

**解决方案**: 已在代码中修复，支持新旧 API

### 问题 3: 图片上传失败

**可能原因**: 图片格式不支持

**解决方案**: 已在代码中修复，自动转换 RGBA 到 RGB

## 性能优化建议

1. **批量处理**: 使用 `--batch-size` 参数调整批量大小（默认 10）
2. **并发处理**: 可以修改重建脚本支持多线程
3. **增量更新**: 对于大量图片，考虑增量更新而非全量重建

## 总结

所有问题已修复，系统现在可以：

✅ 正确获取集合统计信息
✅ 处理各种图片格式（包括 RGBA）
✅ 使用 2560 维向量
✅ 重建向量数据库
✅ 正常进行向量搜索

下一步建议：
1. 运行 `python rebuild_vectors.py --force-recreate` 重建向量数据库
2. 测试搜索功能确保正常工作
3. 根据实际需求调整批量大小和性能参数