#!/usr/bin/env python3
"""
项目清理脚本
识别并归档过时的测试脚本和文档
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# 定义清理策略
CLEANUP_PLAN = {
    "tests_to_archive": {
        "test_agent_fix.py": "过时的Agent工具调用修复验证",
        "test_simple.py": "临时图片提取测试",
        "try.py": "临时测试文件（包含API Key）",
        "test_debug_recommend.py": "调试测试脚本",
        "test_image_preview.py": "特定功能测试",
        "test_api_response.py": "API响应测试",
        "test_analyze_tool.py": "工具测试",
        "test_agent_image_extraction.py": "特定测试",
        "test_agent_search_tool.py": "工具测试",
        "test_agent_api.py": "API测试",
        "test_image_search_complete.py": "搜索测试",
        "test_image_search_topk.py": "特定功能测试",
        "test_full_recommend_flow.py": "流程测试",
        "test_image_recommendation_tool.py": "工具测试",
        "test_recommend_images_fix.py": "修复测试",
        "test_rebuild_vector_index.py": "重建测试",
        "test_storage_index_api.py": "API测试",
        "test_topk_fix.py": "修复测试",
        "test_vector_fix.py": "修复测试",
        "test_integration.py": "集成测试",
        "test_embedding_api.py": "Embedding API测试",
        "test_agent_image_extraction.py": "图片提取测试",
        "test_agent_recommend.py": "旧版推荐测试",
        "test_tool_improvements.py": "旧版工具改进测试",
        "test_tool_improvements_v2.py": "旧版工具改进测试",
        "test_image_recommendation_simple.py": "旧版推荐测试",
    },
    "docs_to_archive": {
        "AGENT_FIXES_SUMMARY.md": "过时的Agent修复总结",
        "AGENT_SEARCH_TOOL_DEEP_FIX_SUMMARY.md": "过时的搜索工具修复总结",
        "AGENT_SEARCH_TOOL_DEEP_FIX.md": "过时的搜索工具诊断",
        "AGENT_SEARCH_TOOL_FIX_SUMMARY.md": "过时的搜索工具修复总结",
        "AGENT_SEARCH_TOOL_FIX.md": "过时的搜索工具诊断",
        "AGENT_TOOL_FIX_DIAGNOSIS.md": "过时的工具诊断",
        "AGENT_TOOL_FIX_SUMMARY.md": "过时的工具修复总结",
        "ARCHITECTURE_VERIFICATION.md": "架构验证报告",
        "EMBEDDING_MIGRATION.md": "Embedding迁移文档",
        "IMAGE_PREVIEW_FIX_SUMMARY.md": "图片预览修复总结",
        "IMAGE_RECOMMENDATION_TOOL.md": "旧版推荐工具文档",
        "IMAGE_SEARCH_TOPK_FIX_SUMMARY.md": "图片搜索修复总结",
        "IMAGE_SEARCH_TOPK_FIX.md": "图片搜索修复诊断",
        "REBUILD_SOLUTION_SUMMARY.md": "重建解决方案总结",
        "REBUILD_VECTOR_INDEX_GUIDE.md": "向量索引重建指南",
        "STORAGE_INDEX_API_FIX_SUMMARY.md": "存储索引修复总结",
        "STORAGE_INDEX_API_FIX.md": "存储索引修复诊断",
        "VECTOR_DB_FIX_GUIDE.md": "向量数据库修复指南",
        "FINAL_SUMMARY_REPORT.md": "旧版最终总结",
    },
    "files_to_delete": {
        "requirements_rebuild.txt": "过时的依赖文件",
    },
    "files_to_keep": {
        "README.md": "项目主文档",
        "requirements.txt": "项目依赖",
        "check_backend.py": "后端检查工具",
        "rebuild_vector_index.py": "向量索引重建工具",
        "rebuild_vectors.py": "向量重建工具",
        "start_backend.sh": "后端启动脚本",
        "quick_start_rebuild.sh": "快速启动脚本",
        "IMAGE_RECOMMENDATION_FIX_REPORT.md": "最新修复报告",
    },
    "tests_to_keep": {
        "tests/test_agent_service.py": "标准测试目录中的测试",
        "test_recommendation_simple_direct.py": "最新推荐测试",
        "test_tool_improvements_v3.py": "最新工具改进测试",
    }
}


def create_archive_manifest():
    """创建归档清单"""
    manifest = {
        "archive_date": datetime.now().isoformat(),
        "tests_archived": [],
        "docs_archived": [],
        "files_deleted": []
    }
    return manifest


def archive_files():
    """执行归档操作"""
    project_root = Path(".")
    archive_tests_dir = Path("archive/tests")
    archive_docs_dir = Path("archive/docs")
    
    manifest = create_archive_manifest()
    
    print("=" * 80)
    print("开始清理项目")
    print("=" * 80)
    
    # 归档测试文件
    print("\n【归档测试文件】")
    print("-" * 80)
    
    for filename, reason in CLEANUP_PLAN["tests_to_archive"].items():
        src_file = project_root / filename
        if src_file.exists():
            dst_file = archive_tests_dir / filename
            shutil.move(str(src_file), str(dst_file))
            manifest["tests_archived"].append({
                "file": filename,
                "reason": reason
            })
            print(f"✓ {filename:40s} -> archive/tests/")
        else:
            print(f"⊗ {filename:40s} 不存在")
    
    # 归档文档文件
    print("\n【归档文档文件】")
    print("-" * 80)
    
    for filename, reason in CLEANUP_PLAN["docs_to_archive"].items():
        src_file = project_root / filename
        if src_file.exists():
            dst_file = archive_docs_dir / filename
            shutil.move(str(src_file), str(dst_file))
            manifest["docs_archived"].append({
                "file": filename,
                "reason": reason
            })
            print(f"✓ {filename:40s} -> archive/docs/")
        else:
            print(f"⊗ {filename:40s} 不存在")
    
    # 删除无用文件
    print("\n【删除无用文件】")
    print("-" * 80)
    
    for filename, reason in CLEANUP_PLAN["files_to_delete"].items():
        src_file = project_root / filename
        if src_file.exists():
            src_file.unlink()
            manifest["files_deleted"].append({
                "file": filename,
                "reason": reason
            })
            print(f"✓ {filename:40s} 已删除")
        else:
            print(f"⊗ {filename:40s} 不存在")
    
    # 保存清单
    import json
    manifest_file = Path("archive/manifest.json")
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print("\n【清理统计】")
    print("-" * 80)
    print(f"归档测试文件: {len(manifest['tests_archived'])} 个")
    print(f"归档文档文件: {len(manifest['docs_archived'])} 个")
    print(f"删除无用文件: {len(manifest['files_deleted'])} 个")
    print(f"\n归档清单已保存: {manifest_file}")
    
    print("\n【保留的文件】")
    print("-" * 80)
    print("测试文件:")
    for filename in CLEANUP_PLAN["tests_to_keep"]:
        print(f"  ✓ {filename}")
    print("\n工具脚本:")
    for filename in CLEANUP_PLAN["files_to_keep"]:
        if filename.endswith(".py") or filename.endswith(".sh"):
            print(f"  ✓ {filename}")
    print("\n核心文档:")
    for filename in CLEANUP_PLAN["files_to_keep"]:
        if filename.endswith(".md"):
            print(f"  ✓ {filename}")
    
    print("\n" + "=" * 80)
    print("清理完成！")
    print("=" * 80)


if __name__ == "__main__":
    archive_files()
