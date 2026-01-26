"""
Agent 工具调用修复验证脚本
测试 Agent 是否能正确处理时间相关的照片搜索请求
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_get_current_time():
    """测试获取当前时间工具"""
    print("=" * 60)
    print("测试 1: 获取当前时间工具")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/api/v1/agent/time")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ 成功获取当前时间")
                print(f"  状态: {data.get('status')}")
                print(f"  时间: {data.get('time')}")
                return True
            else:
                print(f"✗ 失败: HTTP {response.status_code}")
                print(f"  响应: {response.text}")
                return False
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False

async def test_meta_search():
    """测试元数据搜索工具"""
    print("\n" + "=" * 60)
    print("测试 2: 元数据搜索工具")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 测试日期搜索
            response = await client.get(
                f"{BASE_URL}/api/v1/search/meta",
                params={"date_text": "1.18", "top_k": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ 元数据搜索成功")
                print(f"  状态: {data.get('status')}")
                print(f"  消息: {data.get('message')}")
                print(f"  总数: {data.get('total', 0)}")
                return True
            else:
                print(f"✗ 失败: HTTP {response.status_code}")
                print(f"  响应: {response.text}")
                return False
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False

async def test_hybrid_search():
    """测试混合搜索工具"""
    print("\n" + "=" * 60)
    print("测试 3: 混合搜索工具")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 测试日期+语义搜索
            response = await client.get(
                f"{BASE_URL}/api/v1/search/meta/hybrid",
                params={"date_text": "1.18", "query": "海边", "top_k": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ 混合搜索成功")
                print(f"  状态: {data.get('status')}")
                print(f"  消息: {data.get('message')}")
                print(f"  总数: {data.get('total', 0)}")
                return True
            else:
                print(f"✗ 失败: HTTP {response.status_code}")
                print(f"  响应: {response.text}")
                return False
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False

async def test_agent_chat_time_query():
    """测试 Agent 聊天 - 时间查询"""
    print("\n" + "=" * 60)
    print("测试 4: Agent 聊天 - 时间查询")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 测试时间查询
            response = await client.post(
                f"{BASE_URL}/api/v1/agent/chat",
                json={"query": "现在是什么时间？", "top_k": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Agent 时间查询成功")
                print(f"  意图: {data.get('intent')}")
                print(f"  回复: {data.get('answer', '')[:200]}...")
                return True
            else:
                print(f"✗ 失败: HTTP {response.status_code}")
                print(f"  响应: {response.text}")
                return False
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False

async def test_agent_chat_date_search():
    """测试 Agent 聊天 - 日期搜索"""
    print("\n" + "=" * 60)
    print("测试 5: Agent 聊天 - 日期搜索")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 测试日期搜索
            response = await client.post(
                f"{BASE_URL}/api/v1/agent/chat",
                json={"query": "查找1.18的照片", "top_k": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Agent 日期搜索成功")
                print(f"  意图: {data.get('intent')}")
                print(f"  回复: {data.get('answer', '')[:200]}...")
                
                results = data.get('results')
                if results:
                    print(f"  结果总数: {results.get('total', 0)}")
                
                return True
            else:
                print(f"✗ 失败: HTTP {response.status_code}")
                print(f"  响应: {response.text}")
                return False
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False

async def test_agent_chat_time_semantic_search():
    """测试 Agent 聊天 - 时间+语义搜索"""
    print("\n" + "=" * 60)
    print("测试 6: Agent 聊天 - 时间+语义搜索")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 测试时间+语义搜索
            response = await client.post(
                f"{BASE_URL}/api/v1/agent/chat",
                json={"query": "查找去年的海边照片", "top_k": 10}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Agent 时间+语义搜索成功")
                print(f"  意图: {data.get('intent')}")
                print(f"  回复: {data.get('answer', '')[:300]}...")
                
                results = data.get('results')
                if results:
                    print(f"  结果总数: {results.get('total', 0)}")
                    images = results.get('images', [])
                    if images:
                        print(f"  找到 {len(images)} 张图片")
                        for i, img in enumerate(images[:3]):
                            print(f"    {i+1}. {img.get('filename', 'N/A')}")
                
                return True
            else:
                print(f"✗ 失败: HTTP {response.status_code}")
                print(f"  响应: {response.text}")
                return False
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False

async def test_agent_chat_specific_date():
    """测试 Agent 聊天 - 具体日期"""
    print("\n" + "=" * 60)
    print("测试 7: Agent 聊天 - 具体日期")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 测试具体日期搜索
            response = await client.post(
                f"{BASE_URL}/api/v1/agent/chat",
                json={"query": "2023年7月的海边照片", "top_k": 10}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Agent 具体日期搜索成功")
                print(f"  意图: {data.get('intent')}")
                print(f"  回复: {data.get('answer', '')[:300]}...")
                
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
        return False

async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("Agent 工具调用修复验证")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 基础 URL: {BASE_URL}")
    print()
    
    # 运行所有测试
    tests = [
        ("获取当前时间工具", test_get_current_time),
        ("元数据搜索工具", test_meta_search),
        ("混合搜索工具", test_hybrid_search),
        ("Agent 聊天 - 时间查询", test_agent_chat_time_query),
        ("Agent 聊天 - 日期搜索", test_agent_chat_date_search),
        ("Agent 聊天 - 时间+语义搜索", test_agent_chat_time_semantic_search),
        ("Agent 聊天 - 具体日期", test_agent_chat_specific_date),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
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
        print("\n✓ 所有测试通过！Agent 工具调用修复成功。")
    else:
        print(f"\n✗ 有 {failed} 个测试失败，请检查错误信息。")

if __name__ == "__main__":
    asyncio.run(main())