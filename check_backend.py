"""
检查后端服务状态并测试 top_k 参数
"""

import requests
import time
from PIL import Image

# 创建测试图片
img = Image.new('RGB', (256, 256), color='red')
img.save('/tmp/test_image.png', 'PNG')

# 检查服务状态
print("检查后端服务状态...")
try:
    response = requests.get("http://localhost:8000/health", timeout=2)
    print(f"健康检查: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"后端服务未运行: {e}")
    print("请先启动后端服务：python -m app.main")
    exit(1)

# 测试 top_k 参数
base_url = "http://localhost:8000/api/v1"

print("\n" + "=" * 60)
print("测试 top_k 参数传递")
print("=" * 60)

test_cases = [
    (5, "top_k=5"),
    (10, "top_k=10 (默认)"),
    (20, "top_k=20"),
]

for top_k, description in test_cases:
    print(f"\n{description}")
    print("-" * 60)

    with open('/tmp/test_image.png', 'rb') as f:
        files = {'file': ('test.png', f, 'image/png')}
        data = {'top_k': str(top_k)}

        try:
            response = requests.post(
                f"{base_url}/search/image",
                files=files,
                data=data,
                timeout=30
            )

            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                total = result.get('total', 0)
                print(f"返回结果数量: {total}")
                print(f"期望结果数量: {top_k}")

                if total == top_k:
                    print("✓ 测试通过")
                else:
                    print("✗ 测试失败")
            else:
                print(f"错误: {response.text}")
        except Exception as e:
            print(f"请求异常: {e}")

print("\n" + "=" * 60)
