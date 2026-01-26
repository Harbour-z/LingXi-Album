# Agent 工具调用问题诊断与修复方案

## 问题分析

根据对话记录，用户请求"查找去年的海边照片"和"2023年7月"时，agent 返回了关于系统时间、网络连接等错误信息，而不是成功调用工具进行照片搜索。

## 诊断结果

### 1. 工具注册问题 ✅ 已确认正常

**检查结果**：工具注册正确

在 [`app/services/agent_service.py`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/services/agent_service.py#L175-L373) 中，已正确注册了以下工具：

- ✅ `semantic_search_images` - 语义相似度检索
- ✅ `search_by_image_id` - 以图搜图
- ✅ `meta_search_images` - 元数据检索
- ✅ `meta_search_hybrid` - 元数据+语义混合检索
- ✅ `get_current_time` - 获取当前时间
- ✅ `get_photo_meta_schema` - 获取元数据字段定义

### 2. 工具调用逻辑问题 ⚠️ 发现潜在问题

**问题 1**：API 端点配置可能不正确

在 [`agent_service.py#L193`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/services/agent_service.py#L193) 中，API 基础 URL 硬编码为：

```python
api_base = "http://localhost:8000"
```

这可能导致：
- 如果后端服务运行在不同端口，工具调用会失败
- 如果在 Docker 或生产环境中，localhost 可能无法访问

**问题 2**：工具参数配置可能不匹配

检查工具参数配置，发现：
- `semantic_search_images` 使用 GET 方法，但参数可能需要 POST
- 某些工具的 `method="Query"` 配置可能不正确

**问题 3**：错误处理不够详细

在 [`agent.py#L494`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/routers/agent.py#L494) 中，Agent 执行失败时的错误处理：

```python
except Exception as e:
    # Agent 执行失败，回退到规则引擎
    import logging
    logging.getLogger(__name__).error(f"Agent execution failed, falling back to rule-based engine: {e}")
```

这里只记录了错误，但没有向用户返回具体的错误信息。

### 3. 时间获取工具问题 ✅ 已确认正常

**检查结果**：时间获取工具实现正确

在 [`agent.py#L609`](file:///Users/harbour/Desktop/huawei-intern-2026/ImgEmbedding2VecDB/app/routers/agent.py#L609) 中，`get_current_time` 端点实现正确：

```python
@router.get("/time", summary="获取当前时间")
async def get_current_time():
    from datetime import datetime
    return {
        "status": "success",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
```

## 修复方案

### 修复 1：动态配置 API 基础 URL

**文件**：`app/services/agent_service.py`

**问题**：硬编码的 `localhost:8000` 在不同环境下可能无法访问

**解决方案**：从配置中读取 API 基础 URL

```python
def _register_core_tools(self):
    """注册Agent可用工具"""
    settings = get_settings()
    
    # 从配置中读取 API 基础 URL，支持环境变量覆盖
    api_base = os.getenv("AGENT_API_BASE_URL", "http://localhost:8000")
    api_prefix = "/api/v1"
    
    logger.info(f"Agent工具注册，API基础URL: {api_base}")
    
    # ... 其余工具注册代码
```

### 修复 2：增强错误处理和日志

**文件**：`app/routers/agent.py`

**问题**：Agent 执行失败时，用户看不到具体错误

**解决方案**：返回详细的错误信息

```python
try:
    agent_result = await agent_svc.chat(message.query, session_id)
    response = agent_result.get("answer", "")
    images = agent_result.get("images") or []
    
    return ChatResponse(
        session_id=session_id,
        answer=response,
        intent="auto",
        optimized_query=message.query,
        results={"total": len(images), "images": images} if images else None,
        suggestions=[],
        timestamp=datetime.now().isoformat()
    )
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Agent执行失败: {e}", exc_info=True)
    
    # 返回详细的错误信息
    error_message = f"抱歉，智慧相册Agent暂时无法响应。错误信息: {str(e)}"
    
    return ChatResponse(
        session_id=session_id,
        answer=error_message,
        intent="error",
        optimized_query=message.query,
        results=None,
        suggestions=["请稍后再试", "检查网络连接", "联系管理员"],
        timestamp=datetime.now().isoformat()
    )
```

### 修复 3：添加工具调用日志

**文件**：`app/services/agent_service.py`

**问题**：无法追踪工具调用的详细过程

**解决方案**：在关键节点添加日志

```python
async def chat(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """使用ReAct Agent进行对话"""
    conversation_id = session_id or "default_session"
    
    logger.info(f"[Agent] 开始处理查询: {query}, session_id: {session_id}")
    
    try:
        if not self._agent:
            logger.warning("[Agent] ReAct Agent未初始化，使用规则引擎回退")
            # ...
        
        logger.info(f"[Agent] 调用ReAct Agent, conversation_id: {conversation_id}")
        result = await self._agent.invoke(inputs)
        logger.info(f"[Agent] ReAct Agent返回结果: {result.get('output', '')[:100]}...")
        
        # ...
        
    except Exception as e:
        logger.error(f"[Agent] 执行异常: {e}", exc_info=True)
        # ...
```

### 修复 4：验证工具端点可用性

**文件**：`app/services/agent_service.py`

**问题**：工具注册时没有验证端点是否可用

**解决方案**：添加端点健康检查

```python
def _verify_tool_endpoint(self, tool: RestfulApi) -> bool:
    """验证工具端点是否可用"""
    import httpx
    
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(tool.path, headers=tool.headers)
            if response.status_code in [200, 404]:  # 404 也算端点存在
                logger.info(f"[Agent] 工具端点验证成功: {tool.name} - {tool.path}")
                return True
            else:
                logger.warning(f"[Agent] 工具端点返回异常状态: {tool.name} - {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"[Agent] 工具端点验证失败: {tool.name} - {e}")
        return False

def _register_core_tools(self):
    """注册Agent可用工具"""
    # ... 工具注册代码
    
    # 验证工具端点
    for tool in self._tools:
        self._verify_tool_endpoint(tool)
```

### 修复 5：改进 Agent 提示词

**文件**：`app/services/agent_service.py`

**问题**：Agent 可能没有正确理解如何处理时间相关的查询

**解决方案**：增强系统提示词

```python
prompt_template=[
    {
        "role": "system",
        "content": (
            "You are a helpful smart album assistant for a photo album. "
            "Each photo has metadata fields available for filtering: filename, file_size, width, height, format, created_at (ISO datetime), tags (list of strings), description, extra (object). "
            
            "IMPORTANT INSTRUCTIONS FOR TIME-BASED QUERIES:\n"
            "1. When user asks for photos from a specific time period (e.g., 'last year', '2023年7月', 'yesterday'), "
            "   first use get_current_time to understand the current date, then calculate the target date range.\n"
            "2. For date-based searches, use meta_search_images with the appropriate date_text parameter.\n"
            "3. Supported date formats: '1.18', '1月18日', '2026-01-18', '2023.7', '2023年7月'.\n"
            "4. If the user provides both date and semantic description (e.g., '2023年7月 海边'), use meta_search_hybrid.\n"
            
            "TOOL USAGE GUIDELINES:\n"
            "- Use semantic_search_images when the user describes visual/semantic content and wants similarity matching without metadata constraints.\n"
            "- Use meta_search_images when the user wants to filter by metadata only (date, tags, filename, etc.).\n"
            "- Use meta_search_hybrid when the user mixes metadata filtering + semantic description.\n"
            "- Use search_by_image_id when user provides an image ID for similar image search.\n"
            "- Use get_current_time when user asks for time or when you need to calculate date ranges.\n"
            "- Use get_photo_meta_schema when user needs to understand available metadata fields.\n"
            
            "ERROR HANDLING:\n"
            "- If a tool call fails, try to understand the error and provide helpful feedback to the user.\n"
            "- If you cannot find photos matching the criteria, suggest alternative search terms or ask for clarification.\n"
            "- Always be specific about what you searched for and what results you found."
        )
    }
]
```

## 验证步骤

### 1. 测试时间获取工具

```bash
curl http://localhost:8000/api/v1/agent/time
```

预期响应：
```json
{
  "status": "success",
  "time": "2026-01-25 10:30:00"
}
```

### 2. 测试元数据搜索工具

```bash
curl "http://localhost:8000/api/v1/search/meta?date_text=1.18&top_k=5"
```

预期响应：
```json
{
  "status": "success",
  "message": "找到 X 张相关图片",
  "data": [...],
  "total": X
}
```

### 3. 测试混合搜索工具

```bash
curl "http://localhost:8000/api/v1/search/meta/hybrid?date_text=1.18&query=海边&top_k=5"
```

预期响应：
```json
{
  "status": "success",
  "message": "找到 X 张相关图片",
  "data": [...],
  "total": X
}
```

### 4. 测试 Agent 聊天接口

```bash
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "查找去年的海边照片", "top_k": 10}'
```

预期响应：
```json
{
  "session_id": "...",
  "answer": "为您找到了 X 张去年的海边照片...",
  "intent": "auto",
  "optimized_query": "查找去年的海边照片",
  "results": {
    "total": X,
    "images": [...]
  },
  "suggestions": [...],
  "timestamp": "2026-01-25T10:30:00"
}
```

## 成功标准

修复后，agent 应该能够：

1. ✅ 正确识别时间相关的查询（"去年的海边照片"、"2023年7月"）
2. ✅ 成功调用 `get_current_time` 工具获取当前时间
3. ✅ 根据当前时间计算目标日期范围
4. ✅ 调用 `meta_search_images` 或 `meta_search_hybrid` 工具进行搜索
5. ✅ 返回找到的照片列表或明确的"未找到"提示
6. ✅ 提供有用的后续建议
7. ✅ 在工具调用失败时，返回具体的错误信息而非泛泛的系统错误

## 下一步行动

1. 实施上述修复方案
2. 重启后端服务
3. 运行验证步骤
4. 使用实际查询进行端到端测试
5. 监控日志，确保工具调用正常工作