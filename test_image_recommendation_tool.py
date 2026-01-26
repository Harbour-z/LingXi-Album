"""
测试智能图片推荐工具功能

验证流程：
1. 测试健康检查端点
2. 测试上传图片并推荐
3. 验证Agent工具是否正确注册
4. 检查API文档中是否包含新工具
"""

import requests
import json
from typing import Dict, List, Any


def test_health_check():
    """测试健康检查"""
    print("\n" + "=" * 80)
    print("测试1: 健康检查")
    print("=" * 80)
    
    url = "http://localhost:8000/api/v1/image-recommendation/health"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            status = result.get("status")
            service = result.get("service")
            
            print(f"✓ 健康检查成功")
            print(f"  状态: {status}")
            print(f"  服务: {service}")
            return True
        else:
            print(f"✗ 健康检查失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        return False


def test_upload_recommend():
    """测试上传图片推荐"""
    print("\n" + "=" * 80)
    print("测试2: 上传图片并推荐")
    print("=" * 80)
    
    url = "http://localhost:8000/api/v1/image-recommendation/upload-analyze"
    
    # 创建测试图片
    from PIL import Image
    import io
    import numpy as np
    
    # 创建3张测试图片（不同颜色）
    test_images = [
        ("red_test.jpg", create_test_image((256, 256), (255, 0, 0))),
        ("green_test.jpg", create_test_image((256, 256), (0, 255, 0))),
        ("blue_test.jpg", create_test_image((256, 256), (0, 0, 255)))
    ]
    
    print(f"\n准备上传 {len(test_images)} 张测试图片")
    
    try:
        files = []
        for filename, img_data in test_images:
            files.append(("files", (filename, img_data, "image/jpeg")))
        
        data = {
            "user_preference": "我更喜欢构图好的照片"
        }
        
        print(f"\n发送请求到: {url}")
        print(f"用户偏好: {data['user_preference']}")
        
        response = requests.post(url, files=files, data=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            status = result.get("status")
            message = result.get("message")
            data = result.get("data", {})
            
            print(f"\n响应状态: {status}")
            print(f"响应消息: {message}")
            
            if data.get("success"):
                print(f"\n✓ 图片推荐成功")
                
                # 显示推荐信息
                recommendation = data.get("recommendation", {})
                best_id = recommendation.get("best_image_id")
                reason = recommendation.get("recommendation_reason", "")
                
                print(f"\n推荐结果:")
                print(f"  最佳图片ID: {best_id}")
                print(f"  推荐理由: {reason[:100]}...")
                print(f"  其他图片ID: {recommendation.get(\"alternative_image_ids\", [])}")
                
                # 显示分析详情
                analysis = data.get("analysis", {})
                for img_key, img_data in analysis.items():
                    print(f"\n  {img_key}:")
                    print(f"    综合评分: {img_data.get('overall_score', 0):.2f}")
                    print(f"    构图: {img_data.get('composition_score', 0):.2f}")
                    print(f"    色彩: {img_data.get('color_score', 0):.2f}")
                    print(f"    光影: {img_data.get('lighting_score', 0):.2f}")
                    print(f"    主题: {img_data.get('theme_score', 0):.2f}")
                    print(f"    情感: {img_data.get('emotion_score', 0):.2f}")
                    print(f"    创意: {img_data.get('creativity_score', 0):.2f}")
                    print(f"    故事: {img_data.get('story_score', 0):.2f}")
                
                print(f"\n使用的模型: {data.get('model_used')}")
                print(f"分析图片总数: {data.get('total_images')}")
                
                return True
            else:
                print(f"\n✗ 图片推荐失败")
                print(f"错误: {data.get('error')}")
                print(f"详情: {data.get('details')}")
                return False
        else:
            print(f"\n✗ 请求失败: HTTP {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n✗ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_test_image(size=(256, 256), color=(255, 0, 0)):
    """创建测试图片"""
    import numpy as np
    from PIL import Image
    
    img_array = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    img_array[:, :] = color
    
    # 添加一些噪声使图片更真实
    noise = np.random.randint(-20, 20, size=img_array.shape, dtype=np.int16)
    img_array = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    img = Image.fromarray(img_array, mode='RGB')
    
    # 转换为字节
    import io
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=95)
    img_bytes.seek(0)
    
    return img_bytes.getvalue()


def test_agent_tools():
    """测试Agent工具是否正确注册"""
    print("\n" + "=" * 80)
    print("测试3: 验证Agent工具注册")
    print("=" * 80)
    
    # 获取Agent配置
    from app.services.agent_service import get_agent_service
    
    try:
        agent_svc = get_agent_service()
        tools = agent_svc.tools
        
        print(f"\n已注册的Agent工具数量: {len(tools)}")
        
        # 查找recommend_images工具
        found_tool = None
        for tool in tools:
            if hasattr(tool, 'name') and tool.name == 'recommend_images':
                found_tool = tool
                break
        
        if found_tool:
            print(f"✓ 找到recommend_images工具")
            print(f"  工具名称: {found_tool.name}")
            print(f"  工具描述: {found_tool.description[:100]}...")
            print(f"  工具方法: {found_tool.method}")
            print(f"  工具路径: {found_tool.path}")
            print(f"  参数数量: {len(found_tool.params) if hasattr(found_tool, 'params') else 'N/A'}")
            return True
        else:
            print(f"✗ 未找到recommend_images工具")
            print(f"\n已注册的工具列表:")
            for i, tool in enumerate(tools, 1):
                tool_name = getattr(tool, 'name', 'unknown')
                print(f"  {i}. {tool_name}")
            return False
            
    except Exception as e:
        print(f"✗ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_docs():
    """测试API文档是否包含新端点"""
    print("\n" + "=" * 80)
    print("测试4: 验证API文档")
    print("=" * 80)
    
    url = "http://localhost:8000/openapi.json"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            print(f"\nAPI路径数量: {len(paths)}")
            
            # 检查图片推荐相关端点
            recommendation_paths = [
                "/api/v1/image-recommendation/analyze",
                "/api/v1/image-recommendation/upload-analyze",
                "/api/v1/image-recommendation/health"
            ]
            
            found_count = 0
            for path in recommendation_paths:
                if path in paths:
                    print(f"✓ 找到端点: {path}")
                    found_count += 1
                else:
                    print(f"✗ 未找到端点: {path}")
            
            if found_count == len(recommendation_paths):
                print(f"\n✓ 所有图片推荐端点都已注册")
                return True
            else:
                print(f"\n⚠ 只找到 {found_count}/{len(recommendation_paths)} 个端点")
                return False
        else:
            print(f"✗ 获取OpenAPI规范失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        return False


def main():
    """主测试流程"""
    print("\n" + "=" * 80)
    print("智能图片推荐工具功能测试")
    print("=" * 80)
    
    input("\n请确保后端服务已启动 (http://localhost:8000)，然后按 Enter 继续...")
    
    results = []
    
    # 测试1: 健康检查
    results.append(("健康检查", test_health_check()))
    
    # 测试2: API文档验证
    results.append(("API文档", test_api_docs()))
    
    # 测试3: Agent工具注册
    results.append(("Agent工具", test_agent_tools()))
    
    # 测试4: 上传图片推荐（需要真实的API调用，可能超时）
    print("\n" + "=" * 80)
    print("测试4: 上传图片并推荐（需要AI模型调用，可能较慢）")
    print("=" * 80)
    print("注意：此测试需要调用qwen3-max和qwen3-vl-plus模型")
    print("预计耗时：1-2分钟")
    choice = input("\n是否继续此测试？(yes/no): ").strip().lower()
    
    if choice == 'yes':
        results.append(("图片推荐", test_upload_recommend()))
    else:
        print("跳过图片推荐测试")
    
    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("\n✓ 所有测试通过！")
    else:
        print(f"\n⚠ 有 {failed} 个测试失败，请检查日志")


if __name__ == "__main__":
    main()
