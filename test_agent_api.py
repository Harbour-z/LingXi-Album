"""
测试 Agent API 接口
验证图片是否能正确返回
"""

import requests
import json

def test_agent_chat_api():
    """测试 Agent 聊天 API"""
    print("=" * 80)
    print("测试 Agent Chat API - 图片返回功能")
    print("=" * 80)
    
    base_url = "http://localhost:8000/api/v1"
    
    # 测试查询
    test_queries = [
        "帮我找 1 张柴犬的照片",
    ]
    
    for query in test_queries:
        print(f"\n{'=' * 80}")
        print(f"测试查询: {query}")
        print('=' * 80)
        
        try:
            response = requests.post(
                f"{base_url}/agent/chat",
                json={
                    "query": query,
                    "top_k": 5
                },
                timeout=60
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # 检查响应结构
                session_id = result.get("session_id")
                answer = result.get("answer", "")
                intent = result.get("intent", "")
                results = result.get("results")
                suggestions = result.get("suggestions", [])
                
                print(f"\nSession ID: {session_id}")
                print(f"Intent: {intent}")
                print(f"回复内容（前200字符）:")
                print(answer[:200])
                
                # 检查图片结果
                if results:
                    total = results.get("total", 0)
                    images = results.get("images", [])
                    
                    print(f"\n图片结果:")
                    print(f"  总数: {total}")
                    print(f"  图片列表长度: {len(images)}")
                    
                    if images:
                        print(f"\n  图片详情:")
                        for i, img in enumerate(images[:3], 1):
                            img_id = img.get("id", "N/A")
                            preview_url = img.get("preview_url", "N/A")
                            metadata = img.get("metadata")
                            score = img.get("score", "N/A")
                            
                            print(f"    {i}. ID: {img_id}")
                            print(f"       Preview URL: {preview_url}")
                            print(f"       Score: {score}")
                            print(f"       Has Metadata: {metadata is not None}")
                            
                            if metadata:
                                filename = metadata.get("filename", "N/A")
                                file_size = metadata.get("file_size", "N/A")
                                print(f"       Filename: {filename}")
                                print(f"       Size: {file_size} bytes")
                    else:
                        print("  ✗ 没有返回图片")
                        
                        # 打印完整的 results 对象用于调试
                        print(f"\n  Debug - results 对象:")
                        print(json.dumps(results, indent=2, ensure_ascii=False))
                else:
                    print("\n✗ results 字段为空或不存在")
                    print(f"\n  Debug - 完整响应:")
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                
                print(f"\n建议: {suggestions}")
            else:
                print(f"✗ 请求失败: {response.text}")
                
        except Exception as e:
            print(f"✗ 请求异常: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_agent_chat_api()
