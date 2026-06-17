"""
快速检查 RAG 向量数据库状态
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.rag_service import rag_service


async def check_database():
    """检查数据库状态"""
    print("=" * 70)
    print("📊 RAG 向量数据库状态检查")
    print("=" * 70)
    
    print(f"\n✅ 知识块数量: {len(rag_service.chunks)}")
    print(f"✅ 向量维度: {rag_service._embeddings.shape if rag_service._embeddings is not None else 'N/A'}")
    print(f"💾 存储位置: {rag_service._save_dir}")
    
    if len(rag_service.chunks) > 0:
        print(f"\n📋 知识块预览（前5个）:\n")
        for i, chunk in enumerate(rag_service.chunks[:5], 1):
            preview = chunk[:200].replace('\n', ' ').replace('\r', ' ')
            print(f"[{i}] {preview}...")
            print()
        
        # 测试检索
        print("=" * 70)
        print("🧪 测试检索功能")
        print("=" * 70)
        
        test_queries = [
            "古塔是什么时候建造的？",
            "景区门票价格",
            "灵山胜境的历史",
            "推荐游览路线",
        ]
        
        for query in test_queries:
            print(f"\n🔎 查询: {query}")
            results = await rag_service.retrieve(query, top_k=2)
            print(f"   ✅ 找到 {len(results)} 个相关片段")
            if results:
                print(f"   📌 最佳匹配: {results[0][:150]}...")
    
    else:
        print("\n⚠️  数据库为空，需要导入文档")
    
    print("\n" + "=" * 70)
    print("✨ 检查完成！")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(check_database())
