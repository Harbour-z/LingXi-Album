"""
相册管理工具集
提供图片上传、删除、查看等操作
"""

import requests
from typing import List, Dict, Optional
from pathlib import Path


class AlbumTools:
    """相册操作工具类"""

    def __init__(self, api_base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = api_base_url
        self.storage_url = f"{api_base_url}/storage"

    def upload_image(
        self,
        image_path: str,
        tags: Optional[List[str]] = None,
        description: str = "",
        auto_index: bool = True,
        async_index: bool = True
    ) -> Dict:
        """
        工具：上传图片到相册

        Args:
            image_path: 图片路径
            tags: 标签列表
            description: 图片描述
            auto_index: 是否自动索引
            async_index: 是否异步索引

        Returns:
            包含图片ID、路径等信息的字典
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        with open(image_path, "rb") as f:
            response = requests.post(
                f"{self.storage_url}/upload",
                files={"file": f},
                data={
                    "auto_index": auto_index,
                    "async_index": async_index,
                    "tags": ",".join(tags) if tags else "",
                    "description": description
                }
            )

        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"上传失败: {response.text}")

    def delete_image(self, image_id: str, delete_vector: bool = True) -> bool:
        """
        工具：删除图片

        Args:
            image_id: 图片ID
            delete_vector: 是否同时删除向量索引

        Returns:
            删除是否成功
        """
        response = requests.delete(
            f"{self.storage_url}/images/{image_id}",
            params={"delete_vector": delete_vector}
        )

        return response.status_code == 200

    def get_image_info(self, image_id: str) -> Dict:
        """
        工具：获取图片详细信息

        Args:
            image_id: 图片ID

        Returns:
            图片元数据信息
        """
        response = requests.get(f"{self.storage_url}/images/{image_id}/info")

        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"获取图片信息失败: {response.text}")

    def list_images(
        self,
        skip: int = 0,
        limit: int = 20,
        tags: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        工具：列出相册中的图片

        Args:
            skip: 跳过数量
            limit: 返回数量
            tags: 筛选标签

        Returns:
            图片列表
        """
        params = {"skip": skip, "limit": limit}
        if tags:
            params["tags"] = ",".join(tags)

        response = requests.get(f"{self.storage_url}/images", params=params)

        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"获取图片列表失败: {response.text}")

    def batch_upload(self, image_dir: str, tags: Optional[List[str]] = None) -> List[Dict]:
        """
        工具：批量上传目录下的所有图片

        Args:
            image_dir: 图片目录路径
            tags: 统一标签

        Returns:
            上传结果列表
        """
        dir_path = Path(image_dir)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"不是有效目录: {image_dir}")

        results = []
        for image_file in dir_path.glob("*"):
            if image_file.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
                try:
                    result = self.upload_image(str(image_file), tags=tags)
                    results.append(result)
                except Exception as e:
                    print(f"上传失败 {image_file.name}: {e}")

        return results

    def get_system_status(self) -> Dict:
        """
        工具：获取系统状态

        Returns:
            系统状态信息
        """
        response = requests.get("http://localhost:8000/status")

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"获取系统状态失败: {response.text}")
