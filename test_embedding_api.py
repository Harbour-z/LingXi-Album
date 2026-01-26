"""
测试阿里云 Embedding API 功能（使用 DashScope SDK）
"""

import sys
from pathlib import Path

app_path = Path(__file__).parent / "app"
sys.path.insert(0, str(app_path.parent))

from app.services.embedding_service import get_embedding_service
from app.config import get_settings

def test_api_config():
    """测试 API 配置"""
    settings = get_settings()
    
    print("=" * 60)
    print("API 配置检查")
    print("=" * 60)
    print(f"EMBEDDING_API_PROVIDER: {settings.EMBEDDING_API_PROVIDER}")
    print(f"ALIYUN_EMBEDDING_MODEL_NAME: {settings.ALIYUN_EMBEDDING_MODEL_NAME}")
    print(f"ALIYUN_EMBEDDING_DIMENSION: {settings.ALIYUN_EMBEDDING_DIMENSION}")
    print(f"ALIYUN_EMBEDDING_API_KEY: {'已配置' if settings.ALIYUN_EMBEDDING_API_KEY else '未配置'}")
    print()

def test_embedding_service_init():
    """测试 Embedding 服务初始化"""
    print("=" * 60)
    print("测试 Embedding 服务初始化")
    print("=" * 60)
    
    embedding_service = get_embedding_service()
    
    try:
        embedding_service.initialize()
        print(f"✓ Embedding 服务初始化成功")
        print(f"✓ Provider: {embedding_service._api_provider}")
        print(f"✓ 向量维度: {embedding_service.vector_dimension}")
        print()
        return True
    except Exception as e:
        print(f"✗ Embedding 服务初始化失败: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False

def test_text_embedding():
    """测试文本 Embedding"""
    print("=" * 60)
    print("测试文本 Embedding")
    print("=" * 60)
    
    embedding_service = get_embedding_service()
    
    try:
        embedding_service.initialize()
        text = "一张在海边日落的照片"
        embedding = embedding_service.generate_text_embedding(text)
        print(f"✓ 文本 Embedding 生成成功")
        print(f"  输入文本: {text}")
        print(f"  向量维度: {len(embedding)}")
        print(f"  前5个值: {embedding[:5]}")
        print()
        return embedding
    except Exception as e:
        print(f"✗ 文本 Embedding 生成失败: {e}")
        import traceback
        traceback.print_exc()
        print()
        return None

def test_batch_embeddings():
    """测试批量 Embedding"""
    print("=" * 60)
    print("测试批量 Embedding")
    print("=" * 60)
    
    embedding_service = get_embedding_service()
    
    try:
        embedding_service.initialize()
        inputs = [
            {"text": "海边的风景照片"},
            {"text": "红色跑车的图片"},
            {"text": "家庭聚餐的照片"}
        ]
        embeddings = embedding_service.generate_embeddings_batch(inputs)
        print(f"✓ 批量 Embedding 生成成功")
        print(f"  输入数量: {len(inputs)}")
        print(f"  输出数量: {len(embeddings)}")
        print(f"  每个向量维度: {len(embeddings[0]) if embeddings else 0}")
        print()
        return embeddings
    except Exception as e:
        print(f"✗ 批量 Embedding 生成失败: {e}")
        import traceback
        traceback.print_exc()
        print()
        return None

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("阿里云 Embedding API 功能测试（DashScope SDK）")
    print("=" * 60)
    print()
    
    # 1. 检查配置
    test_api_config()
    
    # 2. 测试服务初始化
    if not test_embedding_service_init():
        print("服务初始化失败，跳过后续测试")
        return
    
    # 3. 测试文本 Embedding
    test_text_embedding()
    
    # 4. 测试批量 Embedding
    test_batch_embeddings()
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
