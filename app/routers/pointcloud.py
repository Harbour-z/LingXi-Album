"""
3DGS点云生成API路由
提供图片转3D点云的接口
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import Response

from ..models import (
    BaseResponse,
    ResponseStatus,
    PointCloudRequest,
    PointCloudResponse,
    PointCloudResult,
    PointCloudListResponse,
)
from ..services import (
    get_pointcloud_service,
    PointCloudService,
    get_storage_service,
    StorageService
)

router = APIRouter(prefix="/pointcloud", tags=["PointCloud"])


def get_services():
    """获取服务依赖"""
    pointcloud_svc = get_pointcloud_service()
    storage_svc = get_storage_service()

    if not pointcloud_svc.is_initialized:
        raise HTTPException(status_code=503, detail="点云生成服务未初始化")

    return pointcloud_svc, storage_svc


@router.post(
    "/generate",
    response_model=PointCloudResponse,
    summary="生成3D点云",
    description="""
    将图片转换为3DGS点云(PLY格式)。
    - 支持异步生成（推荐），立即返回任务ID
    - 支持同步生成，等待生成完成
    - 生成质量可选: balanced(高质量) 或 fast(快速模式)
    """
)
async def generate_pointcloud(
    request: PointCloudRequest,
    services: tuple = Depends(get_services)
):
    """生成3D点云"""
    pointcloud_svc, storage_svc = services

    # 获取图片路径
    image_path = storage_svc.get_image_path(request.image_id)
    if not image_path:
        raise HTTPException(status_code=404, detail=f"图片不存在: {request.image_id}")

    # 生成点云
    result = await pointcloud_svc.generate_pointcloud(
        image_id=request.image_id,
        image_path=str(image_path),
        quality=request.quality,
        async_mode=request.async_mode
    )

    # 构造响应
    pointcloud_result = PointCloudResult(
        pointcloud_id=result["pointcloud_id"],
        status=result["status"],
        source_image_id=result["source_image_id"],
        file_path=result["file_path"],
        download_url=f"/api/v1/pointcloud/download/{result['pointcloud_id']}" if result.get("file_path") else None,
        view_url=result.get("view_url"),  # 添加预览 URL
        created_at=result["created_at"],
        completed_at=result.get("completed_at"),
        error_message=result.get("error_message"),
        file_size=result.get("file_size"),
        point_count=result.get("point_count")
    )

    return PointCloudResponse(
        status=ResponseStatus.SUCCESS,
        message="点云生成任务已创建" if request.async_mode else "点云生成完成",
        data=pointcloud_result
    )


@router.get(
    "/{pointcloud_id}",
    response_model=PointCloudResponse,
    summary="获取点云信息",
    description="根据ID获取点云生成状态和详细信息"
)
async def get_pointcloud(
    pointcloud_id: str,
    services: tuple = Depends(get_services)
):
    """获取点云信息"""
    pointcloud_svc, _ = services

    result = pointcloud_svc.get_pointcloud(pointcloud_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"点云不存在: {pointcloud_id}")

    # 构造响应
    pointcloud_result = PointCloudResult(
        pointcloud_id=result["pointcloud_id"],
        status=result["status"],
        source_image_id=result["source_image_id"],
        file_path=result["file_path"],
        download_url=f"/api/v1/pointcloud/download/{result['pointcloud_id']}" if result.get("file_path") else None,
        view_url=result.get("view_url"),  # 添加预览 URL
        created_at=result["created_at"],
        completed_at=result.get("completed_at"),
        error_message=result.get("error_message"),
        file_size=result.get("file_size"),
        point_count=result.get("point_count")
    )

    return PointCloudResponse(
        status=ResponseStatus.SUCCESS,
        message="获取成功",
        data=pointcloud_result
    )


@router.post(
    "/status",
    response_model=PointCloudResponse,
    summary="查询点云状态（POST方式）",
    description="根据ID查询点云生成状态（通过POST请求体传递参数，兼容OpenJiuwen）"
)
async def get_pointcloud_status_post(
    request: dict,
    services: tuple = Depends(get_services)
):
    """查询点云状态（POST方式）"""
    pointcloud_svc, _ = services
    
    # 从请求体中获取 pointcloud_id
    pointcloud_id = request.get("pointcloud_id")
    if not pointcloud_id:
        raise HTTPException(status_code=400, detail="缺少 pointcloud_id 参数")

    result = pointcloud_svc.get_pointcloud(pointcloud_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"点云不存在: {pointcloud_id}")

    # 构造响应
    pointcloud_result = PointCloudResult(
        pointcloud_id=result["pointcloud_id"],
        status=result["status"],
        source_image_id=result["source_image_id"],
        file_path=result["file_path"],
        download_url=f"/api/v1/pointcloud/download/{result['pointcloud_id']}" if result.get("file_path") else None,
        view_url=result.get("view_url"),  # 添加预览 URL
        created_at=result["created_at"],
        completed_at=result.get("completed_at"),
        error_message=result.get("error_message"),
        file_size=result.get("file_size"),
        point_count=result.get("point_count")
    )

    return PointCloudResponse(
        status=ResponseStatus.SUCCESS,
        message="获取成功",
        data=pointcloud_result
    )


@router.get(
    "/download/{pointcloud_id}",
    summary="下载点云文件",
    description="下载PLY格式的点云文件",
    responses={
        200: {
            "content": {"application/octet-stream": {}},
            "description": "PLY点云文件"
        }
    }
)
async def download_pointcloud(
    pointcloud_id: str,
    services: tuple = Depends(get_services)
):
    """下载点云文件"""
    pointcloud_svc, _ = services

    result = pointcloud_svc.get_pointcloud_file(pointcloud_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"点云文件不存在或未生成完成: {pointcloud_id}")

    content, media_type = result

    # 获取点云信息用于构造文件名
    pointcloud_info = pointcloud_svc.get_pointcloud(pointcloud_id)
    filename = f"{pointcloud_id}.ply"

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get(
    "/",
    response_model=PointCloudListResponse,
    summary="列出所有点云",
    description="分页获取所有点云生成记录"
)
async def list_pointclouds(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    services: tuple = Depends(get_services)
):
    """列出所有点云"""
    pointcloud_svc, _ = services

    pointclouds, total = pointcloud_svc.list_pointclouds(
        page=page,
        page_size=page_size
    )

    # 构造响应
    pointcloud_results = [
        PointCloudResult(
            pointcloud_id=pc["pointcloud_id"],
            status=pc["status"],
            source_image_id=pc["source_image_id"],
            file_path=pc["file_path"],
            download_url=f"/api/v1/pointcloud/download/{pc['pointcloud_id']}" if pc.get("file_path") else None,
            view_url=pc.get("view_url"),  # 添加预览 URL
            created_at=pc["created_at"],
            completed_at=pc.get("completed_at"),
            error_message=pc.get("error_message"),
            file_size=pc.get("file_size"),
            point_count=pc.get("point_count")
        )
        for pc in pointclouds
    ]

    return PointCloudListResponse(
        status=ResponseStatus.SUCCESS,
        message="获取成功",
        data=pointcloud_results,
        total=total
    )


@router.get(
    "/by-image/{image_id}",
    response_model=PointCloudListResponse,
    summary="获取图片关联的点云",
    description="获取指定图片的所有点云生成记录"
)
async def get_pointclouds_by_image(
    image_id: str,
    services: tuple = Depends(get_services)
):
    """获取图片关联的点云"""
    pointcloud_svc, _ = services

    pointclouds = pointcloud_svc.get_pointclouds_by_image(image_id)

    # 构造响应
    pointcloud_results = [
        PointCloudResult(
            pointcloud_id=pc["pointcloud_id"],
            status=pc["status"],
            source_image_id=pc["source_image_id"],
            file_path=pc["file_path"],
            download_url=f"/api/v1/pointcloud/download/{pc['pointcloud_id']}" if pc.get("file_path") else None,
            view_url=pc.get("view_url"),  # 添加预览 URL
            created_at=pc["created_at"],
            completed_at=pc.get("completed_at"),
            error_message=pc.get("error_message"),
            file_size=pc.get("file_size"),
            point_count=pc.get("point_count")
        )
        for pc in pointclouds
    ]

    return PointCloudListResponse(
        status=ResponseStatus.SUCCESS,
        message="获取成功",
        data=pointcloud_results,
        total=len(pointclouds)
    )


@router.delete(
    "/{pointcloud_id}",
    response_model=BaseResponse,
    summary="删除点云",
    description="删除点云文件及其记录"
)
async def delete_pointcloud(
    pointcloud_id: str,
    services: tuple = Depends(get_services)
):
    """删除点云"""
    pointcloud_svc, _ = services

    success = pointcloud_svc.delete_pointcloud(pointcloud_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"点云不存在: {pointcloud_id}")

    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        message="点云已删除"
    )


@router.post(
    "/{pointcloud_id}/preview",
    response_model=BaseResponse,
    summary="打开浏览器预览",
    description="在浏览器中打开点云的3D预览页面"
)
async def open_preview(
    pointcloud_id: str,
    services: tuple = Depends(get_services)
):
    """打开浏览器预览"""
    pointcloud_svc, _ = services

    success = pointcloud_svc.open_browser_preview(pointcloud_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"无法打开预览，点云不存在或未完成生成")

    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        message="已在浏览器中打开预览"
    )