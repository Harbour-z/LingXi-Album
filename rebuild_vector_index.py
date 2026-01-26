"""
向量索引重建脚本
通过调用后端 API 重新构建 storage 中所有图像的向量索引
"""

import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

import httpx
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VectorIndexRebuilder:
    """向量索引重建器"""
    
    def __init__(
        self,
        api_base_url: str = "http://localhost:8000",
        storage_path: str = "./storage",
        max_concurrent: int = 5,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        batch_size: int = 10
    ):
        """
        初始化重建器
        
        Args:
            api_base_url: 后端 API 基础 URL
            storage_path: 存储路径
            max_concurrent: 最大并发数
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            batch_size: 批量处理大小
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.storage_path = Path(storage_path)
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.batch_size = batch_size
        
        self.client = httpx.AsyncClient(timeout=30.0)
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0
        }
        self.failed_images: List[Dict[str, Any]] = []
        
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()
    
    def get_all_images(self) -> List[Dict[str, Any]]:
        """
        获取 storage 中所有图像
        
        Returns:
            图像信息列表
        """
        logger.info(f"扫描存储路径: {self.storage_path}")
        
        images = []
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        
        if not self.storage_path.exists():
            logger.error(f"存储路径不存在: {self.storage_path}")
            return images
        
        # 递归遍历所有图像文件
        for image_file in self.storage_path.rglob("*"):
            if image_file.is_file() and image_file.suffix.lower() in allowed_extensions:
                # 使用文件名（不含扩展名）作为 ID
                image_id = image_file.stem
                
                # 获取相对路径
                relative_path = image_file.relative_to(self.storage_path)
                
                images.append({
                    "id": image_id,
                    "path": str(image_file),
                    "relative_path": str(relative_path),
                    "filename": image_file.name,
                    "size": image_file.stat().st_size,
                    "extension": image_file.suffix.lower()
                })
        
        logger.info(f"找到 {len(images)} 张图像")
        return images
    
    async def check_image_indexed(self, image_id: str) -> bool:
        """
        检查图像是否已索引
        
        Args:
            image_id: 图像 ID
            
        Returns:
            是否已索引
        """
        try:
            response = await self.client.get(
                f"{self.api_base_url}/api/v1/vectors/{image_id}"
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"检查索引状态失败 {image_id}: {e}")
            return False
    
    async def generate_image_embedding(
        self,
        image_path: str,
        image_id: str,
        auto_index: bool = True,
        tags: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        调用 API 生成图像 Embedding
        
        Args:
            image_path: 图像路径
            image_id: 图像 ID
            auto_index: 是否自动索引
            tags: 标签
            
        Returns:
            API 响应数据
        """
        url = f"{self.api_base_url}/api/v1/embedding/image"
        
        # 准备请求参数
        params = {
            "image_id": image_id,
            "normalize": True,
            "auto_index": auto_index
        }
        
        if tags:
            params["tags"] = tags
        
        # 使用指数退避重试
        for attempt in range(self.max_retries):
            try:
                response = await self.client.post(
                    url,
                    params=params,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    logger.warning(f"图像不存在: {image_id}")
                    return None
                elif response.status_code == 429:
                    # 速率限制，等待后重试
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"速率限制，等待 {wait_time:.1f} 秒后重试...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"API 调用失败: {response.status_code} - {response.text}")
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)
                        await asyncio.sleep(wait_time)
                    else:
                        return None
                        
            except httpx.TimeoutException:
                logger.error(f"请求超时: {image_id}")
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    await asyncio.sleep(wait_time)
                else:
                    return None
                    
            except Exception as e:
                logger.error(f"请求异常: {e}")
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    await asyncio.sleep(wait_time)
                else:
                    return None
        
        return None
    
    async def process_image(
        self,
        image_info: Dict[str, Any],
        skip_indexed: bool = True,
        force_reindex: bool = False
    ) -> bool:
        """
        处理单个图像
        
        Args:
            image_info: 图像信息
            skip_indexed: 是否跳过已索引的图像
            force_reindex: 是否强制重新索引
            
        Returns:
            是否成功
        """
        image_id = image_info["id"]
        image_path = image_info["path"]
        
        # 检查是否已索引
        if skip_indexed and not force_reindex:
            is_indexed = await self.check_image_indexed(image_id)
            if is_indexed:
                logger.debug(f"跳过已索引的图像: {image_id}")
                self.stats["skipped"] += 1
                return True
        
        # 生成 Embedding 并索引
        logger.info(f"处理图像: {image_info['filename']} ({image_id})")
        
        result = await self.generate_image_embedding(
            image_path=image_path,
            image_id=image_id,
            auto_index=True
        )
        
        if result and result.get("status") == "success":
            logger.info(f"✓ 成功: {image_id}")
            self.stats["success"] += 1
            return True
        else:
            logger.error(f"✗ 失败: {image_id}")
            self.stats["failed"] += 1
            self.failed_images.append({
                "id": image_id,
                "filename": image_info['filename'],
                "path": image_path,
                "error": result.get("message", "Unknown error") if result else "No response"
            })
            return False
    
    async def process_batch(
        self,
        images: List[Dict[str, Any]],
        skip_indexed: bool = True,
        force_reindex: bool = False
    ):
        """
        批量处理图像
        
        Args:
            images: 图像列表
            skip_indexed: 是否跳过已索引的图像
            force_reindex: 是否强制重新索引
        """
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_with_semaphore(image_info):
            async with semaphore:
                return await self.process_image(
                    image_info,
                    skip_indexed=skip_index,
                    force_reindex=force_reindex
                )
        
        tasks = [process_with_semaphore(img) for img in images]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def rebuild(
        self,
        skip_indexed: bool = True,
        force_reindex: bool = False,
        limit: Optional[int] = None
    ):
        """
        重建向量索引
        
        Args:
            skip_indexed: 是否跳过已索引的图像
            force_reindex: 是否强制重新索引
            limit: 限制处理的图像数量（用于测试）
        """
        logger.info("=" * 60)
        logger.info("开始重建向量索引")
        logger.info("=" * 60)
        
        # 获取所有图像
        images = self.get_all_images()
        
        if not images:
            logger.warning("没有找到任何图像")
            return
        
        # 应用限制
        if limit:
            images = images[:limit]
            logger.info(f"限制处理数量: {limit}")
        
        self.stats["total"] = len(images)
        
        # 批量处理
        start_time = time.time()
        
        for i in range(0, len(images), self.batch_size):
            batch = images[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (len(images) + self.batch_size - 1) // self.batch_size
            
            logger.info(f"处理批次 {batch_num}/{total_batches} "
                       f"({i + 1}-{min(i + self.batch_size, len(images))}/{len(images)})")
            
            await self.process_batch(
                batch,
                skip_indexed=skip_indexed,
                force_reindex=force_reindex
            )
            
            # 显示进度
            self.print_progress()
        
        elapsed_time = time.time() - start_time
        
        # 输出最终统计
        self.print_final_stats(elapsed_time)
        
        # 保存失败记录
        if self.failed_images:
            self.save_failed_records()
    
    def print_progress(self):
        """打印当前进度"""
        total = self.stats["total"]
        processed = self.stats["success"] + self.stats["failed"] + self.stats["skipped"]
        progress = (processed / total * 100) if total > 0 else 0
        
        logger.info(f"进度: {processed}/{total} ({progress:.1f}%) | "
                   f"成功: {self.stats['success']} | "
                   f"失败: {self.stats['failed']} | "
                   f"跳过: {self.stats['skipped']}")
    
    def print_final_stats(self, elapsed_time: float):
        """打印最终统计信息"""
        logger.info("=" * 60)
        logger.info("重建完成")
        logger.info("=" * 60)
        logger.info(f"总图像数: {self.stats['total']}")
        logger.info(f"成功: {self.stats['success']}")
        logger.info(f"失败: {self.stats['failed']}")
        logger.info(f"跳过: {self.stats['skipped']}")
        logger.info(f"耗时: {elapsed_time:.2f} 秒")
        
        if self.stats['total'] > 0:
            avg_time = elapsed_time / self.stats['total']
            logger.info(f"平均每张: {avg_time:.2f} 秒")
        
        if self.failed_images:
            logger.warning(f"失败的图像: {len(self.failed_images)}")
    
    def save_failed_records(self):
        """保存失败记录到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"failed_images_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.failed_images, f, indent=2, ensure_ascii=False)
        
        logger.info(f"失败记录已保存到: {filename}")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="向量索引重建工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 重建所有图像（跳过已索引的）
  python rebuild_vector_index.py
  
  # 强制重新索引所有图像
  python rebuild_vector_index.py --force-reindex
  
  # 限制处理数量（用于测试）
  python rebuild_vector_index.py --limit 10
  
  # 自定义并发数和批量大小
  python rebuild_vector_index.py --max-concurrent 10 --batch-size 20
  
  # 指定自定义存储路径和 API URL
  python rebuild_vector_index.py --storage-path ./my_storage --api-url http://localhost:8080
        """
    )
    
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="后端 API 基础 URL (默认: http://localhost:8000)"
    )
    
    parser.add_argument(
        "--storage-path",
        default="./storage",
        help="存储路径 (默认: ./storage)"
    )
    
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="最大并发数 (默认: 5)"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="批量处理大小 (默认: 10)"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="最大重试次数 (默认: 3)"
    )
    
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=1.0,
        help="重试延迟（秒）(默认: 1.0)"
    )
    
    parser.add_argument(
        "--force-reindex",
        action="store_true",
        help="强制重新索引所有图像（包括已索引的）"
    )
    
    parser.add_argument(
        "--no-skip-indexed",
        action="store_true",
        help="不跳过已索引的图像"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        help="限制处理的图像数量（用于测试）"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 创建重建器
        rebuilder = VectorIndexRebuilder(
            api_base_url=args.api_url,
            storage_path=args.storage_path,
            max_concurrent=args.max_concurrent,
            max_retries=args.max_retries,
            retry_delay=args.retry_delay,
            batch_size=args.batch_size
        )
        
        # 执行重建
        await rebuilder.rebuild(
            skip_indexed=not args.no_skip_indexed,
            force_reindex=args.force_reindex,
            limit=args.limit
        )
        
        # 关闭客户端
        await rebuilder.close()
        
        # 检查是否有失败
        if rebuilder.stats["failed"] > 0:
            logger.warning(f"有 {rebuilder.stats['failed']} 张图像处理失败")
            sys.exit(1)
        else:
            logger.info("所有图像处理成功")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("用户中断")
        sys.exit(130)
    except Exception as e:
        logger.error(f"重建失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())