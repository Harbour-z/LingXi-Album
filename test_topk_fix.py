"""
快速测试 top_k 参数修复
"""

import requests
from PIL import Image

# 创建测试图片
img = Image.new('RGB', (256, 256), color='red')
img.save('/tmp/test_image.png', 'PNG')

# 测试不同的 top_k 值
base_url = "http://localhost:8000/api/v1"

print("测试 top_k=5...")
with open('/tmp/test_image.png', 'rb') as f:
    files = {'file': ('test.png', f, 'image/png')}
    data = {'top_k': '5'}
    response = requests.post(f"{base_url}/search/image", files=files, data=data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"返回结果数量: {result.get('total')}")
        print(f"期望: 5")
    else:
        print(f"错误: {response.text}")

print("\n测试 top_k=20...")
with open('/tmp/test_image.png', 'rb') as f:
    files = {'file': ('test.png', f, 'image/png')}
    data = {'top_k': '20'}
    response = requests.post(f"{base_url}/search/image", files=files, data=data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"返回结果数量: {result.get('total')}")
        print(f"期望: 20")
    else:
        print(f"错误: {response.text}")
