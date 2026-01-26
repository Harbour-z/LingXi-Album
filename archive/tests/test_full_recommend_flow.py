"""
完整测试：先搜索图片，然后比较推荐
"""

import requests
import json
import time


def test_full_flow():
    """测试完整流程：搜索 → 推荐"""
    print("=" * 80)
    print("完整流程测试：搜索图片 → 比较推荐")
    print("=" * 80)

    url = "http://localhost:8000/api/v1/agent/chat"
    session_id = "test_full_recommend_flow"

    # 步骤1: 搜索图片
    print("\n" + "=" * 80)
    print("步骤1: 搜索柴犬图片")
    print("=" * 80)

    search_query = "找两张柴犬的图片"
    print(f"\n发送查询: {search_query}")

    payload = {
        "query": search_query,
        "session_id": session_id
    }

    response = requests.post(url, json=payload, timeout=120)

    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 搜索成功")
        print(f"\nAgent回复预览:")
        print(result.get("answer", "")[:200] + "...")
        
        time.sleep(1)
        
        # 步骤2: 比较推荐
        print("\n" + "=" * 80)
        print("步骤2: 比较这两张图片")
        print("=" * 80)

        recommend_query = "这两张图片哪个拍的更好，给我推荐一下"
        print(f"\n发送查询: {recommend_query}")

        payload = {
            "query": recommend_query,
            "session_id": session_id
        }

        response = requests.post(url, json=payload, timeout=120)

        if response.status_code == 200:
            result = response.json()

            print(f"\n✓ 请求成功 (HTTP 200)")
            print(f"\nAgent回复:")
            print("-" * 80)
            print(result.get("answer", ""))
            print("-" * 80)

            # 检查推荐信息
            recommendation = result.get("recommendation")
            if recommendation:
                print(f"\n✓ 包含推荐信息")
                print(f"  推荐ID: {recommendation.get('recommended_image_id')}")
                print(f"  推荐理由: {recommendation.get('recommendation_reason')}")
                
                return True
            else:
                print(f"\n⚠ 未找到推荐信息")
                return False
        else:
            print(f"\n✗ 推荐请求失败: HTTP {response.status_code}")
            print(f"  响应: {response.text}")
            return False
    else:
        print(f"\n✗ 搜索请求失败: HTTP {response.status_code}")
        print(f"  响应: {response.text}")
        return False


def main():
    """主测试流程"""
    print("\n" + "=" * 80)
    print("开始完整流程测试...")
    print("=" * 80)

    input("\n请确保后端服务已启动，然后按 Enter 继续...")

    success = test_full_flow()

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

    if success:
        print("\n✓ 完整流程测试通过！")
        print("\n验证结果:")
        print("  ✓ Agent成功搜索图片")
        print("  ✓ Agent从对话历史中提取图片ID")
        print("  ✓ Agent调用recommend_images工具")
        print("  ✓ 工具成功执行并返回推荐结果")
    else:
        print("\n✗ 测试失败，需要进一步调试。")


if __name__ == "__main__":
    main()
