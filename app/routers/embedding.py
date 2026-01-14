"""
Embedding API路由
提供多模态Embedding生成接口
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends

from ..models import (
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingResult,
    ResponseStatus,
)
from ..services import get_embedding_service, EmbeddingService, get_storage_service, StorageService

router = APIRouter(prefix="/embedding", tags=["Embedding"])


def get_services():
    """获取服务依赖"""
    embedding_svc = get_embedding_service()
    storage_svc = get_storage_service()

    if not embedding_svc.is_initialized:
        raise HTTPException(status_code=503, detail="Embedding服务未初始化")

    return embedding_svc, storage_svc


@router.post(
    "/generate",
    response_model=EmbeddingResponse,
    summary="生成Embedding向量",
    description="""
    支持多种输入类型的Embedding向量生成：
    - 纯文本输入
    - 图片输入（通过图片ID或URL）
    - 图文混合输入
    
    返回归一化的向量表示，可用于后续的相似度计算和检索。
    """
)
async def generate_embedding(
    request: EmbeddingRequest,
    services: tuple = Depends(get_services)
):
    """
    生成Embedding向量

    - **inputs**: 输入列表，支持批量处理
    - **normalize**: 是否对向量进行L2归一化（默认True）
    """
    embedding_svc, storage_svc = services

    # 准备输入数据
    processed_inputs = []
    for inp in request.inputs:
        data = {}

        # 处理文本
        if inp.text:
            data["text"] = inp.text

        # 处理图片
        image_path = None
        if inp.image_id:
            path = storage_svc.get_image_path(inp.image_id)
            if path:
                image_path = str(path)
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"图片不存在: {inp.image_id}"
                )
        elif inp.image_url:
            image_path = inp.image_url

        if image_path:
            data["image"] = image_path

        # 处理指令
        if inp.instruction:
            data["instruction"] = inp.instruction

        if not data:
            raise HTTPException(
                status_code=400,
                detail="输入不能为空，必须提供text、image_id或image_url"
            )

        processed_inputs.append(data)

    # 生成Embedding
    embeddings = embedding_svc.generate_embeddings_batch(
        processed_inputs,
        normalize=request.normalize
    )

    # 构建响应
    results = [
        EmbeddingResult(
            index=i,
            embedding=emb,
            dimension=len(emb)
        )
        for i, emb in enumerate(embeddings)
    ]

    return EmbeddingResponse(
        status=ResponseStatus.SUCCESS,
        message="Embedding生成成功",
        data=results
    )


@router.post(
    "/text",
    response_model=EmbeddingResponse,
    summary="生成文本Embedding",
    description="快捷接口：仅处理文本输入"
)
async def generate_text_embedding(
    text: str,
    instruction: str = None,
    normalize: bool = True,
    services: tuple = Depends(get_services)
):
    """生成纯文本的Embedding向量"""
    embedding_svc, _ = services

    embedding = embedding_svc.generate_text_embedding(
        text=text,
        instruction=instruction,
        normalize=normalize
    )

    return EmbeddingResponse(
        status=ResponseStatus.SUCCESS,
        message="文本Embedding生成成功",
        data=[EmbeddingResult(
            index=0,
            embedding=embedding,
            dimension=len(embedding)
        )]
    )


@router.post(
    "/image",
    response_model=EmbeddingResponse,
    summary="生成图片Embedding",
    description="快捷接口：仅处理图片输入"
)
async def generate_image_embedding(
    image_id: str = None,
    image_url: str = None,
    instruction: str = None,
    normalize: bool = True,
    services: tuple = Depends(get_services)
):
    """生成图片的Embedding向量"""
    embedding_svc, storage_svc = services

    # 确定图片路径
    image_path = None
    if image_id:
        path = storage_svc.get_image_path(image_id)
        if path:
            image_path = str(path)
        else:
            raise HTTPException(status_code=404, detail=f"图片不存在: {image_id}")
    elif image_url:
        image_path = image_url
    else:
        raise HTTPException(status_code=400, detail="必须提供image_id或image_url")

    embedding = embedding_svc.generate_image_embedding(
        image=image_path,
        instruction=instruction,
        normalize=normalize
    )

    return EmbeddingResponse(
        status=ResponseStatus.SUCCESS,
        message="图片Embedding生成成功",
        data=[EmbeddingResult(
            index=0,
            embedding=embedding,
            dimension=len(embedding)
        )]
    )


@router.get(
    "/dimension",
    summary="获取向量维度",
    description="返回当前模型的向量维度"
)
async def get_vector_dimension(
    services: tuple = Depends(get_services)
):
    """获取Embedding向量维度"""
    embedding_svc, _ = services

    return {
        "status": "success",
        "dimension": embedding_svc.vector_dimension
    }
