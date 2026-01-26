"""
测试 Agent 图片提取功能
验证 Agent 回复中的图片能否正确提取并返回给前端
"""

import asyncio
import requests
from app.services import get_agent_service

async def test_agent_image_extraction():
    """测试 Agent 是否能正确提取图片"""
    print("=" * 80)
    print("测试 Agent 图片提取功能")
    print("=" * 80)
    
    # 初始化 Agent 服务
    agent_svc = get_agent_service()
    if not agent_svc.is_initialized:
        print("初始化 Agent 服务...")
        agent_svc.initialize()
    
    # 测试查询
    test_queries = [
        "帮我找 1 张柴犬的照片",
        "搜索红色的跑车",
        "海边的照片"
    ]
    
    for query in test_queries:
        print(f"\n{'=' * 80}")
        print(f"测试查询: {query}")
        print('=' * 80)
        
        try:
            result = await agent_svc.chat(query, session_id="test_session")
            
            answer = result.get("answer", "")
            images = result.get("images", [])
            
            print(f"\n回复内容（前200字符）:")
            print(answer[:200])
            print(f"\n提取到的图片数量: {len(images)}")
            
            if images:
                print(f"\n图片详情:")
                for i, img in enumerate(images, 1):
                    img_id = img.get("id", "N/A")
                    preview_url = img.get("preview_url", "N/A")
                    has_metadata = img.get("metadata") is not None
                    print(f"  {i}. ID: {img_id}")
                    print(f"     Preview URL: {preview_url}")
                    print(f"     Has Metadata: {has_metadata}")
                    if has_metadata:
                        metadata = img.get("metadata", {})
                        filename = metadata.get("filename", "N/A")
                        file_size = metadata.get("file_size", "N/A")
                        print(f"     Filename: {filename}, Size: {file_size} bytes")
            else:
                print("未提取到图片")
                
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_agent_image_extraction())
