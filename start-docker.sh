#!/bin/bash

# 智慧相册 Docker 快速启动脚本

echo "🚀 智慧相册 Docker 启动脚本"
echo "================================"

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未安装 Docker，请先安装 Docker Desktop"
    echo "   下载地址: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    echo "❌ 错误: Docker 未运行，请启动 Docker Desktop"
    exit 1
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件，复制 .env.template..."
    cp .env.template .env
    echo ""
    echo "📝 请编辑 .env 文件，填入你的 API Keys:"
    echo "   - ALIYUN_EMBEDDING_API_KEY"
    echo "   - OPENAI_API_KEY"
    echo "   - VISION_MODEL_API_KEY"
    echo ""
    read -p "已配置完成？按回车继续..."
fi

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 检查必要的 API Key
if [ -z "$ALIYUN_EMBEDDING_API_KEY" ] || [ -z "$OPENAI_API_KEY" ] || [ -z "$VISION_MODEL_API_KEY" ]; then
    echo "❌ 错误: 缺少必要的 API Keys，请检查 .env 文件"
    exit 1
fi

# 构建前端（如果需要）
if [ ! -d "frontend/dist" ]; then
    echo "📦 构建前端..."
    cd frontend && npm install && npm run build && cd ..
fi

echo ""
echo "🔨 构建 Docker 镜像..."
docker-compose build

echo ""
echo "🚀 启动服务..."
docker-compose up -d

echo ""
echo "⏳ 等待服务启动（约30秒）..."
sleep 30

# 检查服务状态
if curl -s http://localhost:7860/health > /dev/null; then
    echo ""
    echo "✅ 服务启动成功！"
    echo "================================"
    echo "🌐 访问地址: http://localhost:7860"
    echo "📊 API文档: http://localhost:7860/docs"
    echo ""
    echo "📝 查看日志: docker-compose logs -f"
    echo "🛑 停止服务: docker-compose down"
    echo ""
    
    # 尝试自动打开浏览器
    if command -v open &> /dev/null; then
        open http://localhost:7860
    elif command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:7860
    fi
else
    echo ""
    echo "⚠️  服务可能未完全启动，请稍等片刻或查看日志:"
    echo "   docker-compose logs -f"
fi
