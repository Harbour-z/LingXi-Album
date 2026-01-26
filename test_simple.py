"""
简单测试：测试 Agent 图片提取
"""

import requests
import re

def test_image_extraction():
    """测试图片提取逻辑"""
    
    # Agent 返回的回复
    response_text = """我找到了一张柴犬的照片！这张照片是在2026年1月20日拍摄的，是一张500x589像素的JPEG格式图片。

这是柴犬的照片：
![柴犬](/api/v1/storage/images/308385fb-1792-4e49-93c3-55c8d4ed5eae)

需要查看更多柴犬的照片或者其他类型的图片吗？"""
    
    # 测试正则表达式
    markdown_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    matches = re.findall(markdown_pattern, response_text, re.DOTALL)
    
    print("=" * 80)
    print("测试图片提取正则表达式")
    print("=" * 80)
    print(f"\n回复内容:")
    print(response_text)
    print(f"\n匹配到 {len(matches)} 个 Markdown 图片")
    
    for i, (alt_text, url) in enumerate(matches, 1):
        print(f"\n图片 {i}:")
        print(f"  Alt text: '{alt_text}'")
        print(f"  URL: '{url}'")
        
        if "/api/v1/storage/images/" in url:
            image_id = url.split("/")[-1]
            print(f"  Image ID: {image_id}")

if __name__ == "__main__":
    test_image_extraction()
