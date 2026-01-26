"""
测试图片编辑功能集成
验证完整的功能链路：Agent识别 -> 调用工具 -> 保存图片 -> 记录元数据
"""

import asyncio
import logging
from app.services import (
    get_storage_service,
    get_image_edit_service,
    get_agent_service
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_image_edit_service():
    """测试图片编辑服务"""
    logger.info("="*60)
    logger.info("测试图片编辑服务")
    logger.info("="*60)
    
    # 初始化服务
    storage_svc = get_storage_service()
    edit_svc = get_image_edit_service()
    agent_svc = get_agent_service()
    
    # 检查服务状态
    logger.info(f"存储服务初始化: {storage_svc.is_initialized}")
    logger.info(f"编辑服务初始化: {edit_svc.is_initialized}")
    logger.info(f"Agent服务初始化: {agent_svc.is_initialized}")
    
    # 获取存储统计
    stats = storage_svc.get_storage_stats()
    logger.info(f"当前图片总数: {stats['total_images']}")
    
    # 列出前5张图片
    images, total = storage_svc.list_images(page=1, page_size=5)
    logger.info(f"获取到 {len(images)} 张图片:")
    for img in images:
        logger.info(f"  - ID: {img['id']}, 文件名: {img['filename']}")
    
    if not images:
        logger.warning("没有图片可供测试，请先上传一些图片")
        return
    
    # 选择第一张图片进行测试
    test_image = images[0]
    image_id = test_image['id']
    
    logger.info(f"\n选择测试图片: {image_id}")
    logger.info(f"图片路径: {test_image['file_path']}")
    
    # 读取图片数据
    image_path = storage_svc.get_image_path(image_id)
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    logger.info(f"图片大小: {len(image_data)} bytes")
    
    # 测试编辑功能（使用卡通风格，速度较快）
    logger.info("\n开始测试图片编辑...")
    logger.info("提示词: '将图片转换为卡通风格'")
    
    result = await edit_svc.edit_image_and_save(
        image_data=image_data,
        prompt="将图片转换为卡通风格",
        source_image_id=image_id,
        style_tag="cartoon",
        n=1
    )
    
    if result.get("success"):
        logger.info(f"✓ 图片编辑成功!")
        logger.info(f"  生成: {result.get('total_generated', 0)} 张")
        logger.info(f"  保存: {result.get('total_saved', 0)} 张")
        
        saved_images = result.get("saved_images", [])
        for saved_img in saved_images:
            logger.info(f"\n新图片信息:")
            logger.info(f"  ID: {saved_img['image_id']}")
            logger.info(f"  URL: {saved_img['url']}")
            logger.info(f"  元数据: {saved_img.get('metadata', {})}")
        
        # 更新后的统计
        new_stats = storage_svc.get_storage_stats()
        logger.info(f"\n更新后图片总数: {new_stats['total_images']}")
        
        # 验证图片是否可以访问
        if saved_images:
            test_img_id = saved_images[0]['image_id']
            test_img_info = storage_svc.get_image_info(test_img_id)
            if test_img_info:
                logger.info(f"✓ 新图片验证成功")
                logger.info(f"  文件名: {test_img_info['filename']}")
                logger.info(f"  大小: {test_img_info['file_size']} bytes")
                logger.info(f"  格式: {test_img_info['format']}")
            else:
                logger.error(f"✗ 无法找到新图片: {test_img_id}")
    else:
        logger.error(f"✗ 图片编辑失败: {result.get('error')}")
    
    logger.info("\n" + "="*60)
    logger.info("测试完成")
    logger.info("="*60)


async def test_agent_integration():
    """测试Agent集成"""
    logger.info("\n" + "="*60)
    logger.info("测试Agent集成")
    logger.info("="*60)
    
    agent_svc = get_agent_service()
    
    if not agent_svc.is_initialized or not agent_svc._agent:
        logger.warning("Agent未初始化，跳过测试")
        return
    
    # 模拟用户查询
    test_queries = [
        "把这张图转成动漫风格",
        "帮我把图片改成卡通风格",
        "我想把照片改成水彩画风格"
    ]
    
    logger.info(f"Agent工具数量: {len(agent_svc._tools)}")
    
    # 检查是否有edit_image工具
    tool_names = [tool.name for tool in agent_svc._tools]
    logger.info(f"可用工具: {tool_names}")
    
    if "edit_image" in tool_names:
        logger.info("✓ edit_image工具已注册")
    else:
        logger.error("✗ edit_image工具未注册")
        return
    
    logger.info("\n建议的测试查询:")
    for i, query in enumerate(test_queries, 1):
        logger.info(f"  {i}. {query}")
    
    logger.info("\n注意: 实际的Agent测试需要先有图片，然后在对话中输入上述查询")
    logger.info("可以通过 http://localhost:8000/docs 查看完整的API文档")


async def main():
    """主测试函数"""
    await test_image_edit_service()
    await test_agent_integration()


if __name__ == "__main__":
    asyncio.run(main())
