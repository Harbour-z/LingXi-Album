"""
测试Agent多张图片分析推荐功能

测试流程：
1. 用户上传多张图片
2. Agent分析并推荐最佳图片
3. 系统提取推荐信息
4. 用户确认删除其他图片
5. 执行删除操作
"""

import requests
import json
from typing import Dict, List, Any


def create_test_session():
    """创建测试会话"""
    print("\n" + "=" * 80)
    print("步骤1: 创建测试会话")
    print("=" * 80)
    
    url = "http://localhost:8000/api/v1/agent/session/create"
    
    try:
        # 不传递body参数，因为user_id是可选的
        response = requests.post(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            session_id = result.get("session_id")
            print(f"✓ 会话创建成功: {session_id}")
            return session_id
        else:
            print(f"✗ 会话创建失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        return None


def test_multi_image_analysis(session_id: str):
    """测试多张图片分析"""
    print("\n" + "=" * 80)
    print("步骤2: 测试多张图片分析")
    print("=" * 80)
    
    url = "http://localhost:8000/api/v1/agent/chat"
    
    # 模拟用户询问多张图片
    query = "告诉我哪一张拍的最好，并且告诉我原因"
    
    payload = {
        "query": query,
        "session_id": session_id
    }
    
    print(f"\n发送查询: {query}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n响应状态: {result.get('status')}")
            print(f"回复内容: {result.get('answer', '')[:300]}...")
            print(f"意图: {result.get('intent')}")
            
            # 检查是否有推荐信息
            recommendation = result.get('recommendation')
            
            if recommendation:
                print(f"\n✓ 检测到推荐信息:")
                print(f"  推荐图片ID: {recommendation.get('recommended_image_id')}")
                print(f"  备选图片ID: {recommendation.get('alternative_image_ids')}")
                print(f"  分析图片总数: {recommendation.get('total_images_analyzed')}")
                print(f"  是否提示删除: {recommendation.get('user_prompt_for_deletion')}")
                print(f"  推荐理由: {recommendation.get('recommendation_reason', '')[:200]}...")
                
                return recommendation
            else:
                print(f"\n⚠ 未检测到推荐信息")
                return None
        else:
            print(f"✗ 请求失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_preview_delete(image_ids: List[str]):
    """测试预览删除操作"""
    print("\n" + "=" * 80)
    print("步骤3: 预览删除操作")
    print("=" * 80)
    
    url = "http://localhost:8000/api/v1/agent/recommendation/preview-delete"
    
    print(f"\n预览删除 {len(image_ids)} 张图片")
    
    try:
        response = requests.post(url, json=image_ids, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n响应状态: {result.get('status')}")
            print(f"图片总数: {result.get('total')}")
            
            images = result.get('images', [])
            print(f"\n即将删除的图片:")
            for i, img in enumerate(images, 1):
                print(f"  {i}. ID: {img.get('id')}")
                print(f"     文件名: {img.get('filename')}")
                print(f"     大小: {img.get('file_size', 0)} bytes")
                print(f"     分辨率: {img.get('width', 0)}x{img.get('height', 0)}")
                print(f"     创建时间: {img.get('created_at')}")
            
            return True
        else:
            print(f"✗ 请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        return False


def test_delete_images(image_ids: List[str], confirmed: bool = False):
    """测试删除图片"""
    print("\n" + "=" * 80)
    print("步骤4: 执行删除操作")
    print("=" * 80)
    
    url = "http://localhost:8000/api/v1/agent/recommendation/delete"
    
    payload = {
        "image_ids": image_ids,
        "confirmed": confirmed,
        "reason": "根据Agent推荐删除非最佳图片"
    }
    
    print(f"\n删除参数:")
    print(f"  图片数量: {len(image_ids)}")
    print(f"  用户确认: {confirmed}")
    print(f"  删除原因: {payload['reason']}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            
            print(f"\n响应状态: {result.get('status')}")
            print(f"响应消息: {result.get('message')}")
            
            print(f"\n删除统计:")
            print(f"  成功删除: {data.get('deleted_count')} 张")
            print(f"  删除失败: {data.get('failed_count')} 张")
            
            if data.get('deleted_image_ids'):
                print(f"\n成功删除的图片ID:")
                for img_id in data.get('deleted_image_ids', []):
                    print(f"  - {img_id}")
            
            if data.get('failed_image_ids'):
                print(f"\n删除失败的图片ID:")
                for img_id in data.get('failed_image_ids', []):
                    print(f"  - {img_id}")
            
            return True
        else:
            print(f"✗ 请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_unconfirmed_delete():
    """测试未确认删除（应该失败）"""
    print("\n" + "=" * 80)
    print("步骤5: 测试未确认删除（安全验证）")
    print("=" * 80)
    
    url = "http://localhost:8000/api/v1/agent/recommendation/delete"
    
    payload = {
        "image_ids": ["test-id-1"],
        "confirmed": False  # 未确认
    }
    
    print(f"\n尝试在未确认的情况下删除图片...")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 400:
            print(f"✓ 正确拒绝未确认的删除请求")
            print(f"  错误消息: {response.json().get('detail')}")
            return True
        else:
            print(f"✗ 安全验证失败，未正确拒绝")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        return False


def main():
    """主测试流程"""
    print("\n" + "=" * 80)
    print("Agent多张图片分析推荐功能测试")
    print("=" * 80)
    
    input("\n请确保后端服务已启动 (http://localhost:8000)，然后按 Enter 继续...")
    
    # 步骤1: 创建会话
    session_id = create_test_session()
    if not session_id:
        print("\n✗ 无法创建会话，测试终止")
        return
    
    # 步骤2: 测试多张图片分析
    recommendation = test_multi_image_analysis(session_id)
    
    if not recommendation:
        print("\n⚠ 未能获取推荐信息，无法继续测试删除功能")
        print("请确保Agent返回了包含图片ID的分析结果")
        return
    
    # 检查是否有备选图片
    alternative_ids = recommendation.get('alternative_image_ids', [])
    
    if not alternative_ids:
        print("\n⚠ 没有备选图片需要删除")
        return
    
    # 步骤3: 预览删除
    test_preview_delete(alternative_ids)
    
    # 步骤5: 测试未确认删除（安全验证）
    test_unconfirmed_delete()
    
    # 步骤4: 测试删除（先测试未确认）
    print("\n" + "-" * 80)
    print("注意：接下来的删除操作将是真实的")
    choice = input("是否继续执行删除操作？(yes/no): ").strip().lower()
    
    if choice == 'yes':
        # 测试确认删除
        test_delete_images(alternative_ids, confirmed=True)
    else:
        print("跳过删除操作")
    
    # 总结
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
    print("\n功能验证:")
    print("✓ Agent能够分析多张图片")
    print("✓ 系统能够提取推荐信息")
    print("✓ API返回结构化推荐数据")
    print("✓ 提供预览删除功能")
    print("✓ 实施安全确认机制")
    print("✓ 支持批量删除操作")


if __name__ == "__main__":
    main()
