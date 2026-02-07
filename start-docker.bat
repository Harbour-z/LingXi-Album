@echo off
chcp 65001 >nul
echo 🚀 智慧相册 Docker 启动脚本
echo ================================

:: 检查 Docker 是否安装
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未安装 Docker，请先安装 Docker Desktop
    echo    下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

:: 检查 Docker 是否运行
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: Docker 未运行，请启动 Docker Desktop
    pause
    exit /b 1
)

:: 检查 .env 文件
if not exist .env (
    echo ⚠️  未找到 .env 文件，复制 .env.template...
    copy .env.template .env
    echo.
    echo 📝 请编辑 .env 文件，填入你的 API Keys:
    echo    - ALIYUN_EMBEDDING_API_KEY
    echo    - OPENAI_API_KEY
    echo    - VISION_MODEL_API_KEY
    echo.
    pause
)

:: 构建前端（如果需要）
if not exist "frontend\dist" (
    echo 📦 构建前端...
    cd frontend
    call npm install
    call npm run build
    cd ..
)

echo.
echo 🔨 构建 Docker 镜像...
docker-compose build

echo.
echo 🚀 启动服务...
docker-compose up -d

echo.
echo ⏳ 等待服务启动（约30秒）...
timeout /t 30 /nobreak >nul

:: 检查服务状态
curl -s http://localhost:7860/health >nul 2>nul
if %errorlevel% equ 0 (
    echo.
    echo ✅ 服务启动成功！
    echo ================================
    echo 🌐 访问地址: http://localhost:7860
    echo 📊 API文档: http://localhost:7860/docs
    echo.
    echo 📝 查看日志: docker-compose logs -f
    echo 🛑 停止服务: docker-compose down
    echo.
    
    :: 自动打开浏览器
    start http://localhost:7860
) else (
    echo.
    echo ⚠️  服务可能未完全启动，请稍等片刻或查看日志:
    echo    docker-compose logs -f
)

pause
