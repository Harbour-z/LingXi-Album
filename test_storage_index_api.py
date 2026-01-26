"""
API 路由验证脚本
测试 /api/v1/storage/index/all 接口是否可用
"""

import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health_check():
    """测试健康检查"""
    print("=" * 60)
    print("测试 1: 健康检查")
    print("=" * 60)
    
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=5.0)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 服务运行正常")
            print(f"  状态: {data.get('status')}")
            print(f"  版本: {data.get('version')}")
            return True
        else:
            print(f"✗ 失败: HTTP {response.status_code}")
            print(f"  响应: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False

def test_storage_stats():
    """测试存储统计"""
    print("\n" + "=" * 60)
    print("测试 2: 存储统计")
    print("=" * 60)
    
    try:
        response = httpx.get(f"{BASE_URL}/api/v1/storage/stats", timeout=10.0)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 存储统计获取成功")
            print(f"  状态: {data.get('status')}")
            stats = data.get('data', {})
            print(f"  总图片数: {stats.get('total_images', 0)}")
            print(f"  总大小: {stats.get('total_size', 0)} bytes")
            return True
        else:
            print(f"✗ 失败: HTTP {response.status_code}")
            print(f"  响应: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False

def test_list_images():
    """测试列出图片"""
    print("\n" + "=" * 60)
    print("测试 3: 列出图片")
    print("=" * 60)
    
    try:
        response = httpx.get(
            f"{BASE_URL}/api/v1/storage/images",
            params={"page": 1, "page_size": 5},
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 图片列表获取成功")
            print(f"  状态: {data.get('status')}")
            print(f"  总数: {data.get('total', 0)}")
            print(f"  当前页: {data.get('page', 0)}")
            
            images = data.get('data', [])
            if images:
                print(f"  图片数量: {len(images)}")
                for i, img in enumerate(images[:3]):
                    print(f"    {i+1}. {img.get('filename', 'N/A')}")
            
            return True
        else:
            print(f"✗ 失败: HTTP {response.status_code}")
            print(f"  响应: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False

def test_index_all():
    """测试索引所有图片"""
    print("\n" + "=" * 60)
    print("测试 4: 索引所有图片")
    print("=" * 60)
    
    try:
        response = httpx.post(
            f"{BASE_URL}/api/v1/storage/index/all",
            timeout=60.0  # 索引可能需要较长时间
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 索引所有图片成功")
            print(f"  状态: {data.get('status')}")
            print(f"  消息: {data.get('message')}")
            
            result_data = data.get('data', {})
            print(f"  已索引: {result_data.get('indexed', 0)}")
            print(f"  总数: {result_data.get('total', 0)}")
            
            return True
        else:
            print(f"✗ 失败: HTTP {response.status_code}")
            print(f"  响应: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False

def test_index_single():
    """测试索引单张图片"""
    print("\n" + "=" * 60)
    print("测试 5: 索引单张图片")
    print("=" * 60)
    
    # 先获取一张图片的 ID
    try:
        list_response = httpx.get(
            f"{BASE_URL}/api/v1/storage/images",
            params={"page": 1, "page_size": 1},
            timeout=10.0
        )
        
        if list_response.status_code != 200:
            print(f"✗ 无法获取图片列表")
            return False
        
        list_data = list_response.json()
        images = list_data.get('data', [])
        
        if not images:
            print(f"⚠ 没有可用的图片进行测试")
            return True
        
        image_id = images[0].get('id')
        print(f"  使用图片 ID: {image_id}")
        
        # 测试索引
        response = httpx.post(
            f"{BASE_URL}/api/v1/storage/index/{image_id}",
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 索引单张图片成功")
            print(f"  状态: {data.get('status')}")
            print(f"  消息: {data.get('message')}")
            return True
        else:
            print(f"✗ 失败: HTTP {response.status_code}")
            print(f"  响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False

def test_api_docs():
    """测试 API 文档"""
    print("\n" + "=" * 60)
    print("测试 6: API 文档")
    print("=" * 60)
    
    try:
        response = httpx.get(f"{BASE_URL}/docs", timeout=5.0)
        
        if response.status_code == 200:
            print(f"✓ API 文档可访问")
            print(f"  URL: {BASE_URL}/docs")
            return True
        else:
            print(f"✗ 失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("API 路由验证测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 基础 URL: {BASE_URL}")
    print()
    
    # 运行所有测试
    tests = [
        ("健康检查", test_health_check),
        ("存储统计", test_storage_stats),
        ("列出图片", test_list_images),
        ("索引所有图片", test_index_all),
        ("索引单张图片", test_index_single),
        ("API 文档", test_api_docs),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print()
    print(f"总计: {len(results)} 个测试")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    
    if failed == 0:
        print("\n✓ 所有测试通过！API 路由正常工作。")
    else:
        print(f"\n✗ 有 {failed} 个测试失败，请检查错误信息。")
        print("\n可能的原因:")
        print("1. 后端服务未启动")
        print("2. 端口配置不正确")
        print("3. 服务初始化失败")
        print("4. 路由注册问题")

if __name__ == "__main__":
    main()