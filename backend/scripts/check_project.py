"""
项目完整性检查脚本
检查所有必要的文件、配置和依赖是否就绪
"""
import sys
from pathlib import Path

# 添加项目根目录到路径（backend 的父目录）
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def check_mark(condition, message):
    """打印检查结果"""
    if condition:
        print(f"✅ {message}")
        return True
    else:
        print(f"❌ {message}")
        return False

def main():
    print("=" * 70)
    print("🔍 AI数字人导游项目 - 完整性检查")
    print("=" * 70)
    print()
    
    all_ok = True
    
    # 1. 检查后端核心文件
    print("📁 1. 后端核心文件检查")
    print("-" * 70)
    
    backend_files = [
        ("backend/main.py", "应用入口"),
        ("backend/config.py", "配置文件"),
        ("backend/.env", "环境变量"),
        ("backend/requirements.txt", "依赖列表"),
    ]
    
    for file_path, desc in backend_files:
        full_path = project_root / file_path
        all_ok &= check_mark(full_path.exists(), f"{desc}: {file_path}")
    
    print()
    
    # 2. 检查后端模块
    print("📦 2. 后端模块检查")
    print("-" * 70)
    
    core_modules = [
        ("backend/app/core/llm.py", "LLM服务"),
        ("backend/app/core/asr.py", "ASR服务"),
        ("backend/app/core/tts.py", "TTS服务"),
        ("backend/app/core/digital_human.py", "数字人引擎"),
        ("backend/app/services/chat_service.py", "聊天服务"),
        ("backend/app/services/rag_service.py", "RAG服务"),
        ("backend/app/api/router.py", "API路由"),
    ]
    
    for file_path, desc in core_modules:
        full_path = project_root / file_path
        all_ok &= check_mark(full_path.exists(), f"{desc}: {file_path}")
    
    print()
    
    # 3. 检查前端文件
    print("🎨 3. 前端文件检查")
    print("-" * 70)
    
    frontend_files = [
        ("package.json", "前端依赖"),
        ("vite.config.js", "Vite配置"),
        ("index.html", "入口HTML"),
        ("src/main.js", "前端入口"),
        ("src/App.vue", "主组件"),
        ("src/api.js", "API接口"),
    ]
    
    for file_path, desc in frontend_files:
        full_path = project_root / file_path
        all_ok &= check_mark(full_path.exists(), f"{desc}: {file_path}")
    
    print()
    
    # 4. 检查数据文件
    print("💾 4. 数据文件检查")
    print("-" * 70)
    
    # RAG 索引
    rag_chunks = project_root / "backend/data/rag_index/chunks.json"
    rag_embs = project_root / "backend/data/rag_index/embeddings.npy"
    all_ok &= check_mark(rag_chunks.exists(), f"RAG文本索引: {rag_chunks.name}")
    all_ok &= check_mark(rag_embs.exists(), f"RAG向量索引: {rag_embs.name}")
    
    if rag_chunks.exists():
        import json
        chunks = json.loads(rag_chunks.read_text(encoding='utf-8'))
        print(f"   📊 知识块数量: {len(chunks)}")
    
    # 知识库文件
    knowledge_dir = project_root / "backend/data/knowledge"
    if knowledge_dir.exists():
        files = list(knowledge_dir.glob("*"))
        print(f"   📚 知识库文件: {len(files)} 个")
        all_ok &= check_mark(len(files) > 0, "知识库文件存在")
    
    print()
    
    # 5. 检查依赖
    print("📦 5. Python依赖检查")
    print("-" * 70)
    
    required_packages = [
        ("fastapi", "FastAPI框架"),
        ("uvicorn", "ASGI服务器"),
        ("langchain", "LangChain框架"),
        ("langchain_community", "LangChain社区包"),
        ("sentence_transformers", "句子转换器"),
        ("whisper", "Whisper语音识别"),
        ("edge_tts", "Edge TTS"),
    ]
    
    for package, desc in required_packages:
        try:
            __import__(package)
            all_ok &= check_mark(True, f"{desc}: {package}")
        except ImportError:
            all_ok &= check_mark(False, f"{desc}: {package} (未安装)")
    
    print()
    
    # 6. 检查配置
    print("⚙️  6. 配置检查")
    print("-" * 70)
    
    try:
        from backend.config import settings
        
        all_ok &= check_mark(settings.LLM_API_KEY != "", "LLM API Key 已配置")
        all_ok &= check_mark(settings.DATABASE_URL != "", "数据库URL已配置")
        all_ok &= check_mark(settings.AMAP_KEY != "", "高德地图Key已配置")
        
        print(f"   🔧 LLM模型: {settings.LLM_MODEL}")
        print(f"   🔧 ASR模型: {settings.ASR_MODEL}")
        print(f"   🔧 TTS语音: {settings.TTS_VOICE}")
        
    except Exception as e:
        all_ok &= check_mark(False, f"配置加载失败: {e}")
    
    print()
    
    # 7. 检查端口占用
    print("🌐 7. 服务状态检查")
    print("-" * 70)
    
    import socket
    
    def check_port(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    
    backend_running = check_port(8000)
    frontend_running = check_port(3000) or check_port(3001)
    
    all_ok &= check_mark(backend_running, "后端服务 (端口 8000)")
    all_ok &= check_mark(frontend_running, "前端服务 (端口 3000/3001)")
    
    print()
    
    # 总结
    print("=" * 70)
    if all_ok:
        print("✨ 项目检查完成 - 一切正常！")
    else:
        print("⚠️  项目检查完成 - 发现一些问题，请查看上方详情")
    print("=" * 70)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
