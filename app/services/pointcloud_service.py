"""
3DGS点云生成服务模块
调用外部3DGS服务将图片转换为3D点云(PLY格式)
"""

import os
import uuid
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import aiohttp

from ..config import get_settings
from ..models.schemas import PointCloudGenerationStatus

logger = logging.getLogger(__name__)


class PointCloudService:
    """
    3DGS点云生成服务类
    负责调用外部3DGS服务，管理点云文件的存储和检索
    """

    _instance: Optional["PointCloudService"] = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._initialized = getattr(self, '_initialized', False)
        self._storage_path: Optional[Path] = None
        self._service_url: Optional[str] = None
        self._timeout: int = 300
        self._pointclouds: Dict[str, Dict[str, Any]] = {}  # 内存缓存点云信息

    def initialize(
        self,
        storage_path: Optional[str] = None,
        service_url: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> None:
        """
        初始化点云生成服务

        Args:
            storage_path: 点云文件存储路径
            service_url: 3DGS服务URL
            timeout: 请求超时时间(秒)
        """
        if self._initialized:
            logger.info("点云生成服务已初始化，跳过重复初始化")
            return

        settings = get_settings()

        self._storage_path = Path(storage_path or settings.POINTCLOUD_STORAGE_PATH)
        self._storage_path.mkdir(parents=True, exist_ok=True)

        self._service_url = service_url or settings.POINTCLOUD_SERVICE_URL
        self._timeout = timeout or settings.POINTCLOUD_SERVICE_TIMEOUT

        self._initialized = True
        logger.info(f"点云生成服务初始化完成，存储路径: {self._storage_path}, 服务URL: {self._service_url}")

    @property
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized

    def _generate_id(self) -> str:
        """生成标准UUID"""
        return str(uuid.uuid4())

    def _get_storage_subdir(self, pointcloud_id: str) -> Path:
        """根据ID获取存储子目录（按日期分层存储）"""
        today = datetime.now().strftime("%Y/%m/%d")
        subdir = self._storage_path / today
        subdir.mkdir(parents=True, exist_ok=True)
        return subdir

    def _get_pointcloud_path(self, pointcloud_id: str) -> Path:
        """获取点云文件完整存储路径"""
        subdir = self._get_storage_subdir(pointcloud_id)
        return subdir / f"{pointcloud_id}.ply"

    async def generate_pointcloud(
        self,
        image_id: str,
        image_path: str,
        quality: str = "medium",
        async_mode: bool = True
    ) -> Dict[str, Any]:
        """
        生成点云文件

        Args:
            image_id: 来源图片ID
            image_path: 图片文件路径
            quality: 生成质量 (low/medium/high)
            async_mode: 是否异步生成

        Returns:
            点云生成结果字典
        """
        if not self.is_initialized:
            raise RuntimeError("点云生成服务未初始化")

        pointcloud_id = self._generate_id()

        # 初始化点云信息
        pointcloud_info = {
            "pointcloud_id": pointcloud_id,
            "status": PointCloudGenerationStatus.PENDING,
            "source_image_id": image_id,
            "quality": quality,
            "created_at": datetime.now(),
            "file_path": None,
            "file_size": None,
            "point_count": None,
            "error_message": None
        }

        self._pointclouds[pointcloud_id] = pointcloud_info

        if async_mode:
            # 异步生成
            asyncio.create_task(self._generate_pointcloud_async(
                pointcloud_id, image_path, quality
            ))
            logger.info(f"点云生成任务已启动 (异步): {pointcloud_id}")
        else:
            # 同步生成
            await self._generate_pointcloud_async(pointcloud_id, image_path, quality)
            logger.info(f"点云生成任务已完成 (同步): {pointcloud_id}")

        return pointcloud_info

    async def _generate_pointcloud_async(
        self,
        pointcloud_id: str,
        image_path: str,
        quality: str
    ) -> None:
        """
        异步生成点云的内部实现

        Args:
            pointcloud_id: 点云ID
            image_path: 图片路径
            quality: 生成质量
        """
        pointcloud_info = self._pointclouds.get(pointcloud_id)
        if not pointcloud_info:
            logger.error(f"点云信息不存在: {pointcloud_id}")
            return

        # 更新状态为处理中
        pointcloud_info["status"] = PointCloudGenerationStatus.PROCESSING
        logger.info(f"[PointCloudService] 点云任务状态更新 - ID: {pointcloud_id}, 状态: PROCESSING")

        try:
            # 调用3DGS服务
            result = await self._call_3dgs_service(image_path, quality)
            logger.info(f"[PointCloudService] 3DGS服务返回 - ID: {pointcloud_id}, success: {result.get('success')}")

            if result.get("success"):
                # 保存PLY文件
                ply_data = result.get("ply_data")
                point_count = result.get("point_count", 0)
                view_url = result.get("view_url")

                ply_path = self._get_pointcloud_path(pointcloud_id)
                with open(ply_path, "wb") as f:
                    f.write(ply_data)

                # 更新点云信息
                update_data = {
                    "status": PointCloudGenerationStatus.COMPLETED,
                    "file_path": str(ply_path.relative_to(self._storage_path)),
                    "file_size": len(ply_data),
                    "point_count": point_count,
                    "completed_at": datetime.now()
                }

                # 如果有预览 URL，保存它
                if view_url:
                    # 判断 view_url 是否已经是完整URL，避免重复拼接
                    if view_url.startswith("http://") or view_url.startswith("https://"):
                        update_data["view_url"] = view_url
                    else:
                        update_data["view_url"] = f"{self._service_url}{view_url}"

                pointcloud_info.update(update_data)
                logger.info(f"[PointCloudService] ✓ 点云任务状态更新 - ID: {pointcloud_id}, 状态: COMPLETED, view_url: {update_data.get('view_url')}")
            else:
                # 生成失败
                pointcloud_info.update({
                    "status": PointCloudGenerationStatus.FAILED,
                    "error_message": result.get("error", "Unknown error"),
                    "completed_at": datetime.now()
                })
                logger.error(f"[PointCloudService] ✗ 点云任务状态更新 - ID: {pointcloud_id}, 状态: FAILED, 错误: {result.get('error')}")

        except Exception as e:
            logger.error(f"点云生成异常: {pointcloud_id}, 错误: {e}", exc_info=True)
            pointcloud_info.update({
                "status": PointCloudGenerationStatus.FAILED,
                "error_message": str(e),
                "completed_at": datetime.now()
            })

    async def _call_3dgs_service(
        self,
        image_path: str,
        quality: str
    ) -> Dict[str, Any]:
        """
        调用外部3DGS服务

        Args:
            image_path: 图片路径
            quality: 生成质量 ('balanced' 或 'fast')

        Returns:
            服务响应结果
        """
        try:
            # 读取图片
            with open(image_path, "rb") as f:
                image_data = f.read()

            # 构造请求 - 使用新的 API 格式
            url = f"{self._service_url}/api/v1/generate"
            
            # 获取图片扩展名
            image_ext = Path(image_path).suffix.lower()

            # 构造 multipart/form-data
            # 在 aiohttp 中，需要将文件和表单数据合并到 data 参数中
            data = aiohttp.FormData()
            data.add_field(
                "image",
                image_data,
                filename=f"image{image_ext}",
                content_type=self._get_mime_type(image_ext)
            )
            data.add_field("quality", quality)
            data.add_field("return_format", "url")
            data.add_field("simplify_ply", "true")

            timeout = aiohttp.ClientTimeout(total=self._timeout)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        # 解析 JSON 响应
                        response_data = await response.json()
                        
                        if response_data.get("success"):
                            # 从返回的 URL 下载 PLY 文件
                            download_url = response_data.get("download_url")
                            view_url = response_data.get("view_url")
                            
                            if download_url:
                                ply_data, point_count = await self._download_ply_file(
                                    session, 
                                    f"{self._service_url}{download_url}"
                                )
                                
                                return {
                                    "success": True,
                                    "ply_data": ply_data,
                                    "point_count": point_count,
                                    "metadata": response_data.get("metadata", {}),
                                    "view_url": view_url  # 保存预览 URL
                                }
                            else:
                                return {
                                    "success": False,
                                    "error": "No download URL in response"
                                }
                        else:
                            return {
                                "success": False,
                                "error": response_data.get("error", "Unknown error")
                            }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Service returned {response.status}: {error_text}"
                        }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Request timeout"
            }
        except aiohttp.ClientError as e:
            return {
                "success": False,
                "error": f"HTTP client error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    async def _download_ply_file(
        self,
        session: aiohttp.ClientSession,
        url: str
    ) -> Tuple[bytes, int]:
        """
        从 URL 下载 PLY 文件并估算点数

        Args:
            session: aiohttp 会话
            url: PLY 文件下载 URL

        Returns:
            (PLY 文件数据, 估算的点数)
        """
        async with session.get(url) as response:
            if response.status == 200:
                ply_data = await response.read()
                # 简单估算点数：PLY 文件通常每个点约 40-50 字节
                # 这是一个粗略估计，实际点数可能需要解析 PLY 文件
                estimated_point_count = len(ply_data) // 45
                return ply_data, estimated_point_count
            else:
                raise Exception(f"Failed to download PLY file: {response.status}")

    def _get_mime_type(self, file_ext: str) -> str:
        """
        根据文件扩展名获取 MIME 类型

        Args:
            file_ext: 文件扩展名（包含点）

        Returns:
            MIME 类型字符串
        """
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
            ".heic": "image/heic",
            ".heif": "image/heif",
            ".tiff": "image/tiff",
            ".tif": "image/tiff"
        }
        return mime_types.get(file_ext.lower(), "image/jpeg")

    def get_pointcloud(self, pointcloud_id: str) -> Optional[Dict[str, Any]]:
        """
        获取点云信息

        Args:
            pointcloud_id: 点云ID

        Returns:
            点云信息字典或None
        """
        result = self._pointclouds.get(pointcloud_id)
        
        if result:
            logger.debug(f"[PointCloudService] 从内存缓存获取点云信息 - ID: {pointcloud_id}, 状态: {result.get('status')}, view_url: {result.get('view_url')}")
            return result
        
        # 如果内存缓存中没有，尝试从文件系统恢复任务信息
        logger.warning(f"[PointCloudService] 内存缓存中未找到点云 - ID: {pointcloud_id}, 尝试从文件系统恢复")
        
        try:
            # 尝试查找PLY文件
            ply_path = self._get_pointcloud_path(pointcloud_id)
            if ply_path.exists():
                # 文件存在，说明任务已完成，恢复任务信息
                file_stat = ply_path.stat()
                recovered_info = {
                    "pointcloud_id": pointcloud_id,
                    "status": PointCloudGenerationStatus.COMPLETED,
                    "file_path": str(ply_path.relative_to(self._storage_path)),
                    "file_size": file_stat.st_size,
                    "point_count": file_stat.st_size // 45,  # 粗略估计
                    "created_at": datetime.fromtimestamp(file_stat.st_ctime),
                    "completed_at": datetime.fromtimestamp(file_stat.st_mtime),
                    "view_url": None,  # 文件恢复时没有预览URL
                    "source_image_id": None,
                    "error_message": None
                }
                
                # 将恢复的信息保存到内存缓存
                self._pointclouds[pointcloud_id] = recovered_info
                logger.info(f"[PointCloudService] ✓ 从文件系统恢复点云信息 - ID: {pointcloud_id}")
                return recovered_info
        except Exception as e:
            logger.error(f"[PointCloudService] 从文件系统恢复点云信息失败 - ID: {pointcloud_id}, 错误: {e}")
        
        logger.warning(f"[PointCloudService] 点云不存在 - ID: {pointcloud_id}")
        return None

    def get_pointcloud_file(self, pointcloud_id: str) -> Optional[Tuple[bytes, str]]:
        """
        获取点云文件内容

        Args:
            pointcloud_id: 点云ID

        Returns:
            (文件内容, 媒体类型) 或 None
        """
        pointcloud_info = self.get_pointcloud(pointcloud_id)
        if not pointcloud_info or pointcloud_info["status"] != PointCloudGenerationStatus.COMPLETED:
            return None

        file_path = self._storage_path / pointcloud_info["file_path"]
        if not file_path.exists():
            return None

        with open(file_path, "rb") as f:
            content = f.read()

        return content, "application/octet-stream"

    def list_pointclouds(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        列出所有点云

        Args:
            page: 页码
            page_size: 每页数量

        Returns:
            (点云列表, 总数)
        """
        all_pointclouds = list(self._pointclouds.values())

        # 按创建时间倒序排序
        all_pointclouds.sort(key=lambda x: x["created_at"], reverse=True)

        # 分页
        total = len(all_pointclouds)
        start = (page - 1) * page_size
        end = start + page_size

        return all_pointclouds[start:end], total

    def delete_pointcloud(self, pointcloud_id: str) -> bool:
        """
        删除点云

        Args:
            pointcloud_id: 点云ID

        Returns:
            是否删除成功
        """
        pointcloud_info = self.get_pointcloud(pointcloud_id)
        if not pointcloud_info:
            return False

        # 删除文件
        if pointcloud_info["file_path"]:
            file_path = self._storage_path / pointcloud_info["file_path"]
            if file_path.exists():
                file_path.unlink()

        # 删除记录
        del self._pointclouds[pointcloud_id]

        logger.info(f"点云删除成功: {pointcloud_id}")
        return True

    def get_pointclouds_by_image(self, image_id: str) -> List[Dict[str, Any]]:
        """
        根据图片ID获取所有关联的点云

        Args:
            image_id: 图片ID

        Returns:
            点云列表
        """
        return [
            pc for pc in self._pointclouds.values()
            if pc["source_image_id"] == image_id
        ]

    def open_browser_preview(self, pointcloud_id: str) -> bool:
        """
        在浏览器中打开点云预览页面

        Args:
            pointcloud_id: 点云ID

        Returns:
            是否成功打开
        """
        pointcloud_info = self.get_pointcloud(pointcloud_id)
        if not pointcloud_info:
            logger.error(f"点云不存在: {pointcloud_id}")
            return False

        if pointcloud_info["status"] != PointCloudGenerationStatus.COMPLETED:
            logger.error(f"点云未完成生成: {pointcloud_id}, 状态: {pointcloud_info['status']}")
            return False

        view_url = pointcloud_info.get("view_url")
        if not view_url:
            logger.error(f"点云没有预览URL: {pointcloud_id}")
            return False

        try:
            import webbrowser
            logger.info(f"正在在浏览器中打开预览: {view_url}")
            webbrowser.open(view_url)
            return True
        except Exception as e:
            logger.error(f"打开浏览器失败: {e}")
            return False


# 全局服务实例
_pointcloud_service: Optional[PointCloudService] = None


def get_pointcloud_service() -> PointCloudService:
    """获取点云生成服务实例"""
    global _pointcloud_service
    if _pointcloud_service is None:
        _pointcloud_service = PointCloudService()
    return _pointcloud_service