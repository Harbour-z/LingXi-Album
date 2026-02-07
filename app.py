"""
智慧相册 - 魔搭创空间入口文件
LingXi Album - ModelScope Space Entry Point
"""

import uvicorn
from app.main import create_app

if __name__ == "__main__":
    # 创建FastAPI应用实例
    app = create_app()
    
    # 启动服务,监听0.0.0.0:7860
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,
        log_level="info"
    )
