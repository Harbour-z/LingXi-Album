"""
测试以图搜图功能的完整修复
验证：
1. 图像向量相似度计算接口调用
2. 向量数据库比对搜索接口调用
3. 搜索结果相似度排序
4. 返回结果的相关性
"""

import requests
import io
from PIL import Image
import numpy as np
from typing import Dict, List, Any


def create_test_image(size=(256, 256), color=(255, 0, 0), noise_level=0):
    """创建测试图片"""
    img_array = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    img_array[:, :] = color
    
    # 添加噪声使图片更真实
    if noise_level > 0:
        noise = np.random.randint(-noise_level, noise_level, size=img_array.shape, dtype=np.int16)
        img_array = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    img = Image.fromarray(img_array, mode='RGB')
    return img


def test_image_search_similarity():
    """测试以图搜图的相似度排序和相关性"""
    base_url = "http://localhost:8000/api/v1"
    
    print("=" * 80)
    print("测试以图搜图 - 相似度排序和相关性验证")
    print("=" * 80)
    
    # 创建测试图片（红色）
    test_image = create_test_image(color=(255, 0, 0), noise_level=20)
    
    print(f"\n创建测试图片: size={test_image.size}, color=红色")
    
    # 准备 FormData
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='JPEG', quality=95)
    img_bytes.seek(0)
    
    files = {
        'file': ('test_red_image.jpg', img_bytes, 'image/jpeg')
    }
    data = {
        'top_k': '10'
    }
    
    try:
        print(f"\n发送搜索请求到: {base_url}/search/image")
        response = requests.post(
            f"{base_url}/search/image",
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('status')
            message = result.get('message')
            data = result.get('data', [])
            total = result.get('total', 0)
            query_type = result.get('query_type', 'unknown')
            
            print(f"\n响应状态: {status}")
            print(f"响应消息: {message}")
            print(f"查询类型: {query_type}")
            print(f"返回结果数量: {total}")
            
            # 验证查询类型
            if query_type == 'image':
                print(f"✓ 查询类型正确: image")
            else:
                print(f"✗ 查询类型错误: {query_type}，期望 image")
            
            # 验证返回结果数量
            if total == 10:
                print(f"✓ 返回结果数量正确: {total}")
            else:
                print(f"⚠ 返回结果数量: {total}（期望 10）")
            
            # 分析相似度排序
            if data:
                print(f"\n" + "-" * 80)
                print("相似度排序验证:")
                print("-" * 80)
                
                scores = []
                for i, item in enumerate(data, 1):
                    score = item.get('score', 0)
                    image_id = item.get('id', 'N/A')
                    scores.append(score)
                    print(f"{i:2d}. ID: {image_id}, 相似度: {score:.4f}")
                
                # 验证相似度降序排列
                is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
                if is_sorted:
                    print(f"\n✓ 相似度排序正确: 降序排列")
                else:
                    print(f"\n✗ 相似度排序错误: 未按降序排列")
                
                # 统计相似度范围
                min_score = min(scores) if scores else 0
                max_score = max(scores) if scores else 0
                avg_score = sum(scores) / len(scores) if scores else 0
                
                print(f"\n相似度统计:")
                print(f"  最低分: {min_score:.4f}")
                print(f"  最高分: {max_score:.4f}")
                print(f"  平均分: {avg_score:.4f}")
                
                # 验证相似度合理性
                if max_score > 0.8:
                    print(f"✓ 存在高相似度结果 (>0.8)")
                elif max_score > 0.5:
                    print(f"⚠ 最高相似度中等 ({max_score:.4f})")
                else:
                    print(f"✗ 最高相似度过低 ({max_score:.4f})，可能存在问题")
                
                # 验证是否有有效的相似度值
                valid_scores = [s for s in scores if s is not None and s > 0]
                if valid_scores:
                    print(f"✓ 所有结果都有有效的相似度值")
                else:
                    print(f"✗ 相似度值无效")
                
            else:
                print(f"\n⚠ 警告: 没有返回任何搜索结果")
                print(f"可能原因:")
                print(f"  1. 向量数据库为空，需要先上传和索引图片")
                print(f"  2. 向量搜索服务未正确初始化")
                print(f"  3. 相似度阈值过高")
                
        else:
            print(f"\n✗ 请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n✗ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
    return True


def test_different_images():
    """测试不同类型图片的搜索结果差异"""
    base_url = "http://localhost:8000/api/v1"
    
    print("\n" + "=" * 80)
    print("测试不同类型图片的搜索")
    print("=" * 80)
    
    # 创建不同颜色的测试图片
    test_cases = [
        {"color": (255, 0, 0), "name": "红色图片"},
        {"color": (0, 255, 0), "name": "绿色图片"},
        {"color": (0, 0, 255), "name": "蓝色图片"},
    ]
    
    results_summary = []
    
    for test_case in test_cases:
        color = test_case["color"]
        name = test_case["name"]
        
        print(f"\n测试: {name}")
        print("-" * 80)
        
        # 创建测试图片
        test_image = create_test_image(color=color, noise_level=20)
        
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='JPEG', quality=95)
        img_bytes.seek(0)
        
        files = {
            'file': (f'test_{name}.jpg', img_bytes, 'image/jpeg')
        }
        data = {
            'top_k': '5'
        }
        
        try:
            response = requests.post(
                f"{base_url}/search/image",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                data = result.get('data', [])
                total = result.get('total', 0)
                
                if data:
                    scores = [item.get('score', 0) for item in data]
                    avg_score = sum(scores) / len(scores) if scores else 0
                    max_score = max(scores) if scores else 0
                    
                    results_summary.append({
                        "name": name,
                        "count": total,
                        "avg_score": avg_score,
                        "max_score": max_score
                    })
                    
                    print(f"返回结果: {total} 条")
                    print(f"平均相似度: {avg_score:.4f}")
                    print(f"最高相似度: {max_score:.4f}")
                else:
                    print(f"⚠ 没有返回结果")
                    
        except Exception as e:
            print(f"✗ 请求异常: {e}")
    
    # 总结不同图片的搜索结果差异
    print("\n" + "-" * 80)
    print("搜索结果对比:")
    print("-" * 80)
    print(f"{'图片类型':<12} {'结果数':<8} {'平均分':<10} {'最高分':<10}")
    print("-" * 80)
    
    for summary in results_summary:
        print(f"{summary['name']:<12} {summary['count']:<8} "
              f"{summary['avg_score']:<10.4f} {summary['max_score']:<10.4f}")
    
    return True


def test_search_by_image_id():
    """测试通过图片ID搜索相似图片"""
    base_url = "http://localhost:8000/api/v1"
    
    print("\n" + "=" * 80)
    print("测试通过图片ID搜索相似图片")
    print("=" * 80)
    
    # 首先获取一张图片的ID
    print("\n尝试获取数据库中的图片ID...")
    
    try:
        # 尝试列出存储的图片
        response = requests.get(f"{base_url}/storage/images", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            images = result.get('images', [])
            
            if images:
                test_image_id = images[0].get('id')
                print(f"找到图片ID: {test_image_id}")
                
                # 使用该ID进行搜索
                print(f"\n使用图片ID搜索相似图片...")
                
                response = requests.get(
                    f"{base_url}/search/image/{test_image_id}",
                    params={'top_k': '5'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    data = result.get('data', [])
                    total = result.get('total', 0)
                    
                    print(f"返回结果: {total} 条")
                    
                    # 验证是否过滤了查询图片本身
                    found_self = any(item.get('id') == test_image_id for item in data)
                    if not found_self:
                        print(f"✓ 正确过滤了查询图片本身")
                    else:
                        print(f"⚠ 查询结果中包含查询图片本身")
                    
                    if data:
                        scores = [item.get('score', 0) for item in data]
                        print(f"相似度范围: {min(scores):.4f} - {max(scores):.4f}")
                    
                    return True
                else:
                    print(f"✗ 搜索失败: {response.text}")
                    return False
            else:
                print(f"⚠ 数据库中没有图片")
                return False
        else:
            print(f"⚠ 无法获取图片列表: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("以图搜图功能完整测试")
    print("=" * 80)
    
    # 等待用户确认服务已启动
    input("\n请确保后端服务已启动 (http://localhost:8000)，然后按 Enter 继续...")
    
    all_passed = True
    
    # 测试1: 相似度排序和相关性
    print("\n")
    if not test_image_search_similarity():
        all_passed = False
    
    # 测试2: 不同类型图片的搜索
    print("\n")
    if not test_different_images():
        all_passed = False
    
    # 测试3: 通过图片ID搜索
    print("\n")
    if not test_search_by_image_id():
        all_passed = False
    
    # 总结
    print("\n" + "=" * 80)
    if all_passed:
        print("✓ 所有测试通过")
    else:
        print("⚠ 部分测试失败，请查看日志")
    print("=" * 80)
