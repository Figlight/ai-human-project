import sys
from pathlib import Path

# 将项目根目录添加到 python path 中，确保能导入 backend
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import re
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from backend.config import settings

async def create_db():
    db_url = settings.DATABASE_URL
    
    # 支持 mysql+aiomysql 或者是 sqlite 格式
    if db_url.startswith("sqlite"):
        print("ℹ️ 当前使用的是 SQLite 数据库，无需手动创建库文件，启动后端时会自动生成。")
        return
        
    # 解析 mysql 连接字符串
    # 示例: mysql+aiomysql://root:password@localhost:3306/aihumanproject
    match = re.match(r"(mysql\+aiomysql://[^/]+)/([^?#\s]+)", db_url)
    if not match:
        print("❌ 无法解析 DATABASE_URL 格式，当前创建脚本仅支持 mysql+aiomysql 格式连接。")
        print(f"当前配置的 URL 为: {db_url}")
        return
        
    base_url = match.group(1)
    db_name = match.group(2)
    
    print(f"🔄 正在尝试连接 MySQL 服务器并创建数据库: '{db_name}' ...")
    
    # 建立临时连接引擎（不指定库名）
    engine = create_async_engine(base_url, echo=False)
    
    try:
        async with engine.connect() as conn:
            from sqlalchemy import text
            # 执行建库 SQL
            await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
            await conn.commit()
        print(f"✅ 数据库 '{db_name}' 创建成功（或已存在）！")
    except Exception as e:
        print(f"❌ 运行失败: 连接 MySQL 时遇到错误！")
        print(f"错误详情: {e}")
        print("\n💡 提示:")
        print("1. 请确保您的 MySQL 本地服务已启动（例如 MySQL84）。")
        print("2. 请检查 backend/.env 文件中的数据库账号或密码是否填写正确。")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_db())
