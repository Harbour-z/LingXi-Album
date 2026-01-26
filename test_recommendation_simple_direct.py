"""
直接测试图片推荐功能
"""

import requests
import json


def test_agent_chat_with_recommendation():
    """测试Agent聊天和推荐功能"""
    print("=" * 80)
    print("测试Agent聊天和图片推荐功能")
    print("=" * 80)

    url = "http://localhost:8000/api/v1/agent/chat"
    session_id = "test_recommendation_simple_direct"

    # 测试1: 搜索图片
    print("\n【测试1】搜索图片")
    print("-" * 80)
    search_query = "找两张柴犬的图片"
    print(f"查询: {search_query}")

    payload = {
        "query": search_query,
        "session_id": session_id
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            result = response.json()
            print("✓ 搜索成功")
            print(f"  回复: {result.get('answer', '')[:200]}...")
            print(f"  图片数量: {result.get('results', {}).get('total', 0)}")
            
            if result.get('results', {}).get('images'):
                image_ids = [img.get('id') for img in result['results']['images']]
                print(f"  图片ID: {image_ids}")
                
                # 测试2: 推荐图片
                print("\n【测试2】推荐图片")
                print("-" * 80)
                recommend_query = "前两张哪张拍的比较好，为什么"
                print(f"查询: {recommend_query}")

                payload = {
                    "query": recommend_query,
                    "session_id": session_id
                }

                response = requests.post(url, json=payload, timeout=120)
                if response.status_code == 200:
                    result = response.json()
                    print("✓ 推荐请求成功")
                    print(f"  回复: {result.get('answer', '')[:500]}...")
                    
                    recommendation = result.get('recommendation')
                    if recommendation:
                        print("\n  推荐信息:")
                        print(f"    推荐图片ID: {recommendation.get('recommended_image_id')}")
                        print(f"    备选图片数: {len(recommendation.get('alternative_image_ids', []))}")
                        print(f"    分析总数: {recommendation.get('total_images_analyzed')}")
                    else:
                        print("  ⚠ 没有推荐信息")
                else:
                    print(f"✗ 推荐请求失败: HTTP {response.status_code}")
                    print(f"  响应: {response.text[:500]}")
            else:
                print("  ⚠ 没有找到图片")
        else:
            print(f"✗ 搜索失败: HTTP {response.status_code}")
            print(f"  响应: {response.text[:500]}")
    except Exception as e:
        print(f"✗ 异常: {e}")
        import traceback
        traceback.print_exc()


def test_recommendation_api_direct():
    """直接测试图片推荐API"""
    print("\n" + "=" * 80)
    print("直接测试图片推荐API")
    print("=" * 80)

    url = "http://localhost:8000/api/v1/image-recommendation/analyze"

    # 先获取一些图片ID
    print("\n步骤1: 获取图片ID")
    print("-" * 80)
    search_url = "http://localhost:8000/api/v1/search/text"
    search_payload = {
        "query_text": "柴犬",
        "top_k": 3
    }

    try:
        search_response = requests.post(search_url, json=search_payload, timeout=60)
        if search_response.status_code == 200:
            search_result = search_response.json()
            images = search_result.get('results', [])
            
            if len(images) >= 2:
                image_ids = [img['id'] for img in images[:2]]
                print(f"✓ 获取到 {len(image_ids)} 张图片ID: {image_ids}")
                
                # 测试推荐API
                print("\n步骤2: 调用推荐API")
                print("-" * 80)
                rec_payload = {
                    "images": image_ids,
                    "user_preference": "我喜欢构图好的照片"
                }
                print(f"请求参数: {json.dumps(rec_payload, indent=2, ensure_ascii=False)}")

                rec_response = requests.post(url, json=rec_payload, timeout=180)
                if rec_response.status_code == 200:
                    rec_result = rec_response.json()
                    print("✓ 推荐API调用成功")
                    
                    data = rec_result.get('data', {})
                    if data.get('success'):
                        print("\n推荐结果:")
                        recommendation = data.get('recommendation', {})
                        print(f"  推荐图片ID: {recommendation.get('best_image_id')}")
                        print(f"  推荐理由: {recommendation.get('recommendation_reason', '')[:200]}...")
                        print(f"  使用的模型: {data.get('model_used')}")
                        print(f"  分析的图片数: {data.get('total_images')}")
                        
                        analysis = data.get('analysis', {})
                        if analysis:
                            print(f"\n  分析详情:")
                            for img_id, analysis_data in analysis.items():
                                print(f"    图片 {img_id}:")
                                print(f"      综合评分: {analysis_data.get('overall_score')}")
                                print(f"      构图评分: {analysis_data.get('composition_score')}")
                                print(f"      色彩评分: {analysis_data.get('color_score')}")
                    else:
                        print(f"✗ 推荐失败: {data.get('error')}")
                        if 'details' in data:
                            print(f"  详细信息: {data['details']}")
                else:
                    print(f"✗ 推荐API调用失败: HTTP {rec_response.status_code}")
                    print(f"  响应: {rec_response.text[:500]}")
            else:
                print(f"✗ 需要至少2张图片，当前只有 {len(images)} 张")
        else:
            print(f"✗ 搜索失败: HTTP {search_response.status_code}")
    except Exception as e:
        print(f"✗ 异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_agent_chat_with_recommendation()
    test_recommendation_api_direct()
