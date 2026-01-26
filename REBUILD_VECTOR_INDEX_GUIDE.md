# 向量索引重建脚本使用说明

## 概述

`rebuild_vector_index.py` 是一个用于通过后端 API 重新构建向量索引的脚本。它会遍历 storage 中所有已存储的图像，调用后端 API 生成 Embedding 向量，并自动更新向量数据库索引。

## 功能特性

- ✅ 自动遍历 storage 中所有图像文件
- ✅ 调用后端 API 生成图像 Embedding
- ✅ 支持并发处理，提高效率
- ✅ 智能跳过已索引的图像
- ✅ 指数退避重试机制
- ✅ 速率限制处理
- ✅ 详细的进度显示和统计
- ✅ 失败记录保存
- ✅ 可配置的参数

## 环境依赖

### Python 依赖

```bash
pip install httpx pillow
```

### 测试依赖（可选）

```bash
pip install pytest pytest-asyncio
```

### 后端服务要求

- 后端 API 服务必须运行在指定地址（默认 `http://localhost:8000`）
- 需要以下 API 端点可用：
  - `POST /api/v1/embedding/image` - 生成图像 Embedding
  - `GET /api/v1/vectors/{image_id}` - 检查图像是否已索引

## 配置参数

### 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--api-url` | string | `http://localhost:8000` | 后端 API 基础 URL |
| `--storage-path` | string | `./storage` | 存储路径 |
| `--max-concurrent` | int | `5` | 最大并发数 |
| `--batch-size` | int | `10` | 批量处理大小 |
| `--max-retries` | int | `3` | 最大重试次数 |
| `--retry-delay` | float | `1.0` | 重试延迟（秒） |
| `--force-reindex` | flag | `False` | 强制重新索引所有图像 |
| `--no-skip-indexed` | flag | `False` | 不跳过已索引的图像 |
| `--limit` | int | `None` | 限制处理的图像数量 |
| `--verbose` | flag | `False` | 详细输出 |

## 使用示例

### 基本使用

#### 1. 重建所有图像（跳过已索引的）

```bash
python rebuild_vector_index.py
```

这是最常用的方式，会：
- 扫描 `./storage` 目录中的所有图像
- 跳过已经索引的图像
- 只处理新图像

#### 2. 强制重新索引所有图像

```bash
python rebuild_vector_index.py --force-reindex
```

这会：
- 处理所有图像，包括已索引的
- 重新生成所有 Embedding
- 更新所有向量索引

#### 3. 限制处理数量（用于测试）

```bash
python rebuild_vector_index.py --limit 10
```

只处理前 10 张图像，适合测试和调试。

#### 4. 自定义并发数和批量大小

```bash
python rebuild_vector_index.py --max-concurrent 10 --batch-size 20
```

提高并发数和批量大小可以加快处理速度，但会增加服务器负载。

#### 5. 指定自定义存储路径和 API URL

```bash
python rebuild_vector_index.py --storage-path ./my_storage --api-url http://localhost:8080
```

适用于非默认配置的环境。

#### 6. 详细输出模式

```bash
python rebuild_vector_index.py --verbose
```

显示详细的调试信息，包括每个 API 请求的详情。

### 高级使用

#### 1. 不跳过已索引的图像

```bash
python rebuild_vector_index.py --no-skip-indexed
```

即使图像已索引，也会重新处理（但不强制重新索引，只是重新生成 Embedding）。

#### 2. 调整重试策略

```bash
python rebuild_vector_index.py --max-retries 5 --retry-delay 2.0
```

增加重试次数和延迟，适用于网络不稳定的环境。

#### 3. 组合多个参数

```bash
python rebuild_vector_index.py \
  --api-url http://localhost:8080 \
  --storage-path ./production_storage \
  --max-concurrent 8 \
  --batch-size 15 \
  --max-retries 4 \
  --retry-delay 1.5 \
  --verbose
```

## 输出示例

### 正常输出

```
2024-01-25 10:00:00 - __main__ - INFO - ============================================================
2024-01-25 10:00:00 - __main__ - INFO - 开始重建向量索引
2024-01-25 10:00:00 - __main__ - INFO - ============================================================
2024-01-25 10:00:00 - __main__ - INFO - 扫描存储路径: ./storage
2024-01-25 10:00:00 - __main__ - INFO - 找到 100 张图像
2024-01-25 10:00:00 - __main__ - INFO - 处理批次 1/10 (1-10/100)
2024-01-25 10:00:01 - __main__ - INFO - 处理图像: image1.jpg (abc123)
2024-01-25 10:00:02 - __main__ - INFO - ✓ 成功: abc123
2024-01-25 10:00:02 - __main__ - INFO - 处理图像: image2.png (def456)
2024-01-25 10:00:03 - __main__ - INFO - ✓ 成功: def456
...
2024-01-25 10:01:30 - __main__ - INFO - 进度: 100/100 (100.0%) | 成功: 95 | 失败: 3 | 跳过: 2
2024-01-25 10:01:30 - __main__ - INFO - ============================================================
2024-01-25 10:01:30 - __main__ - INFO - 重建完成
2024-01-25 10:01:30 - __main__ - INFO - ============================================================
2024-01-25 10:01:30 - __main__ - INFO - 总图像数: 100
2024-01-25 10:01:30 - __main__ - INFO - 成功: 95
2024-01-25 10:01:30 - __main__ - INFO - 失败: 3
2024-01-25 10:01:30 - __main__ - INFO - 跳过: 2
2024-01-25 10:01:30 - __main__ - INFO - 耗时: 90.50 秒
2024-01-25 10:01:30 - __main__ - INFO - 平均每张: 0.91 秒
2024-01-25 10:01:30 - __main__ - INFO - 失败记录已保存到: failed_images_20240125_100130.json
```

