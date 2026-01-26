"""
Agent 语义搜索工具调用问题诊断脚本
"""

import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_search_text_direct():
    """直接测试语义搜索接口"""
    print("=" * 60)
    print("测试 1: 直接调用语义搜索接口")
    print("=" * 60)
    
    try:
        # 使用正确的 GET 请求
        response = httpx.get(
            f"{BASE_URL}/api/v1/search/text",
            params={
                "query": "柴犬",
                "top_k": 5
            },
            timeout=10.0
        )
        
        print(f"HTTP 状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 语义搜索成功")
            print(f"  状态: {data.get('status')}")
            print(f"  消息: {data.get('message')}")
            print(f"  总数: {data.get('total', 0)}")
            
            results = data.get('data', [])
            if results:
                print(f"  找到 {len(results)} 张图片")
                for i, result in enumerate(results[:3]):
                    print(f"    {i+1}. ID: {result.get('id')}, 分数: {result.get('score'):.3f}")
            
            return True
        else:
            print(f"✗ 失败: HTTP {response.status_code}")
            print(f"  响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_text_with_encoding():
    """测试带编码的语义搜索"""
    print("\n" + "=" * 60)
    print("测试 2: 带URL编码的语义搜索")
    print("=" * 60)
    
    try:
        # 使用 URL 编码
        from urllib.parse import quote
        encoded_query = quote("柴犬")
        
        response = httpx.get(
            f"{BASE_URL}/api/v1/search/text",
            params={
                "query": encoded_query,
                "top_k": 5
            },
            timeout=10.0
        )
        
        print(f"HTTP 状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 带编码的语义搜索成功")
            print(f"  状态: {data.get('status')}")
            print(f"  总数: {data.get('total', 0)}")
            return True
        else:
            print(f"✗ 失败: HTTP {response.status_code}")
            print(f"  响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False

def test_search_text_post():
    """测试 POST 方式的语义搜索"""
    print("\n" + "=" * 60)
    print("测试 3: POST 方式的语义搜索")
    print("=" * 60)
    
    try:
        response = httpx.post(
            f"{BASE_URL}/api/v1/search/",
            json={
                "query_text": "柴犬",
                "top_k": 5
            },
            timeout=10.0
        )
        
        print(f"HTTP 状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ POST 方式语义搜索成功")
            print(f"  状态: {data.get('status')}")
            print(f"  总数: {data.get('total', 0)}")
            return True
        else:
            print(f"✗ 失败: HTTP {response.status_code}")
            print(f"  响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False

def test_agent_chat():
    """测试 Agent 聊天接口"""
    print("\n" + "=" * 60)
    print("测试 4: Agent 聊天接口")
    print("=" * 60)
    
    try:
        response = httpx.post(
            f"{BASE_URL}/api/v1/agent/chat",
            json={
                "query": "帮我找几张柴犬图片",
                "top_k": 5
            },
            timeout=30.0
        )
        
        print(f"HTTP 状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Agent 聊天成功")
            print(f"  意图: {data.get('intent')}")
            print(f"  回复: {data.get('answer', '')[:200]}...")
            
            results = data.get('results')
            if results:
                print(f"  结果总数: {results.get('total', 0)}")
                images = results.get('images', [])
                if images:
                    print(f"  找到 {len(images)} 张图片")
            
            return True
        else:
            print(f"✗ 失败: HTTP {response.status_code}")
            print(f"  响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_openjiuwen_tool_direct():
    """直接测试 OpenJiuwen 工具调用"""
    print("\n" + "=" * 60)
    print("测试 5: 直接测试 OpenJiuwen 工具调用")
    print("=" * 60)
    
    try:
        from openjiuwen.core.utils.tool.service_api.restful_api import RestfulApi
        from openjiuwen.core.utils.tool.param import Param
        
        tool = RestfulApi(
            name="semantic_search_images",
            description="测试工具",
            params=[
                Param(name="query", description="搜索查询", param_type="string", required=True),
                Param(name="top_k", description="返回数量", param_type="integer", default_value=5, required=False, method="Query")
            ],
            path=f"{BASE_URL}/api/v1/search/text",
            headers={"Content-Type": "application/json"},
            method="GET"
        )
        
        print(f"工具名称: {tool.name}")
        print(f"工具路径: {tool.path}")
        print(f"工具方法: {tool.method}")
        
        # 尝试调用工具
        result = tool.invoke({"query": "柴犬", "top_k": 5})
        
        print(f"✓ OpenJiuwen 工具调用成功")
        print(f"  结果类型: {type(result)}")
        print(f"  结果: {result}")
        
        return True
        
    except Exception as e:
        print(f"✗ OpenJiuwen 工具调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("Agent 语义搜索工具调用问题诊断")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 基础 URL: {BASE_URL}")
    print()
    
    # 运行所有测试
    tests = [
        ("直接调用语义搜索接口", test_search_text_direct),
        ("带URL编码的语义搜索", test_search_text_with_encoding),
        ("POST 方式的语义搜索", test_search_text_post),
        ("Agent 聊天接口", test_agent_chat),
        ("OpenJiuwen 工具调用", test_openjiuwen_tool_direct),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print()
    print(f"总计: {len(results)} 个测试")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    
    if failed == 0:
        print("\n✓ 所有测试通过！")
    else:
        print(f"\n✗ 有 {failed} 个测试失败")
        print("\n根据日志分析，问题可能是：")
        print("1. OpenJiuwen 的 RestfulApi 工具实现问题")
        print("2. URL 编码问题")
        print("3. 网络连接问题")
        print("4. 工具参数配置问题")

if __name__ == "__main__":
    main()