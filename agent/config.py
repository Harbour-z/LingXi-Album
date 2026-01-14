"""
Agent配置文件
"""

import os
from pathlib import Path

# 后端服务配置
ALBUM_API_BASE_URL = os.getenv("ALBUM_API_URL", "http://localhost:8000/api/v1")
ALBUM_API_TIMEOUT = 30  # 秒

# LLM模型配置
LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")  # 华为云API密钥
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 2048

# Agent配置
MAX_ITERATIONS = 10  # 最大推理轮数
ENABLE_MEMORY = True  # 是否启用对话记忆
MEMORY_SIZE = 100  # 对话历史记录数

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = Path(__file__).parent / "logs" / "agent.log"

# 确保日志目录存在
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
