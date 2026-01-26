"""
测试Agent调用recommend_images工具
"""

import requests
import json


def test_agent_recommend_images():
    """测试Agent通过聊天接口调用recommend_images工具"""
    print("=" * 80)
    print("Agent调用Recommend Images工具测试")
    print("=" * 80)

    url = "http://localhost:8000/api/v1/agent/chat"

    # 测试查询
    test_query = "这两张图片哪个拍的更好，给我推荐一下"

    print(f"\n发送查询: {test_query}")
    print("\n预期行为:")
    print("  1. Agent应该识别这是一个图片比较/推荐的请求")
    print("  2. Agent应该调用recommend_images工具")
    print("  3. 工具应该成功执行并返回推荐结果")

    payload = {
        "query": test_query,
        "session_id": "test_agent_recommend_session"
    }

    try:
        response = requests.post(url, json=payload, timeout=120)

        print(f"\n响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            print(f"\n✓ 请求成功 (HTTP 200)")
            print(f"\nAgent回复:")
            print("-" * 80)
            print(result.get("answer", ""))
            print("-" * 80)

            # 检查是否有推荐信息
            recommendation = result.get("recommendation")
            if recommendation:
                print(f"\n✓ 包含推荐信息")
                print(f"  推荐ID: {recommendation.get('recommended_image_id')}")
                print(f"  推荐理由: {recommendation.get('recommendation_reason')}")
                print(f"  备选数量: {recommendation.get('alternative_count', 0)}")
            else:
                print(f"\n⚠ 未找到推荐信息")

            return True

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

    success = test_agent_recommend_images()

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

    if success:
        print("\n✓ 测试通过！")
    else:
        print("\n✗ 测试失败，需要进一步调试。")
        print("\n可能的问题:")
        print("  - Agent没有正确调用recommend_images工具")
        print("  - 工具调用时参数格式错误")
        print("  - OpenJiuwen工具框架的参数传递问题")


if __name__ == "__main__":
    main()
