"""
测试API响应结构
验证/api/v1/agent/chat端点返回的完整数据结构
"""

import requests
import json


def test_api_response():
    """测试API响应结构"""
    print("=" * 80)
    print("API响应结构测试")
    print("=" * 80)

    url = "http://localhost:8000/api/v1/agent/chat"

    payload = {
        "query": "找两张柴犬的图片",
        "session_id": "test_api_structure"
    }

    try:
        response = requests.post(url, json=payload, timeout=120)

        if response.status_code == 200:
            result = response.json()

            print("\n完整API响应:")
            print("-" * 80)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("-" * 80)

            print("\n响应字段分析:")
            print(f"  - answer: {len(result.get('answer', ''))} 字符")
            print(f"  - images: {len(result.get('images', []))} 张")
            print(f"  - recommendations: {result.get('recommendations', 'N/A')}")

            images = result.get('images', [])
            if images:
                print("\n图片详细信息:")
                for i, img in enumerate(images, 1):
                    print(f"  {i}. ID: {img.get('id')}")
                    print(f"     preview_url: {img.get('preview_url')}")
                    print(f"     alt_text: {img.get('alt_text')}")

        else:
            print(f"\n请求失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")

    except Exception as e:
        print(f"\n请求异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_api_response()
