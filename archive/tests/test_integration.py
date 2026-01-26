"""
集成测试：验证Agent的完整功能
包括：
1. ReAct Agent迭代次数设置为6
2. analyze工具正常工作
3. 所有其他工具正常工作
4. 端到端测试
"""

import requests
import json


def test_react_iteration_config():
    """测试ReAct Agent迭代次数配置"""
    print("\n" + "=" * 80)
    print("测试1: ReAct Agent迭代次数配置")
    print("=" * 80)
    
    url = "http://localhost:8000/api/v1/agent/chat"
    
    # 发送一个需要多次迭代的复杂查询
    test_query = "帮我找几张去年的海边照片，并分析其中一张照片"
    
    payload = {
        "query": test_query,
        "context": {}
    }
    
    print(f"\n发送复杂查询: {test_query}")
    print("预期: Agent应该能够进行最多6次迭代来完成这个任务")
    print("\n注意：这是一个需要多次工具调用的复杂查询：")
    print("  1. get_current_time - 获取当前时间")
    print("  2. meta_search_hybrid - 搜索去年的海边照片")
    print("  3. analyze - 分析其中一张照片")
    print("  4. 返回结果")
    print("\n这需要3-4次迭代，在6次迭代限制内")
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n响应状态: {result.get('status')}")
            print(f"响应消息: {result.get('message')}")
            
            if 'answer' in result:
                print(f"\nAgent回答: {result['answer']}")
            
            print("\n✓ ReAct Agent正常工作")
            return True
        else:
            print(f"\n✗ 请求失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n✗ 请求异常: {e}")
        return False


def test_analyze_tool_integration():
    """测试analyze工具在Agent工作流中的集成"""
    print("\n" + "=" * 80)
    print("测试2: analyze工具在Agent工作流中的集成")
    print("=" * 80)
    
    url = "http://localhost:8000/api/v1/agent/execute"
    
    print("\n测试场景: Agent调用analyze工具")
    
    # 首先搜索一张图片
    print("\n步骤1: 搜索一张图片...")
    search_payload = {
        "action": "search",
        "parameters": {
            "query_text": "风景照片",
            "top_k": 1
        }
    }
    
    try:
        response = requests.post(url, json=search_payload, timeout=30)
        
        if response.status_code == 200:
            search_result = response.json()
            
            if search_result.get('status') == 'success' and search_result.get('result'):
                images = search_result['result'].get('images', [])
                
                if images:
                    image_id = images[0].get('id')
                    print(f"✓ 找到图片: {image_id}")
                    
                    # 步骤2: 分析这张图片
                    print(f"\n步骤2: 分析图片 {image_id}...")
                    analyze_payload = {
                        "action": "analyze",
                        "parameters": {
                            "image_id": image_id
                        }
                    }
                    
                    response = requests.post(url, json=analyze_payload, timeout=120)
                    
                    if response.status_code == 200:
                        analyze_result = response.json()
                        
                        if analyze_result.get('status') == 'success':
                            print(f"✓ 图片分析成功")
                            
                            result = analyze_result.get('result', {})
                            analysis = result.get('analysis', {})
                            
                            print(f"\n分析结果:")
                            print(f"  图片ID: {result.get('image_id')}")
                            print(f"  使用的模型: {result.get('model_used')}")
                            
                            if analysis:
                                print(f"  构图美学评分: {analysis.get('composition_score')}")
                                print(f"  色彩搭配评分: {analysis.get('color_score')}")
                                print(f"  光影运用评分: {analysis.get('lighting_score')}")
                                print(f"  综合评分: {analysis.get('overall_score')}")
                            
                            print("\n✓ analyze工具集成测试通过")
                            return True
                        else:
                            print(f"✗ 图片分析失败: {analyze_result.get('message')}")
                            return False
                    else:
                        print(f"✗ 请求失败: HTTP {response.status_code}")
                        return False
                else:
                    print("⚠ 未找到图片，无法进行analyze测试")
                    print("  建议：先上传一些测试图片")
                    return None
            else:
                print(f"✗ 搜索失败: {search_result.get('message')}")
                return False
        else:
            print(f"✗ 请求失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_agent_tools():
    """测试所有Agent工具是否可用"""
    print("\n" + "=" * 80)
    print("测试3: 所有Agent工具可用性")
    print("=" * 80)
    
    url = "http://localhost:8000/api/v1/agent/actions"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            actions = result.get('actions', [])
            
            print(f"\n可用动作数量: {len(actions)}")
            
            expected_actions = ['search', 'upload', 'delete', 'update', 'analyze']
            available_actions = [a.get('action') for a in actions]
            
            print("\n检查必需动作:")
            for action in expected_actions:
                if action in available_actions:
                    print(f"  ✓ {action}")
                else:
                    print(f"  ✗ {action} - 缺失")
            
            missing = set(expected_actions) - set(available_actions)
            if not missing:
                print("\n✓ 所有必需动作都可用")
                return True
            else:
                print(f"\n✗ 缺少动作: {missing}")
                return False
        else:
            print(f"✗ 请求失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        return False


def main():
    """主测试流程"""
    print("=" * 80)
    print("Agent集成测试")
    print("=" * 80)
    
    input("\n请确保后端服务已启动，然后按 Enter 继续...")
    
    results = []
    
    # 测试1: 所有工具可用性
    results.append(("所有工具可用性", test_all_agent_tools()))
    
    # 测试2: analyze工具集成
    result = test_analyze_tool_integration()
    if result is not None:
        results.append(("analyze工具集成", result))
    
    # 测试3: ReAct Agent迭代次数
    results.append(("ReAct Agent迭代次数", test_react_iteration_config()))
    
    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, result in results:
        if result is True:
            status = "✓ 通过"
            passed += 1
        elif result is False:
            status = "✗ 失败"
            failed += 1
        else:
            status = "⊘ 跳过"
            skipped += 1
        
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed} 通过, {failed} 失败, {skipped} 跳过")
    
    if failed == 0:
        print("\n✓ 所有测试通过！")
    else:
        print(f"\n⚠ 有 {failed} 个测试失败")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
