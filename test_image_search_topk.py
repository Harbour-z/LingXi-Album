"""
测试以图搜图功能中 top_k 参数传递问题
验证修复后，前端传递的 top_k 参数能够正确影响搜索结果数量
"""

import requests
import io
from PIL import Image
import numpy as np


def create_test_image(size=(256, 256), color=(255, 0, 0)):
    """创建测试用的红色图片"""
    img_array = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    img_array[:, :] = color
    img = Image.fromarray(img_array, mode='RGB')
    return img


def test_image_search_with_different_topk():
    """测试不同 top_k 值的图片搜索"""
    base_url = "http://localhost:8000/api/v1"
    
    print("=" * 80)
    print("测试以图搜图 - top_k 参数传递")
    print("=" * 80)
    
    # 创建测试图片
    test_image = create_test_image()
    
    # 测试不同的 top_k 值
    test_cases = [
        {"top_k": 5, "expected": 5, "description": "top_k=5"},
        {"top_k": 10, "expected": 10, "description": "top_k=10 (默认值)"},
        {"top_k": 20, "expected": 20, "description": "top_k=20"},
        {"top_k": 50, "expected": 50, "description": "top_k=50"},
    ]
    
    for test_case in test_cases:
        top_k = test_case["top_k"]
        expected = test_case["expected"]
        description = test_case["description"]
        
        print(f"\n测试用例: {description}")
        print("-" * 80)
        
        # 准备 FormData
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        files = {
            'file': ('test_image.png', img_bytes, 'image/png')
        }
        data = {
            'top_k': str(top_k)
        }
        
        try:
            response = requests.post(
                f"{base_url}/search/image",
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"请求状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('status')
                message = result.get('message')
                data = result.get('data', [])
                total = result.get('total', 0)
                
                print(f"响应状态: {status}")
                print(f"响应消息: {message}")
                print(f"返回结果数量: {total}")
                print(f"期望结果数量: {expected}")
                
                # 验证结果数量
                if total == expected:
                    print(f"✓ 测试通过：结果数量正确 ({total})")
                else:
                    print(f"✗ 测试失败：期望 {expected} 个结果，实际返回 {total} 个")
                
                # 显示前3个结果
                if len(data) > 0:
                    print(f"\n前3个结果:")
                    for i, item in enumerate(data[:3], 1):
                        score = item.get('score', 0)
                        image_id = item.get('id', 'N/A')
                        print(f"  {i}. ID: {image_id}, 相似度: {score:.4f}")
            else:
                print(f"✗ 请求失败: {response.text}")
                
        except Exception as e:
            print(f"✗ 请求异常: {e}")
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


def test_search_without_topk():
    """测试不传递 top_k 参数时，使用默认值 10"""
    base_url = "http://localhost:8000/api/v1"
    
    print("\n" + "=" * 80)
    print("测试不传递 top_k 参数时的默认行为")
    print("=" * 80)
    
    # 创建测试图片
    test_image = create_test_image()
    
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    files = {
        'file': ('test_image.png', img_bytes, 'image/png')
    }
    
    try:
        response = requests.post(
            f"{base_url}/search/image",
            files=files,
            timeout=30
        )
        
        print(f"请求状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            total = result.get('total', 0)
            
            print(f"返回结果数量: {total}")
            print(f"期望默认值: 10")
            
            if total == 10:
                print(f"✓ 测试通过：使用默认值 10")
            else:
                print(f"✗ 测试失败：期望 10 个结果，实际返回 {total} 个")
        else:
            print(f"✗ 请求失败: {response.text}")
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")


if __name__ == "__main__":
    print("\n开始测试以图搜图 top_k 参数传递...\n")
    
    # 等待用户确认服务已启动
    input("请确保后端服务已启动 (http://localhost:8000)，然后按 Enter 继续...")
    
    # 测试不同 top_k 值
    test_image_search_with_different_topk()
    
    # 测试默认行为
    test_search_without_topk()
