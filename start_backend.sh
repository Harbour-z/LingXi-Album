#!/bin/bash

# 停止现有服务
echo "停止现有服务..."
pkill -f "python.*main.py" || true
pkill -f "uvicorn" || true
sleep 2

# 启动后端服务
echo "启动后端服务..."
cd "$(dirname "$0")"
python -m app.main &
echo "后端服务已启动，PID: $!"

# 等待服务启动
echo "等待服务启动..."
sleep 5

# 检查服务状态
curl -s http://localhost:8000/health
echo ""
