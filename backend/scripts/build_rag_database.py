"""
批量导入知识库文件到 RAG 向量数据库

此脚本会将 backend/data/knowledge 目录中的所有文档导入到向量数据库中，
用于后续的 RAG 检索增强生成。
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径（backend 的父目录）
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.rag_service import rag_service
from backend.config import settings


async def build_vector_database():
    """构建向量数据库"""
    print("=" * 70)
    print("🚀 开始构建 RAG 向量数据库")
    print("=" * 70)
    
    knowledge_dir = settings.KNOWLEDGE_DIR
    print(f"\n📁 知识库目录: {knowledge_dir}")
    print(f"📊 当前知识块数量: {len(rag_service.chunks)}")
    
    if not knowledge_dir.exists():
        print(f"❌ 知识库目录不存在: {knowledge_dir}")
        return
    
    # 获取所有支持的文件
    supported_extensions = {'.pdf', '.docx', '.xlsx', '.txt', '.md'}
    files = [
        f for f in knowledge_dir.iterdir() 
        if f.is_file() and f.suffix.lower() in supported_extensions
    ]
    
    if not files:
        print("⚠️  未找到支持的文档文件")
        print(f"   支持的格式: {', '.join(supported_extensions)}")
        return
    
    print(f"\n📄 找到 {len(files)} 个文档文件:\n")
    for i, file in enumerate(files, 1):
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  [{i}] {file.name} ({size_mb:.2f} MB)")
    
    print("\n" + "=" * 70)
    print("开始导入文档...")
    print("=" * 70 + "\n")
    
    total_chunks = 0
    success_count = 0
    failed_files = []
    
    for file in files:
        try:
            print(f"📥 正在处理: {file.name}...", end=" ")
            result = await rag_service.add_document(file)
            
            if result["chunks"] > 0:
                total_chunks += result["chunks"]
                success_count += 1
                print(f"✅ 成功导入 {result['chunks']} 个知识块")
            else:
                print("⚠️  未提取到内容")
                
        except Exception as e:
            print(f"❌ 失败: {e}")
            failed_files.append((file.name, str(e)))
    
    # 打印总结
    print("\n" + "=" * 70)
    print("📊 导入完成总结")
    print("=" * 70)
    print(f"✅ 成功导入: {success_count}/{len(files)} 个文件")
    print(f"📝 总知识块数: {total_chunks}")
    print(f"💾 向量存储位置: {rag_service._save_dir}")
    
    if failed_files:
        print(f"\n❌ 失败的文件:")
        for filename, error in failed_files:
            print(f"   - {filename}: {error}")
    
    # 验证导入结果
    print("\n" + "=" * 70)
    print("🔍 验证导入结果")
    print("=" * 70)
    
    if len(rag_service.chunks) > 0:
        print(f"✅ 向量数据库中有 {len(rag_service.chunks)} 个知识块")
        
        # 显示前几个知识块的预览
        print(f"\n📋 知识块预览（前3个）:\n")
        for i, chunk in enumerate(rag_service.chunks[:3], 1):
            preview = chunk[:150].replace('\n', ' ')
            print(f"[{i}] {preview}...")
            print()
        
        # 测试检索功能
        print("=" * 70)
        print("🧪 测试检索功能")
        print("=" * 70)
        
        test_queries = [
            "古塔是什么时候建造的？",
            "景区门票多少钱？",
            "推荐游览路线",
        ]
        
        for query in test_queries:
            print(f"\n🔎 查询: {query}")
            results = await rag_service.retrieve(query, top_k=2)
            print(f"   找到 {len(results)} 个相关片段")
            if results:
                print(f"   最佳匹配: {results[0][:100]}...")
    
    else:
        print("⚠️  向量数据库为空，请检查文档内容")
    
    print("\n" + "=" * 70)
    print("✨ 向量数据库构建完成！")
    print("=" * 70)


async def rebuild_database():
    """重建向量数据库（清空后重新导入）"""
    print("\n⚠️  警告: 这将清空现有的向量数据库！")
    response = input("是否继续？(yes/no): ").strip().lower()
    
    if response != 'yes':
        print("已取消操作")
        return
    
    print("\n🔄 正在重建向量数据库...\n")
    await rag_service.rebuild_index()
    await build_vector_database()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='构建 RAG 向量数据库')
    parser.add_argument('--rebuild', action='store_true', help='重建数据库（清空后重新导入）')
    
    args = parser.parse_args()
    
    if args.rebuild:
        asyncio.run(rebuild_database())
    else:
        asyncio.run(build_vector_database())
