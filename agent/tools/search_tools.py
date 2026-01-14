"""
智能搜索工具集
提供文本搜索、以图搜图、混合搜索等功能
"""

import requests
from typing import List, Dict, Optional


class SearchTools:
    """搜索操作工具类"""

    def __init__(self, api_base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = api_base_url
        self.search_url = f"{api_base_url}/search"

    def search_by_text(
        self,
        query: str,
        top_k: int = 10,
        score_threshold: float = 0.0
    ) -> List[Dict]:
        """
        工具：通过文本语义搜索图片

        Args:
            query: 搜索查询文本（如"蓝天白云"、"海边日落"）
            top_k: 返回结果数量
            score_threshold: 相似度阈值（0-1）

        Returns:
            相似图片列表，包含ID、路径、相似度分数
        """
        response = requests.get(
            f"{self.search_url}/text",
            params={
                "query": query,
                "top_k": top_k,
                "score_threshold": score_threshold
            }
        )

        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"文本搜索失败: {response.text}")

    def search_by_image_id(
        self,
        image_id: str,
        top_k: int = 10,
        score_threshold: float = 0.0
    ) -> List[Dict]:
        """
        工具：以图搜图（使用已上传的图片ID）

        Args:
            image_id: 参考图片的ID
            top_k: 返回结果数量
            score_threshold: 相似度阈值

        Returns:
            相似图片列表
        """
        response = requests.get(
            f"{self.search_url}/image/{image_id}",
            params={
                "top_k": top_k,
                "score_threshold": score_threshold
            }
        )

        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"以图搜图失败: {response.text}")

    def search_by_image_file(
        self,
        image_path: str,
        top_k: int = 10,
        score_threshold: float = 0.0
    ) -> List[Dict]:
        """
        工具：以图搜图（上传本地图片文件）

        Args:
            image_path: 本地图片路径
            top_k: 返回结果数量
            score_threshold: 相似度阈值

        Returns:
            相似图片列表
        """
        with open(image_path, "rb") as f:
            response = requests.post(
                f"{self.search_url}/image",
                files={"file": f},
                data={
                    "top_k": top_k,
                    "score_threshold": score_threshold
                }
            )

        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"以图搜图失败: {response.text}")

    def search_hybrid(
        self,
        query_text: Optional[str] = None,
        query_image_id: Optional[str] = None,
        top_k: int = 10,
        text_weight: float = 0.5,
        image_weight: float = 0.5,
        score_threshold: float = 0.0
    ) -> List[Dict]:
        """
        工具：图文混合搜索

        Args:
            query_text: 搜索文本
            query_image_id: 参考图片ID
            top_k: 返回结果数量
            text_weight: 文本权重
            image_weight: 图片权重
            score_threshold: 相似度阈值

        Returns:
            相似图片列表
        """
        response = requests.post(
            f"{self.search_url}/hybrid",
            json={
                "query_text": query_text,
                "query_image_id": query_image_id,
                "top_k": top_k,
                "text_weight": text_weight,
                "image_weight": image_weight,
                "score_threshold": score_threshold
            }
        )

        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"混合搜索失败: {response.text}")

    def advanced_search(
        self,
        query_text: Optional[str] = None,
        query_image_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        top_k: int = 10,
        score_threshold: float = 0.0
    ) -> List[Dict]:
        """
        工具：高级搜索（支持标签过滤）

        Args:
            query_text: 搜索文本
            query_image_id: 参考图片ID
            tags: 标签过滤
            top_k: 返回结果数量
            score_threshold: 相似度阈值

        Returns:
            相似图片列表
        """
        payload = {
            "top_k": top_k,
            "score_threshold": score_threshold
        }

        if query_text:
            payload["query_text"] = query_text
        if query_image_id:
            payload["query_image_id"] = query_image_id
        if tags:
            payload["tags"] = tags

        response = requests.post(f"{self.search_url}/", json=payload)

        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"高级搜索失败: {response.text}")
