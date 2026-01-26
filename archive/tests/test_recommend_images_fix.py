"""
测试recommend_images工具修复
验证图片推荐功能是否恢复正常
"""

import requests
import json


def test_recommend_images_tool():
    """测试recommend_images工具"""
    print("=" * 80)
    print("Recommend Images工具测试")
    print("=" * 80)

    # 直接调用API端点
    url = "http://localhost:8000/api/v1/image-recommendation/analyze"

    # 测试数据：使用已知的两张图片ID
    payload = {
        "images": [
            "308385fb-1792-4e49-93c3-55c8d4ed5eae",
            "22a32394-d095-41ad-9991-731048d82695"
        ],
        "user_preference": "帮我选一张最好的"
    }

    print(f"\n发送请求到: {url}")
    print(f"请求数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=payload, timeout=120)

        print(f"\n响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            print(f"\n✓ 请求成功 (HTTP 200)")
            print(f"\n完整响应:")
            print("-" * 80)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("-" * 80)

            # 检查响应结构
            if result.get("status") == "success":
                data = result.get("data", {})
                
                if data.get("success"):
                    print(f"\n✓ 图片推荐成功")
                    
                    analysis = data.get("analysis", {})
                    recommend = data.get("recommendation", {})
                    
                    print(f"\n分析结果:")
                    for image_id, analysis_data in analysis.items():
                        print(f"\n  图片ID: {image_id}")
                        if analysis_data:
                            print(f"    构图美学: {analysis_data.get('composition_score')}")
                            print(f"    色彩搭配: {analysis_data.get('color_score')}")
                            print(f"    光影运用: {analysis_data.get('lighting_score')}")
                            print(f"    综合评分: {analysis_data.get('overall_score')}")
                    
                    print(f"\n推荐结果:")
                    print(f"  推荐图片ID: {recommend.get('recommended_image_id')}")
                    print(f"  推荐理由: {recommend.get('recommendation_reason')}")
                    
                    return True
                else:
                    print(f"\n✗ 图片推荐失败")
                    print(f"  错误: {data.get('error')}")
                    return False
            else:
                print(f"\n✗ 响应状态错误: {result.get('status')}")
                print(f"  消息: {result.get('message')}")
                return False

        elif response.status_code == 422:
            print(f"\n✗ 请求参数错误 (HTTP 422)")
            print(f"  响应内容: {response.text}")
            print("\n  可能原因:")
            print("  - 参数格式不正确")
            print("  - images数组格式错误")
            print("  - 缺少必需参数")
            return False

        else:
            print(f"\n✗ 请求失败: HTTP {response.status_code}")
            print(f"  响应内容: {response.text}")
            return False

    except Exception as e:
        print(f"\n✗ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试流程"""
    print("\n" + "=" * 80)
    print("开始测试...")
    print("=" * 80)

    input("\n请确保后端服务已启动，然后按 Enter 继续...")

    success = test_recommend_images_tool()

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

    if success:
        print("\n✓ 所有测试通过！图片推荐功能已恢复正常。")
        print("\n功能验证:")
        print("  ✓ API端点可以接收图片ID列表")
        print("  ✓ 参数格式正确")
        print("  ✓ 可以调用qwen3-vl-plus进行分析")
        print("  ✓ 返回推荐结果")
    else:
        print("\n✗ 测试失败，需要进一步调试。")


if __name__ == "__main__":
    main()
