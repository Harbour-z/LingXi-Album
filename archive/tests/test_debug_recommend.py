"""
测试并查看OpenJiuwen传递的参数格式
"""

import requests
import json


def test_with_debug():
    """测试推荐功能并查看调试日志"""
    print("=" * 80)
    print("推荐功能调试测试")
    print("=" * 80)

    url = "http://localhost:8000/api/v1/agent/chat"
    session_id = "test_debug_recommend"

    # 步骤1: 搜索图片
    print("\n步骤1: 搜索图片")
    print("-" * 80)

    search_query = "找三张柴犬的图片"
    print(f"发送查询: {search_query}")

    payload = {
        "query": search_query,
        "session_id": session_id
    }

    response = requests.post(url, json=payload, timeout=120)

    if response.status_code == 200:
        result = response.json()
        print("✓ 搜索成功")
        
        import time
        time.sleep(1)
        
        # 步骤2: 推荐图片
        print("\n步骤2: 推荐图片（查看调试日志）")
        print("-" * 80)

        recommend_query = "前三张哪张拍的比较好，为什么"
        print(f"发送查询: {recommend_query}")
        print("\n请查看Terminal#17的日志，查找:")
        print("  - [Middleware] 捕获到图片推荐请求")
        print("  - [Middleware] Body: {...}")
        print("\n这将显示OpenJiuwen实际发送的参数格式")

        payload = {
            "query": recommend_query,
            "session_id": session_id
        }

        response = requests.post(url, json=payload, timeout=120)

        if response.status_code == 200:
            result = response.json()
            print("\n✓ 请求完成")
            print(f"\nAgent回复:")
            print("-" * 80)
            print(result.get("answer", "")[:500] + "...")
            print("-" * 80)
        else:
            print(f"\n✗ 请求失败: HTTP {response.status_code}")
    else:
        print(f"\n✗ 搜索失败: HTTP {response.status_code}")


if __name__ == "__main__":
    input("\n请确保后端服务已启动，然后按 Enter 继续...")
    test_with_debug()
