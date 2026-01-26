"""
测试analyze工具功能
验证analyze工具是否能正确调用qwen3-vl-plus模型进行图片分析
"""

import requests
import json


def test_analyze_via_agent_execute():
    """测试通过agent/execute端点调用analyze动作"""
    print("=" * 80)
    print("测试analyze工具（通过agent/execute端点）")
    print("=" * 80)
    
    url = "http://localhost:8000/api/v1/agent/execute"
    
    # 准备测试请求
    test_cases = [
        {
            "name": "测试1：分析指定图片ID",
            "request": {
                "action": "analyze",
                "parameters": {
                    "image_id": "test-image-id"
                }
            },
            "expected_success": False,
            "expected_reason": "图片不存在"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}")
        print("-" * 80)
        
        try:
            response = requests.post(url, json=test_case['request'], timeout=60)
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"响应状态: {result.get('status')}")
                print(f"响应消息: {result.get('message')}")
                print(f"动作类型: {result.get('action')}")
                
                if 'result' in result:
                    print(f"结果: {json.dumps(result['result'], indent=2, ensure_ascii=False)}")
                
                # 验证预期结果
                success = result.get('status') == 'success'
                if success == test_case['expected_success']:
                    print("✓ 测试通过")
                else:
                    print(f"✗ 测试失败: 预期success={test_case['expected_success']}, 实际success={success}")
                    if test_case.get('expected_reason'):
                        print(f"  预期原因: {test_case['expected_reason']}")
            else:
                print(f"✗ 请求失败: HTTP {response.status_code}")
                print(f"响应内容: {response.text}")
                
        except Exception as e:
            print(f"✗ 请求异常: {e}")


def test_analyze_endpoint():
    """测试analyze端点是否可用"""
    print("\n" + "=" * 80)
    print("检查agent动作列表")
    print("=" * 80)
    
    url = "http://localhost:8000/api/v1/agent/actions"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            actions = result.get('actions', [])
            
            print(f"\n可用的动作数量: {len(actions)}")
            
            # 查找analyze动作
            analyze_action = None
            for action in actions:
                if action.get('action') == 'analyze':
                    analyze_action = action
                    break
            
            if analyze_action:
                print("\n✓ 找到analyze动作")
                print(f"  描述: {analyze_action.get('description')}")
                print(f"  参数: {json.dumps(analyze_action.get('parameters', {}), indent=2, ensure_ascii=False)}")
            else:
                print("\n✗ 未找到analyze动作")
        else:
            print(f"✗ 获取动作列表失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")


def main():
    """主测试流程"""
    print("\n" + "=" * 80)
    print("analyze工具功能测试")
    print("=" * 80)
    
    input("\n请确保后端服务已启动，然后按 Enter 继续...")
    
    # 测试1：检查analyze动作是否在列表中
    test_analyze_endpoint()
    
    # 测试2：调用analyze动作
    test_analyze_via_agent_execute()
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
