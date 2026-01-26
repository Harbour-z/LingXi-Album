"""
简单测试智能图片推荐工具
"""

import requests


def test_health_check():
    """测试健康检查"""
    print("\n测试健康检查...")
    url = "http://localhost:8000/api/v1/image-recommendation/health"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 健康检查成功: {result}")
            return True
        else:
            print(f"✗ 健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False


def test_agent_tools():
    """测试Agent工具注册"""
    print("\n测试Agent工具注册...")
    try:
        from app.services.agent_service import get_agent_service
        agent_svc = get_agent_service()
        tools = agent_svc._tools  # 访问私有属性
        
        print(f"已注册工具数量: {len(tools)}")
        
        for i, tool in enumerate(tools, 1):
            tool_name = getattr(tool, 'name', 'unknown')
            print(f"  {i}. {tool_name}")
            
        return True
    except Exception as e:
        print(f"✗ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_docs():
    """测试API文档"""
    print("\n测试API文档...")
    url = "http://localhost:8000/openapi.json"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            openapi = response.json()
            paths = openapi.get("paths", {})
            
            rec_paths = [
                "/api/v1/image-recommendation/analyze",
                "/api/v1/image-recommendation/upload-analyze",
                "/api/v1/image-recommendation/health"
            ]
            
            found = [p for p in rec_paths if p in paths]
            print(f"找到 {len(found)}/{len(rec_paths)} 个图片推荐端点")
            
            return len(found) == len(rec_paths)
        else:
            print(f"✗ 获取失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False


def main():
    print("=" * 80)
    print("智能图片推荐工具简单测试")
    print("=" * 80)
    
    input("\n请确保后端服务已启动，然后按 Enter 继续...")
    
    results = []
    results.append(("健康检查", test_health_check()))
    results.append(("API文档", test_api_docs()))
    results.append(("Agent工具", test_agent_tools()))
    
    passed = sum(1 for _, r in results if r)
    failed = len(results) - passed
    
    print("\n测试总结:")
    print(f"通过: {passed}, 失败: {failed}")
    
    if failed == 0:
        print("\n✓ 所有测试通过！")
    else:
        print(f"\n⚠ {failed} 个测试失败")


if __name__ == "__main__":
    main()
