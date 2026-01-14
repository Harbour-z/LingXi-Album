#!/bin/bash

# 智慧相册系统完整启动脚本

echo "========================================="
echo "智慧相册系统启动脚本"
echo "========================================="

# 检查后端服务是否运行
check_backend() {
    echo "检查后端服务状态..."
    if curl -s http://localhost:8000/status > /dev/null; then
        echo "✅ 后端服务已运行"
        return 0
    else
        echo "❌ 后端服务未运行"
        return 1
    fi
}

# 启动后端服务
start_backend() {
    echo ""
    echo "启动后端API服务..."
    cd "$(dirname "$0")"
    
    # 检查Python环境
    if ! command -v python &> /dev/null; then
        echo "❌ 未找到Python，请先安装Python 3.11+"
        exit 1
    fi
    
    # 启动服务（后台运行）
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "后端服务启动中... (PID: $BACKEND_PID)"
    
    # 等待服务启动
    echo "等待服务初始化..."
    sleep 5
    
    if check_backend; then
        echo "✅ 后端服务启动成功"
        echo "API文档: http://localhost:8000/docs"
    else
        echo "❌ 后端服务启动失败，请查看日志: logs/backend.log"
        exit 1
    fi
}

# 启动Agent
start_agent() {
    echo ""
    echo "启动OpenJiuwen Agent..."
    
    # 设置环境变量
    export ALBUM_API_URL="http://localhost:8000/api/v1"
    export LLM_MODEL="qwen-plus"
    # export LLM_API_KEY="your-api-key"  # 取消注释并填写API密钥
    
    # 启动Agent交互式界面
    python agent/agent_main.py
}

# 主流程
main() {
    # 创建日志目录
    mkdir -p logs
    
    # 检查或启动后端
    if ! check_backend; then
        start_backend
    fi
    
    # 启动Agent
    start_agent
}

# 运行
main
