"""
向量索引重建脚本的单元测试
"""

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

# 添加项目路径
app_path = Path(__file__).parent / "app"
sys.path.insert(0, str(app_path.parent))

from rebuild_vector_index import VectorIndexRebuilder


class TestVectorIndexRebuilder:
    """向量索引重建器测试"""
    
    @pytest.fixture
    def rebuilder(self):
        """创建重建器实例"""
        return VectorIndexRebuilder(
            api_base_url="http://localhost:8000",
            storage_path="./test_storage",
            max_concurrent=2,
            max_retries=2,
            retry_delay=0.1,
            batch_size=2
        )
    
    @pytest.fixture
    def mock_storage(self, tmp_path):
        """创建模拟存储目录"""
        # 创建测试图像文件
        test_images = [
            "test1.jpg",
            "test2.png",
            "test3.webp",
            "not_an_image.txt"  # 应该被忽略
        ]
        
        for img_name in test_images:
            img_path = tmp_path / img_name
            img_path.write_text("fake image content")
        
        return tmp_path
    
    def test_get_all_images(self, rebuilder, mock_storage):
        """测试获取所有图像"""
        rebuilder.storage_path = mock_storage
        
        images = rebuilder.get_all_images()
        
        # 应该找到 3 张图像（忽略 .txt 文件）
        assert len(images) == 3
        
        # 检查图像信息
        assert images[0]["id"] == "test1"
        assert images[0]["filename"] == "test1.jpg"
        assert images[0]["extension"] == ".jpg"
        
        assert images[1]["id"] == "test2"
        assert images[1]["filename"] == "test2.png"
        
        assert images[2]["id"] == "test3"
        assert images[2]["filename"] == "test3.webp"
    
    def test_get_all_images_empty_storage(self, rebuilder, tmp_path):
        """测试空存储目录"""
        rebuilder.storage_path = tmp_path
        
        images = rebuilder.get_all_images()
        
        assert len(images) == 0
    
    def test_get_all_images_nonexistent_storage(self, rebuilder):
        """测试不存在的存储目录"""
        rebuilder.storage_path = Path("/nonexistent/path")
        
        images = rebuilder.get_all_images()
        
        assert len(images) == 0
    
    @pytest.mark.asyncio
    async def test_check_image_indexed_success(self, rebuilder):
        """测试检查图像索引状态 - 成功"""
        with patch.object(rebuilder.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = MagicMock(status_code=200)
            
            result = await rebuilder.check_image_indexed("test_id")
            
            assert result is True
            mock_get.assert_called_once_with(
                "http://localhost:8000/api/v1/vectors/test_id"
            )
    
    @pytest.mark.asyncio
    async def test_check_image_indexed_not_found(self, rebuilder):
        """测试检查图像索引状态 - 未找到"""
        with patch.object(rebuilder.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = MagicMock(status_code=404)
            
            result = await rebuilder.check_image_indexed("test_id")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_check_image_indexed_error(self, rebuilder):
        """测试检查图像索引状态 - 错误"""
        with patch.object(rebuilder.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            result = await rebuilder.check_image_indexed("test_id")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_generate_image_embedding_success(self, rebuilder):
        """测试生成图像 Embedding - 成功"""
        mock_response = {
            "status": "success",
            "message": "图片Embedding生成成功",
            "data": [{
                "index": 0,
                "embedding": [0.1, 0.2, 0.3],
                "dimension": 3
            }]
        }
        
        with patch.object(rebuilder.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: mock_response
            )
            
            result = await rebuilder.generate_image_embedding(
                image_path="/path/to/image.jpg",
                image_id="test_id",
                auto_index=True
            )
            
            assert result is not None
            assert result["status"] == "success"
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_image_embedding_not_found(self, rebuilder):
        """测试生成图像 Embedding - 图像不存在"""
        with patch.object(rebuilder.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(status_code=404)
            
            result = await rebuilder.generate_image_embedding(
                image_path="/path/to/image.jpg",
                image_id="test_id"
            )
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_generate_image_embedding_rate_limit(self, rebuilder):
        """测试生成图像 Embedding - 速率限制"""
        with patch.object(rebuilder.client, 'post', new_callable=AsyncMock) as mock_post:
            # 第一次返回 429，第二次返回 200
            mock_post.side_effect = [
                MagicMock(status_code=429),
                MagicMock(
                    status_code=200,
                    json=lambda: {
                        "status": "success",
                        "data": [{"index": 0, "embedding": [0.1, 0.2], "dimension": 2}]
                    }
                )
            ]
            
            result = await rebuilder.generate_image_embedding(
                image_path="/path/to/image.jpg",
                image_id="test_id"
            )
            
            assert result is not None
            assert result["status"] == "success"
            assert mock_post.call_count == 2
    
    @pytest.mark.asyncio
    async def test_process_image_success(self, rebuilder):
        """测试处理图像 - 成功"""
        image_info = {
            "id": "test_id",
            "path": "/path/to/image.jpg",
            "filename": "image.jpg"
        }
        
        with patch.object(rebuilder, 'check_image_indexed', new_callable=AsyncMock) as mock_check:
            mock_check.return_value = False
            
            with patch.object(rebuilder, 'generate_image_embedding', new_callable=AsyncMock) as mock_gen:
                mock_gen.return_value = {
                    "status": "success",
                    "message": "成功"
                }
                
                result = await rebuilder.process_image(image_info)
                
                assert result is True
                assert rebuilder.stats["success"] == 1
    
    @pytest.mark.asyncio
    async def test_process_image_skip_indexed(self, rebuilder):
        """测试处理图像 - 跳过已索引"""
        image_info = {
            "id": "test_id",
            "path": "/path/to/image.jpg",
            "filename": "image.jpg"
        }
        
        with patch.object(rebuilder, 'check_image_indexed', new_callable=AsyncMock) as mock_check:
            mock_check.return_value = True
            
            result = await rebuilder.process_image(image_info, skip_indexed=True)
            
            assert result is True
            assert rebuilder.stats["skipped"] == 1
    
    @pytest.mark.asyncio
    async def test_process_image_failure(self, rebuilder):
        """测试处理图像 - 失败"""
        image_info = {
            "id": "test_id",
            "path": "/path/to/image.jpg",
            "filename": "image.jpg"
        }
        
        with patch.object(rebuilder, 'check_image_indexed', new_callable=AsyncMock) as mock_check:
            mock_check.return_value = False
            
            with patch.object(rebuilder, 'generate_image_embedding', new_callable=AsyncMock) as mock_gen:
                mock_gen.return_value = None
                
                result = await rebuilder.process_image(image_info)
                
                assert result is False
                assert rebuilder.stats["failed"] == 1
                assert len(rebuilder.failed_images) == 1
    
    @pytest.mark.asyncio
    async def test_process_batch(self, rebuilder):
        """测试批量处理"""
        images = [
            {"id": f"img{i}", "path": f"/path/img{i}.jpg", "filename": f"img{i}.jpg"}
            for i in range(3)
        ]
        
        with patch.object(rebuilder, 'process_image', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = True
            
            await rebuilder.process_batch(images)
            
            assert mock_process.call_count == 3
            assert rebuilder.stats["success"] == 3
    
    @pytest.mark.asyncio
    async def test_rebuild_with_limit(self, rebuilder, mock_storage):
        """测试重建 - 限制数量"""
        rebuilder.storage_path = mock_storage
        
        with patch.object(rebuilder, 'process_batch', new_callable=AsyncMock) as mock_batch:
            await rebuilder.rebuild(limit=2)
            
            # 应该只处理 2 张图像
            assert rebuilder.stats["total"] == 2
            mock_batch.assert_called_once()
    
    def test_print_progress(self, rebuilder, caplog):
        """测试打印进度"""
        rebuilder.stats = {
            "total": 100,
            "success": 50,
            "failed": 10,
            "skipped": 20
        }
        
        with caplog.at_level(logging.INFO):
            rebuilder.print_progress()
        
        assert "进度: 80/100 (80.0%)" in caplog.text
        assert "成功: 50" in caplog.text
        assert "失败: 10" in caplog.text
        assert "跳过: 20" in caplog.text
    
    def test_save_failed_records(self, rebuilder, tmp_path):
        """测试保存失败记录"""
        rebuilder.failed_images = [
            {"id": "img1", "filename": "img1.jpg", "error": "Error 1"},
            {"id": "img2", "filename": "img2.jpg", "error": "Error 2"}
        ]
        
        # 修改当前目录到临时目录
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            rebuilder.save_failed_records()
            
            # 检查文件是否创建
            failed_files = list(tmp_path.glob("failed_images_*.json"))
            assert len(failed_files) == 1
            
            # 检查文件内容
            with open(failed_files[0], 'r') as f:
                saved_data = json.load(f)
            
            assert len(saved_data) == 2
            assert saved_data[0]["id"] == "img1"
            assert saved_data[1]["id"] == "img2"
            
        finally:
            os.chdir(original_cwd)


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_rebuild_workflow(self, tmp_path):
        """测试完整的重建工作流"""
        # 创建测试存储
        (tmp_path / "img1.jpg").write_text("fake image 1")
        (tmp_path / "img2.png").write_text("fake image 2")
        
        rebuilder = VectorIndexRebuilder(
            api_base_url="http://localhost:8000",
            storage_path=str(tmp_path),
            max_concurrent=1,
            batch_size=1
        )
        
        # Mock API 调用
        with patch.object(rebuilder, 'check_image_indexed', new_callable=AsyncMock) as mock_check:
            mock_check.return_value = False
            
            with patch.object(rebuilder, 'generate_image_embedding', new_callable=AsyncMock) as mock_gen:
                mock_gen.return_value = {
                    "status": "success",
                    "message": "成功"
                }
                
                await rebuilder.rebuild()
                
                assert rebuilder.stats["total"] == 2
                assert rebuilder.stats["success"] == 2
                assert rebuilder.stats["failed"] == 0
                
                await rebuilder.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])