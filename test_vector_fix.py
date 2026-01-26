"""
测试向量数据库修复和重建功能
"""

import sys
from pathlib import Path

app_path = Path(__file__).parent / "app"
sys.path.insert(0, str(app_path.parent))

from app.services import get_vector_db_service, get_embedding_service
from app.config import get_settings

def test_collection_info():
    """测试集合信息获取"""
    print("=" * 60)
    print("测试 1: 集合信息获取")
    print("=" * 60)
    
    try:
        vector_db_svc = get_vector_db_service()
        settings = get_settings()
        
        # 初始化
        vector_db_svc.initialize(
            mode=settings.QDRANT_MODE,
            path=settings.QDRANT_PATH,
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            api_key=settings.QDRANT_API_KEY,
            collection_name=settings.QDRANT_COLLECTION_NAME,
            vector_dimension=settings.VECTOR_DIMENSION
        )
        
        # 获取集合信息
        info = vector_db_svc.get_collection_info()
        
        print("✓ 集合信息获取成功")
        print(f"  集合名称: {info['name']}")
        print(f"  向量数量: {info['vectors_count']}")
        print(f"  点数量: {info['points_count']}")
        print(f"  状态: {info['status']}")
        print(f"  向量维度: {info['vector_dimension']}")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ 集合信息获取失败: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False

def test_embedding_service():
    """测试 Embedding 服务"""
    print("=" * 60)
    print("测试 2: Embedding 服务")
    print("=" * 60)
    
    try:
        embedding_svc = get_embedding_service()
        embedding_svc.initialize()
        
        # 测试文本嵌入
        text = "测试文本"
        embedding = embedding_svc.generate_text_embedding(text)
        
        print("✓ 文本嵌入生成成功")
        print(f"  文本: {text}")
        print(f"  向量维度: {len(embedding)}")
        print(f"  前5个值: {embedding[:5]}")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ Embedding 服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False

def test_vector_count():
    """测试向量计数"""
    print("=" * 60)
    print("测试 3: 向量计数")
    print("=" * 60)
    
    try:
        vector_db_svc = get_vector_db_service()
        
        count = vector_db_svc.count()
        
        print("✓ 向量计数成功")
        print(f"  总向量数: {count}")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ 向量计数失败: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("向量数据库修复和重建功能测试")
    print("=" * 60)
    print()
    
    results = []
    
    # 测试 1: 集合信息获取
    results.append(("集合信息获取", test_collection_info()))
    
    # 测试 2: Embedding 服务
    results.append(("Embedding 服务", test_embedding_service()))
    
    # 测试 3: 向量计数
    results.append(("向量计数", test_vector_count()))
    
    # 输出测试结果
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    print()
    
    # 检查是否所有测试都通过
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("✓ 所有测试通过！")
        print("\n下一步:")
        print("1. 如果需要重建向量数据库，运行: python rebuild_vectors.py --force-recreate")
        print("2. 或者运行: python rebuild_vectors.py (保留现有数据)")
    else:
        print("✗ 部分测试失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()