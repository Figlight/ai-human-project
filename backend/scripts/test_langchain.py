"""
测试 LangChain ChatTongyi 集成
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.core.llm import llm_service


async def test_llm_chat():
    """测试非流式对话"""
    print("=" * 60)
    print("测试 1: 非流式对话")
    print("=" * 60)
    
    if not llm_service.llm:
        print("❌ LLM 未初始化，请检查 API Key 配置")
        return
    
    reply, emotion = await llm_service.chat(
        prompt="请介绍一下灵山景区的历史",
        context=None,
        system_prompt=None
    )
    
    print(f"\n回复: {reply}")
    print(f"情感: {emotion}")
    print()


async def test_llm_stream():
    """测试流式对话"""
    print("=" * 60)
    print("测试 2: 流式对话")
    print("=" * 60)
    
    if not llm_service.llm:
        print("❌ LLM 未初始化，请检查 API Key 配置")
        return
    
    print("\n开始流式输出:\n")
    
    full_text = ""
    async for delta, full, emotion in llm_service.chat_stream(
        prompt="灵山景区有哪些主要景点？",
        context=None,
        system_prompt=None
    ):
        if delta:
            print(delta, end="", flush=True)
            full_text += delta
    
    print(f"\n\n完整回复长度: {len(full_text)} 字符")
    print()


async def test_rag_with_llm():
    """测试 RAG + LLM 优化"""
    print("=" * 60)
    print("测试 3: RAG 检索 + LLM 优化")
    print("=" * 60)
    
    from backend.app.services.rag_service import rag_service
    
    query = "古塔是什么时候建造的？"
    print(f"\n查询: {query}\n")
    
    results = await rag_service.retrieve(query, top_k=5)
    
    print(f"检索到 {len(results)} 个相关片段:\n")
    for i, chunk in enumerate(results, 1):
        print(f"[{i}] {chunk[:100]}...")
        print()


async def main():
    """运行所有测试"""
    print("\n🚀 开始测试 LangChain ChatTongyi 集成\n")
    
    # 测试 1: 非流式对话
    await test_llm_chat()
    
    # 测试 2: 流式对话
    await test_llm_stream()
    
    # 测试 3: RAG + LLM
    await test_rag_with_llm()
    
    print("\n✅ 所有测试完成！\n")


if __name__ == "__main__":
    asyncio.run(main())
