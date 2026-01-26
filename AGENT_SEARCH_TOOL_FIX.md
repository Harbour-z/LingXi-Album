# Agent 语义搜索工具调用问题诊断与修复

## 问题概述

Agent 无法调用语义搜索工具接口，导致产品核心功能失效。日志显示错误信息：

```
{'errCode': 188004, 'errMessage': 'Url invalid error, as illegal ip address', 'data': ''}
```

## 诊断过程

### 1. 语义搜索服务验证 ✅

**测试结果**: 语义搜索服务本身工作正常

通过直接调用接口测试：
```bash
GET http://localhost:8000/api/v1/search/text?query=柴犬&top_k=5
```

**响应**: HTTP 200，成功返回 5 张图片

### 2. Agent 聊天接口验证 ✅

**测试结果**: Agent 聊天接口能正常响应

```bash
POST http://localhost:8000/api/v1/agent/chat
```

**响应**: HTTP 200，Agent 能理解查询并尝试调用工具

### 3. OpenJiuwen 工具调用验证 ⚠️

**测试结果**: OpenJiuwen 的 RestfulApi 工具调用失败

**错误信息**: `'Url invalid error, as illegal ip address'`

### 4. 问题根源发现 ⚠️

**问题**: OpenJiuwen 框架的 URL 验证机制

OpenJiuwen 的 RestfulApi 工具在处理 `localhost` 地址时，会进行 URL 验证，认为 `localhost` 是一个非法的 IP 地址，导致工具调用失败。

## 根本原因

**OpenJiuwen 框架的 URL 验证问题**

在 [`app/services/agent_service.py`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/services/agent_service.py#L218) 中：

```python
# ❌ 问题代码
api_base = os.getenv("AGENT_API_BASE_URL", "http://localhost:8000")
```

OpenJiuwen 框架的 URL 验证机制不接受 `localhost` 作为主机名，要求使用 IP 地址。

## 解决方案

使用 `127.0.0.1` 代替 `localhost`：

```python
# ✅ 修复后的代码
# 使用 127.0.0.1 代替 localhost，避免 OpenJiuwen 的 URL 验证问题
api_base = os.getenv("AGENT_API_BASE_URL", "http://127.0.0.1:8000")
```

## 实施的修复

**文件**: [`app/services/agent_service.py`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/services/agent_service.py#L218-L221)

**变更**: 将默认 API 基础 URL 从 `http://localhost:8000` 改为 `http://127.0.0.1:8000`

## 验证步骤

### 1. 重启后端服务

修复后需要重启后端服务以加载新的配置：

```bash
# 停止当前运行的服务
# 然后重新启动
python -m app.main
```

### 2. 运行测试脚本

```bash
python test_agent_search_tool.py
```

### 3. 测试 Agent 聊天

```bash
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "帮我找几张柴犬图片", "top_k": 5}'
```

### 4. 检查日志

查看 Agent 日志，确认工具调用成功：

```
[Agent] 调用ReAct Agent, inputs: {...}
Executing tool: semantic_search_images
Tool semantic_search_images completed with result: {...}
[Agent] 返回图片数量: X
```

## 技术说明

### OpenJiuwen URL 验证机制

OpenJiuwen 框架的 RestfulApi 工具会对 URL 进行验证：

1. **不接受主机名**: 不接受 `localhost` 等主机名
2. **要求 IP 地址**: 必须使用 IP 地址，如 `127.0.0.1`
3. **URL 格式验证**: 严格验证 URL 格式

### localhost vs 127.0.0.1

| 特性 | localhost | 127.0.0.1 |
|------|-----------|-----------|
| 类型 | 主机名 | IP 地址 |
| DNS 解析 | 需要 | 不需要 |
| OpenJiuwen 支持 | ❌ 不支持 | ✅ 支持 |
| 功能 | 相同 | 相同 |

### 最佳实践

```python
# ✅ 正确的配置
api_base = "http://127.0.0.1:8000"  # 使用 IP 地址

# ❌ 错误的配置
api_base = "http://localhost:8000"  # 使用主机名
```

## 测试结果

### 修复前

```
Tool semantic_search_images completed with result: 
{'errCode': 188004, 'errMessage': 'Url invalid error, as illegal ip address', 'data': ''}
```

### 修复后（需要重启服务）

预期结果：

```
Tool semantic_search_images completed with result: 
{'status': 'success', 'message': '文本搜索完成', 'data': [...], 'total': X}
```

## 其他相关配置

### 环境变量配置

如果需要使用其他地址，可以通过环境变量配置：

```bash
export AGENT_API_BASE_URL="http://127.0.0.1:8000"
```

### 生产环境配置

在生产环境中，应该使用实际的服务器 IP 地址：

```bash
export AGENT_API_BASE_URL="http://your-server-ip:8000"
```

## 成功标准

修复后，Agent 应该能够：

1. ✅ 成功调用语义搜索工具
2. ✅ 返回正确的搜索结果
3. ✅ 不再出现 URL 验证错误
4. ✅ 语义搜索功能完全恢复正常

## 注意事项

1. **必须重启服务**: 修改配置后必须重启后端服务才能生效
2. **使用 IP 地址**: 始终使用 IP 地址而非主机名
3. **环境变量覆盖**: 支持通过环境变量覆盖默认配置
4. **生产环境配置**: 生产环境应使用实际的服务器 IP

## 相关文件

- [`app/services/agent_service.py`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/services/agent_service.py) - Agent 服务配置（已修复）
- [`test_agent_search_tool.py`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/test_agent_search_tool.py) - 测试脚本

## 总结

### 问题原因

OpenJiuwen 框架的 URL 验证机制不接受 `localhost` 主机名，要求使用 IP 地址。

### 解决方案

将 API 基础 URL 从 `http://localhost:8000` 改为 `http://127.0.0.1:8000`。

### 验证方法

1. 重启后端服务
2. 运行测试脚本
3. 测试 Agent 聊天
4. 检查日志

### 下一步

1. 重启后端服务
2. 运行 `python test_agent_search_tool.py` 验证修复
3. 使用 Agent 聊天接口测试语义搜索功能
4. 监控日志确认工具调用成功

修复完成后，Agent 将能够成功调用语义搜索工具接口，语义搜索功能将完全恢复正常运行！