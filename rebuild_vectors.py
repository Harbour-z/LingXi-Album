"""
向量数据库重建脚本
用于在向量维度变更后重建所有图像的向量索引
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

app_path = Path(__file__).parent / "app"
sys.path.insert(0, str(app_path.parent))

from app.services import (
    get_vector_db_service,
    get_embedding_service,
    get_storage_service
)
from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VectorDBRebuilder:
    """向量数据库重建器"""
    
    def __init__(self):
        self.vector_db_svc = get_vector_db_service()
        self.embedding_svc = get_embedding_service()
        self.storage_svc = get_storage_service()
        self.settings = get_settings()
        
    def initialize(self):
        """初始化所有服务"""
        logger.info("初始化向量数据库服务...")
        self.vector_db_svc.initialize(
            mode=self.settings.QDRANT_MODE,
            path=self.settings.QDRANT_PATH,
            host=self.settings.QDRANT_HOST,
            port=self.settings.QDRANT_PORT,
            api_key=self.settings.QDRANT_API_KEY,
            collection_name=self.settings.QDRANT_COLLECTION_NAME,
            vector_dimension=self.settings.VECTOR_DIMENSION
        )
        
        logger.info("初始化 Embedding 服务...")
        self.embedding_svc.initialize()
        
        logger.info("初始化存储服务...")
        self.storage_svc.initialize()
        
        logger.info("所有服务初始化完成")
    
    def get_all_images(self) -> List[Dict[str, Any]]:
        """获取所有已存储的图像信息"""
        logger.info("获取所有已存储的图像...")
        
        images = []
        storage_path = Path(self.settings.STORAGE_PATH)
        
        if not storage_path.exists():
            logger.warning(f"存储路径不存在: {storage_path}")
            return images
        
        # 遍历存储目录
        for image_file in storage_path.glob("**/*"):
            if image_file.is_file() and image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                # 使用文件名作为 ID
                image_id = image_file.stem
                images.append({
                    "id": image_id,
                    "path": str(image_file),
                    "filename": image_file.name
                })
        
        logger.info(f"找到 {len(images)} 张图像")
        return images
    
    def rebuild_collection(self, force_recreate: bool = False):
        """
        重建向量数据库集合
        
        Args:
            force_recreate: 是否强制重建集合（删除所有现有数据）
        """
        if force_recreate:
            logger.info("强制重建集合，删除所有现有数据...")
            try:
                self.vector_db_svc.delete_collection()
                logger.info("旧集合已删除")
            except Exception as e:
                logger.warning(f"删除集合失败（可能不存在）: {e}")
            
            # 重新创建集合
            self.vector_db_svc._ensure_collection()
            logger.info("新集合已创建")
        else:
            logger.info("使用现有集合")
    
    def rebuild_vectors(self, batch_size: int = 10):
        """
        重建所有图像的向量
        
        Args:
            batch_size: 批量处理大小
        """
        logger.info("开始重建向量数据库...")
        
        # 获取所有图像
        images = self.get_all_images()
        
        if not images:
            logger.warning("没有找到任何图像，重建完成")
            return
        
        total_images = len(images)
        success_count = 0
        failed_count = 0
        failed_images = []
        
        # 批量处理
        for i in range(0, total_images, batch_size):
            batch = images[i:i + batch_size]
            logger.info(f"处理批次 {i // batch_size + 1}/{(total_images + batch_size - 1) // batch_size} "
                       f"({i + 1}-{min(i + batch_size, total_images)}/{total_images})")
            
            batch_records = []
            for image_info in batch:
                try:
                    # 生成向量
                    logger.info(f"  处理图像: {image_info['filename']}")
                    vector = self.embedding_svc.generate_image_embedding(image_info['path'])
                    
                    # 准备元数据
                    metadata = {
                        "filename": image_info['filename'],
                        "file_path": image_info['path'],
                        "created_at": datetime.now().isoformat(),
                        "tags": [],
                        "description": ""
                    }
                    
                    batch_records.append({
                        "id": image_info['id'],
                        "vector": vector,
                        "metadata": metadata
                    })
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"  处理图像失败 {image_info['filename']}: {e}")
                    failed_count += 1
                    failed_images.append({
                        "id": image_info['id'],
                        "filename": image_info['filename'],
                        "error": str(e)
                    })
            
            # 批量插入向量
            if batch_records:
                try:
                    self.vector_db_svc.upsert_batch(batch_records)
                    logger.info(f"  批量插入成功: {len(batch_records)} 条记录")
                except Exception as e:
                    logger.error(f"  批量插入失败: {e}")
                    # 尝试逐条插入
                    for record in batch_records:
                        try:
                            self.vector_db_svc.upsert(
                                id=record['id'],
                                vector=record['vector'],
                                metadata=record['metadata']
                            )
                        except Exception as e2:
                            logger.error(f"    插入记录失败 {record['id']}: {e2}")
                            failed_count += 1
                            success_count -= 1
        
        # 输出统计信息
        logger.info("=" * 60)
        logger.info("向量数据库重建完成")
        logger.info(f"总图像数: {total_images}")
        logger.info(f"成功: {success_count}")
        logger.info(f"失败: {failed_count}")
        
        if failed_images:
            logger.warning(f"失败的图像列表:")
            for img in failed_images:
                logger.warning(f"  - {img['filename']}: {img['error']}")
        
        # 验证重建结果
        self.verify_rebuild()
    
    def verify_rebuild(self):
        """验证重建结果"""
        logger.info("验证重建结果...")
        
        try:
            info = self.vector_db_svc.get_collection_info()
            logger.info(f"集合信息:")
            logger.info(f"  名称: {info['name']}")
            logger.info(f"  向量数量: {info['vectors_count']}")
            logger.info(f"  点数量: {info['points_count']}")
            logger.info(f"  状态: {info['status']}")
            logger.info(f"  向量维度: {info['vector_dimension']}")
            
            # 获取一些样本记录
            records, _ = self.vector_db_svc.scroll(limit=5)
            logger.info(f"样本记录数: {len(records)}")
            
        except Exception as e:
            logger.error(f"验证失败: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="向量数据库重建工具")
    parser.add_argument(
        "--force-recreate",
        action="store_true",
        help="强制重建集合（删除所有现有数据）"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="批量处理大小（默认: 10）"
    )
    
    args = parser.parse_args()
    
    try:
        rebuilder = VectorDBRebuilder()
        rebuilder.initialize()
        
        # 重建集合
        rebuilder.rebuild_collection(force_recreate=args.force_recreate)
        
        # 重建向量
        rebuilder.rebuild_vectors(batch_size=args.batch_size)
        
        logger.info("重建流程完成")
        
    except Exception as e:
        logger.error(f"重建失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()