### 错误处理输出

```
2024-01-25 10:00:05 - __main__ - WARNING - 速率限制，等待 2.0 秒后重试...
2024-01-25 10:00:08 - __main__ - ERROR - API 调用失败: 500 - Internal Server Error
2024-01-25 10:00:10 - __main__ - ERROR - ✗ 失败: xyz789
```

## 失败记录

脚本会自动保存失败的图像记录到 JSON 文件：

```json
[
  {
    "id": "xyz789",
    "filename": "image3.jpg",
    "path": "/path/to/image3.jpg",
    "error": "Internal Server Error"
  },
  {
    "id": "uvw012",
    "filename": "image4.png",
    "path": "/path/to/image4.png",
    "error": "Timeout"
  }
]
```

文件名格式：`failed_images_YYYYMMDD_HHMMSS.json`

## 性能优化建议

### 1. 并发数调整

- **低配置服务器**：`--max-concurrent 2-3`
- **中等配置服务器**：`--max-concurrent 5-8`
- **高配置服务器**：`--max-concurrent 10-20`

### 2. 批量大小调整

- **小批量（稳定）**：`--batch-size 5-10`
- **中批量（平衡）**：`--batch-size 10-20`
- **大批量（快速）**：`--batch-size 20-50`

### 3. 重试策略

- **稳定网络**：`--max-retries 2 --retry-delay 0.5`
- **不稳定网络**：`--max-retries 5 --retry-delay 2.0`

## 故障排除

### 问题 1: 连接被拒绝

**错误信息**：
```
httpx.ConnectError: [Errno 61] Connection refused
```

**解决方案**：
1. 确认后端服务正在运行
2. 检查 `--api-url` 参数是否正确
3. 检查防火墙设置

### 问题 2: 速率限制

**错误信息**：
```
WARNING - 速率限制，等待 X 秒后重试...
```

**解决方案**：
1. 降低 `--max-concurrent` 参数
2. 增加 `--retry-delay` 参数
3. 联系后端管理员提高速率限制

### 问题 3: 超时错误

**错误信息**：
```
ERROR - 请求超时: image_id
```

**解决方案**：
1. 检查网络连接
2. 增加 `--retry-delay` 参数
3. 检查后端服务性能

### 问题 4: 图像不存在

**错误信息**：
```
WARNING - 图像不存在: image_id
```

**解决方案**：
1. 检查 `--storage-path` 参数是否正确
2. 确认图像文件确实存在
3. 检查文件权限

## 测试

### 运行单元测试

```bash
pytest test_rebuild_vector_index.py -v
```

### 运行集成测试

```bash
pytest test_rebuild_vector_index.py::TestIntegration -v -s
```

### 测试覆盖率

```bash
pytest test_rebuild_vector_index.py --cov=rebuild_vector_index --cov-report=html
```

## 最佳实践

### 1. 首次使用

```bash
# 先用小批量测试
python rebuild_vector_index.py --limit 5 --verbose

# 确认无误后，处理全部
python rebuild_vector_index.py
```

### 2. 定期更新

```bash
# 只处理新图像（跳过已索引的）
python rebuild_vector_index.py
```

### 3. 完全重建

```bash
# 强制重新索引所有图像
python rebuild_vector_index.py --force-reindex
```

### 4. 监控和日志

```bash
# 保存日志到文件
python rebuild_vector_index.py --verbose 2>&1 | tee rebuild.log
```

## 注意事项

1. **API 可用性**：确保后端 API 服务正常运行
2. **网络稳定性**：不稳定的网络可能导致大量重试
3. **服务器负载**：高并发可能增加服务器负载
4. **存储空间**：确保有足够的磁盘空间
5. **权限问题**：确保脚本有读取存储目录的权限

## 与其他工具的对比

| 特性 | rebuild_vector_index.py | rebuild_vectors.py |
|------|------------------------|-------------------|
| 调用方式 | 通过 API | 直接调用服务 |
| 依赖 | 需要 API 服务 | 需要本地服务 |
| 并发控制 | ✅ 支持 | ❌ 不支持 |
| 重试机制 | ✅ 指数退避 | ❌ 简单重试 |
| 进度显示 | ✅ 详细 | ✅ 基础 |
| 失败记录 | ✅ JSON 文件 | ✅ 日志 |
| 跨平台 | ✅ 是 | ✅ 是 |

## 总结

`rebuild_vector_index.py` 是一个功能完善的向量索引重建工具，具有以下优势：

- 🚀 **高效**：支持并发处理，提高处理速度
- 🔄 **可靠**：智能重试机制，处理网络问题
- 📊 **透明**：详细的进度显示和统计
- 🛠️ **灵活**：可配置的参数，适应不同场景
- 🧪 **可测试**：完整的单元测试覆盖

适用于生产环境的向量索引重建任务。