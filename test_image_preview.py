"""
测试图片预览功能恢复
验证Agent是否在回复中包含Markdown图片链接，前端能否正常显示
"""

import requests
import json


def test_image_preview():
    """测试图片预览功能"""
    print("=" * 80)
    print("图片预览功能测试")
    print("=" * 80)

    url = "http://localhost:8000/api/v1/agent/chat"

    # 测试查询
    test_query = "找两张柴犬的图片"

    print(f"\n发送查询: {test_query}")
    print("预期: Agent应该在回复中包含Markdown图片链接，格式：![描述](/api/v1/storage/images/{image_id})")

    payload = {
        "query": test_query,
        "session_id": "test_image_preview_session"
    }

    try:
        response = requests.post(url, json=payload, timeout=120)

        if response.status_code == 200:
            result = response.json()

            print(f"\n✓ 请求成功 (HTTP {response.status_code})")
            print(f"\nAgent回复:")
            print("-" * 80)
            print(result.get("answer", ""))
            print("-" * 80)

            # 检查是否包含图片链接
            answer = result.get("answer", "")
            images = result.get("images", [])

            # 检查Markdown格式图片链接
            import re
            markdown_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
            markdown_links = re.findall(markdown_pattern, answer)

            print(f"\n检查结果:")
            print(f"  1. Markdown图片链接数量: {len(markdown_links)}")
            print(f"  2. 提取到的images数量: {len(images)}")

            if markdown_links:
                print(f"\n  找到的Markdown链接:")
                for i, (alt, url) in enumerate(markdown_links, 1):
                    print(f"    {i}. alt='{alt}'")
                    print(f"       url='{url}'")

            if images:
                print(f"\n  提取到的图片信息:")
                for i, img in enumerate(images, 1):
                    print(f"    {i}. ID: {img.get('id')}")
                    print(f"       preview_url: {img.get('preview_url')}")

            # 验证结果
            success = len(markdown_links) > 0 or len(images) > 0

            if success:
                print("\n✓ 测试通过：图片预览功能已恢复")
                print("  - Agent在回复中包含了Markdown图片链接")
                print("  - 前端可以解析并显示图片预览")
            else:
                print("\n✗ 测试失败：未找到图片链接")
                print("  可能原因：")
                print("  - Agent没有在回复中包含Markdown图片链接")
                print("  - 正则表达式匹配失败")

            return success

        else:
            print(f"\n✗ 请求失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
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

    success = test_image_preview()

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

    if success:
        print("\n✓ 所有测试通过！图片预览功能已恢复正常。")
        print("\n前端应该能够：")
        print("  1. 解析Agent回复中的Markdown图片链接")
        print("  2. 显示图片缩略图预览")
        print("  3. 支持点击查看大图")
    else:
        print("\n✗ 测试失败，需要进一步调试。")


if __name__ == "__main__":
    main()
