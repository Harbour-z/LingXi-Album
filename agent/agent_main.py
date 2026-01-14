"""
OpenJiuwen Agent 主程序
集成智慧相册后端服务的Agent能力
"""

import os
from typing import List, Dict, Any
from tools import AlbumTools, SearchTools

# 注意：需要安装 openjiuwen 框架
# pip install openjiuwen

# TODO: 根据实际的 OpenJiuwen API 调整导入
# from openjiuwen import Agent, Tool
# from openjiuwen.llm import QwenLLM


class SmartAlbumAgent:
    """
    智慧相册 Agent
    基于 OpenJiuwen 框架，提供自然语言交互的相册管理能力
    """

    def __init__(
        self,
        api_base_url: str = "http://localhost:8000/api/v1",
        llm_model: str = "qwen-plus"  # 或其他华为云模型
    ):
        """
        初始化 Agent

        Args:
            api_base_url: 后端API地址
            llm_model: 使用的LLM模型名称
        """
        self.api_base_url = api_base_url
        self.llm_model = llm_model

        # 初始化工具集
        self.album_tools = AlbumTools(api_base_url)
        self.search_tools = SearchTools(api_base_url)

        # 初始化 OpenJiuwen Agent
        self._setup_agent()

    def _setup_agent(self):
        """配置 OpenJiuwen Agent"""

        # TODO: 根据 OpenJiuwen 实际API调整
        # 这里提供框架示例，需要根据华为文档修改

        # 1. 定义系统提示词
        system_prompt = """
        你是一个智慧相册助手，可以帮助用户管理和搜索照片。
        
        你可以使用以下能力：
        1. 上传图片到相册（upload_image）
        2. 删除图片（delete_image）
        3. 查看图片信息（get_image_info）
        4. 列出所有图片（list_images）
        5. 通过文字描述搜索图片（search_by_text）
        6. 通过图片找相似图片（search_by_image）
        7. 图文混合搜索（search_hybrid）
        
        请根据用户的需求，选择合适的工具完成任务。
        """

        # 2. 定义工具列表（适配 OpenJiuwen 格式）
        tools = self._register_tools()

        # 3. 初始化 Agent（伪代码，需要根据实际API调整）
        # self.agent = Agent(
        #     llm=QwenLLM(model=self.llm_model),
        #     tools=tools,
        #     system_prompt=system_prompt,
        #     max_iterations=10
        # )

        print("Agent 初始化完成")
        print(f"后端API: {self.api_base_url}")
        print(f"LLM模型: {self.llm_model}")
        print(f"可用工具数: {len(tools)}")

    def _register_tools(self) -> List[Dict]:
        """
        注册所有工具到 OpenJiuwen
        返回工具列表（需要转换为 OpenJiuwen 格式）
        """

        tools = [
            # 相册管理工具
            {
                "name": "upload_image",
                "description": "上传图片到相册，支持自动索引和打标签",
                "parameters": {
                    "image_path": {"type": "string", "description": "图片文件路径"},
                    "tags": {"type": "array", "description": "图片标签列表", "optional": True},
                    "description": {"type": "string", "description": "图片描述", "optional": True}
                },
                "function": self.album_tools.upload_image
            },
            {
                "name": "delete_image",
                "description": "删除指定的图片",
                "parameters": {
                    "image_id": {"type": "string", "description": "要删除的图片ID"}
                },
                "function": self.album_tools.delete_image
            },
            {
                "name": "list_images",
                "description": "列出相册中的图片列表，支持标签筛选",
                "parameters": {
                    "limit": {"type": "integer", "description": "返回数量", "default": 20},
                    "tags": {"type": "array", "description": "标签筛选", "optional": True}
                },
                "function": self.album_tools.list_images
            },

            # 搜索工具
            {
                "name": "search_by_text",
                "description": "通过文字描述搜索相似的图片，支持自然语言语义搜索",
                "parameters": {
                    "query": {"type": "string", "description": "搜索文本，如'蓝天白云'、'海边日落'"},
                    "top_k": {"type": "integer", "description": "返回结果数量", "default": 10}
                },
                "function": self.search_tools.search_by_text
            },
            {
                "name": "search_by_image",
                "description": "以图搜图，找到相似的图片",
                "parameters": {
                    "image_id": {"type": "string", "description": "参考图片的ID"}
                },
                "function": self.search_tools.search_by_image_id
            },
            {
                "name": "search_hybrid",
                "description": "图文混合搜索，同时使用文字描述和参考图片搜索",
                "parameters": {
                    "query_text": {"type": "string", "description": "文字描述", "optional": True},
                    "query_image_id": {"type": "string", "description": "参考图片ID", "optional": True}
                },
                "function": self.search_tools.search_hybrid
            }
        ]

        return tools

    def chat(self, user_input: str) -> str:
        """
        与用户对话

        Args:
            user_input: 用户输入

        Returns:
            Agent 响应
        """
        # TODO: 调用 OpenJiuwen 的对话接口
        # response = self.agent.chat(user_input)
        # return response

        # 临时实现（演示用）
        print(f"\n用户: {user_input}")
        print("Agent: [OpenJiuwen 集成中，请根据实际API调整]")

        # 简单的规则匹配演示
        if "搜索" in user_input or "找" in user_input:
            # 提取搜索关键词（实际应该由 LLM 完成）
            results = self.search_tools.search_by_text(user_input, top_k=5)
            return f"找到 {len(results)} 张相关图片"

        elif "上传" in user_input:
            return "请提供图片路径，我将帮您上传"

        return "我可以帮您搜索图片、上传图片或管理相册，请告诉我您需要什么"

    def run_interactive(self):
        """启动交互式对话"""
        print("\n" + "="*60)
        print("智慧相册 Agent (基于 OpenJiuwen)")
        print("="*60)
        print("输入 'exit' 或 'quit' 退出")
        print("输入 'help' 查看帮助")
        print()

        while True:
            try:
                user_input = input("用户: ").strip()

                if user_input.lower() in ["exit", "quit"]:
                    print("再见！")
                    break

                if user_input.lower() == "help":
                    self._show_help()
                    continue

                if not user_input:
                    continue

                response = self.chat(user_input)
                print(f"Agent: {response}\n")

            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                print(f"错误: {e}\n")

    def _show_help(self):
        """显示帮助信息"""
        print("\n可用命令示例：")
        print("  - 帮我找一些海滩的照片")
        print("  - 搜索蓝天白云的图片")
        print("  - 上传 /path/to/image.jpg")
        print("  - 显示所有图片")
        print("  - 找和这张图片相似的照片")
        print()


def main():
    """主程序入口"""

    # 配置参数
    API_BASE_URL = os.getenv("ALBUM_API_URL", "http://localhost:8000/api/v1")
    LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")

    # 创建 Agent
    agent = SmartAlbumAgent(
        api_base_url=API_BASE_URL,
        llm_model=LLM_MODEL
    )

    # 启动交互式对话
    agent.run_interactive()


if __name__ == "__main__":
    main()
