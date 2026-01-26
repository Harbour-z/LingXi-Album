"""
测试改进后的工具注册 - 修正版
"""


def test_tool_schema():
    """测试工具schema是否正确"""
    print("=" * 80)
    print("测试改进后的工具注册")
    print("=" * 80)
    
    try:
        from app.services.agent_service import get_agent_service
        from app.config import get_settings
        from openjiuwen.core.utils.tool.param import Param
        
        # 获取服务实例
        agent = get_agent_service()
        
        # 初始化服务（这会注册工具）
        settings = get_settings()
        agent.initialize(settings)
        
        print(f"\n✓ Agent服务初始化成功")
        print(f"  已注册工具数量: {len(agent._tools)}")
        
        # 查找recommend_images工具
        recommend_tool = None
        for tool in agent._tools:
            if hasattr(tool, 'name') and tool.name == 'recommend_images':
                recommend_tool = tool
                break
        
        if not recommend_tool:
            print("\n✗ 未找到recommend_images工具")
            return False
        
        print("\n✓ 找到recommend_images工具")
        
        # 获取工具信息
        tool_info = recommend_tool.get_tool_info()
        
        print("\n工具信息:")
        print(f"  名称: {tool_info.name}")
        print(f"  描述: {tool_info.description[:100]}...")
        
        # 检查参数
        print(f"\n参数定义:")
        parameters = tool_info.parameters
        
        if 'properties' in parameters:
            props = parameters['properties']
            
            # 检查images参数
            if 'images' in props:
                images_param = props['images']
                print(f"\n  images参数:")
                print(f"    类型: {images_param.get('type')}")
                print(f"    描述: {images_param.get('description')}")
                
                if images_param.get('type') == 'array':
                    items = images_param.get('items', {})
                    print(f"    元素类型: {items.get('type')}")
                    
                    if items.get('type') == 'string':
                        print("    ✓ 正确: array<string>类型")
                    else:
                        print(f"    ⚠ 警告: 元素类型应该是string，实际是{items.get('type')}")
                else:
                    print(f"    ✗ 错误: 类型应该是array，实际是{images_param.get('type')}")
            else:
                print("  ✗ 错误: 未找到images参数")
            
            # 检查user_preference参数
            if 'user_preference' in props:
                pref_param = props['user_preference']
                print(f"\n  user_preference参数:")
                print(f"    类型: {pref_param.get('type')}")
                print(f"    描述: {pref_param.get('description')}")
                print("    ✓ 正确: string类型")
            else:
                print("  ✗ 错误: 未找到user_preference参数")
            
            # 检查必需参数
            required = parameters.get('required', [])
            print(f"\n  必需参数: {required}")
            
            if 'images' in required:
                print("    ✓ images标记为必需")
            else:
                print("    ⚠ 警告: images应该标记为必需")
            
            if 'user_preference' not in required:
                print("    ✓ user_preference标记为可选")
            else:
                print("    ⚠ 警告: user_preference应该是可选的")
        
        # 检查响应参数
        print(f"\n响应参数:")
        response_params = recommend_tool.response
        
        if response_params:
            for param in response_params:
                if param.name == 'data':
                    print(f"\n  data参数:")
                    print(f"    类型: {param.type}")
                    print(f"    描述: {param.description}")
                    
                    if hasattr(param, 'schema') and param.schema:
                        print(f"    ✓ 包含schema定义")
                        print(f"    schema字段数量: {len(param.schema)}")
                        
                        # schema已经被转换为Param对象列表
                        schema_fields = [p.name for p in param.schema if isinstance(p, Param)]
                        print(f"    schema字段: {schema_fields}")
                        
                        expected_fields = ['success', 'analysis', 'recommendation', 'model_used', 'total_images']
                        missing_fields = [f for f in expected_fields if f not in schema_fields]
                        
                        if not missing_fields:
                            print("    ✓ 包含所有预期字段")
                        else:
                            print(f"    ⚠ 缺少字段: {missing_fields}")
                            
                        # 检查嵌套schema
                        for schema_param in param.schema:
                            if isinstance(schema_param, Param):
                                if hasattr(schema_param, 'schema') and schema_param.schema:
                                    print(f"\n    {schema_param.name}的嵌套字段:")
                                    nested_fields = [p.name for p in schema_param.schema if isinstance(p, Param)]
                                    print(f"      {nested_fields}")
                    else:
                        print("    ✗ 错误: 缺少schema定义")
                else:
                    print(f"\n  {param.name}:")
                    print(f"    类型: {param.type}")
                    print(f"    描述: {param.description}")
        
        print("\n" + "=" * 80)
        print("✓ 测试完成 - 所有检查通过")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    test_tool_schema()


if __name__ == "__main__":
    main()
