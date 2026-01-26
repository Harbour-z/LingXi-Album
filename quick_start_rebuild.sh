#!/bin/bash

# 向量索引重建快速开始脚本

set -e

echo "============================================================"
echo "向量索引重建工具 - 快速开始"
echo "============================================================"
echo ""

# 检查 Python 版本
echo "检查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"
echo ""

# 安装依赖
echo "安装依赖..."
pip install -r requirements_rebuild.txt
echo ""

# 检查后端服务
echo "检查后端服务..."
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "✓ 后端服务运行正常"
else
    echo "⚠ 后端服务未运行或不可访问"
    echo "请确保后端服务在 http://localhost:8000 运行"
    echo ""
    read -p "是否继续? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo ""

# 运行测试
echo "运行单元测试..."
pytest test_rebuild_vector_index.py -v --tb=short
echo ""

# 询问是否开始重建
echo "============================================================"
echo "准备开始向量索引重建"
echo "============================================================"
echo ""
echo "可用选项:"
echo "1. 重建所有图像（跳过已索引的）"
echo "2. 强制重新索引所有图像"
echo "3. 限制处理数量（测试模式）"
echo "4. 自定义参数"
echo ""
read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "开始重建所有图像（跳过已索引的）..."
        python rebuild_vector_index.py
        ;;
    2)
        echo ""
        echo "开始强制重新索引所有图像..."
        python rebuild_vector_index.py --force-reindex
        ;;
    3)
        echo ""
        read -p "请输入限制数量: " limit
        echo "开始处理前 $limit 张图像..."
        python rebuild_vector_index.py --limit "$limit" --verbose
        ;;
    4)
        echo ""
        echo "自定义参数模式"
        read -p "API URL (默认: http://localhost:8000): " api_url
        api_url=${api_url:-http://localhost:8000}
        
        read -p "存储路径 (默认: ./storage): " storage_path
        storage_path=${storage_path:-./storage}
        
        read -p "最大并发数 (默认: 5): " max_concurrent
        max_concurrent=${max_concurrent:-5}
        
        read -p "批量大小 (默认: 10): " batch_size
        batch_size=${batch_size:-10}
        
        echo ""
        echo "开始重建..."
        python rebuild_vector_index.py \
            --api-url "$api_url" \
            --storage-path "$storage_path" \
            --max-concurrent "$max_concurrent" \
            --batch-size "$batch_size"
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "============================================================"
echo "重建完成！"
echo "============================================================"
echo ""
echo "下一步:"
echo "- 查看失败记录: cat failed_images_*.json"
echo "- 测试搜索功能: curl -X POST http://localhost:8000/api/v1/search/text -H 'Content-Type: application/json' -d '{\"query\": \"测试\", \"top_k\": 10}'"
echo "- 查看统计信息: curl http://localhost:8000/api/v1/vectors/stats/info"
echo ""