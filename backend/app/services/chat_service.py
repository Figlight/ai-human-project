import hashlib
import json
import re
import asyncio
from typing import Optional
from datetime import datetime
from pathlib import Path
from sqlalchemy import select
from backend.app.core.llm import llm_service
from backend.app.core.asr import asr_service
from backend.app.core.tts import tts_service
from backend.app.core.digital_human import digital_human_engine
from backend.app.services.rag_service import rag_service
from backend.app.db.database import async_session
from backend.app.db.models import Conversation
from backend.config import settings


def sanitize_text_for_tts(text: str) -> str:
    """清理用于 TTS 语音合成的文本，移除 Markdown 标记与情感括号"""
    if not text:
        return ""
    # 1. 移除 Markdown 粗体/斜体/删除线标记 (如 **文本**, *文本*, ~~文本~~)
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'~+', '', text)
    # 2. 移除任何中英文括号的情感表情标记 (如 【情绪:xxx】 或者 [情绪:happy] 各种变体)
    text = re.sub(r'[【\[]情绪[：:]\w+[】\]]', '', text)
    # 3. 移除 Markdown 标题 (如 ### 标题)
    text = re.sub(r'#+\s+', '', text)
    # 4. 移除 Markdown 链接 [链接文本](链接url) -> 只保留链接文本
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # 5. 移除任何 Emoji 符号及变体/连接控制符
    text = re.sub(r'[\u2600-\u27bf]|[\U00010000-\U0010ffff]|[\u200d\ufe0f]', '', text)
    return text.strip()


class ChatService:
    async def process_text_stream(self, session_id: str, message: str, user_id: int = None, use_rag: bool = True, preference: Optional[str] = None):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"收到消息: {message[:50]}...")
        
        digital_human_engine.set_state("thinking")

        context = None
        if use_rag:
            logger.info("开始 RAG 检索...")
            retrieved = await rag_service.retrieve(message)
            context = "\n".join(retrieved) if retrieved else None
            logger.info(f"RAG 检索完成，找到 {len(retrieved) if retrieved else 0} 个相关片段")

        # 获取历史对话上下文作为多轮对话背景
        history = await self.get_conversation_history(session_id, limit=10)
        history_list = [{"role": item["role"], "content": item["content"]} for item in history]

        queue = asyncio.Queue(maxsize=50)

        async def llm_streamer():
            nonlocal full_reply, clean_reply, final_emotion
            logger.info("开始调用 LLM...")
            async for delta, full, emotion in llm_service.chat_stream(message, context=context, history=history_list, preference=preference):
                if delta:
                    # 动态清洗可能夹带的字面 \\n
                    delta = delta.replace("\\n", "\n")
                    full_reply += delta
                    await queue.put(("delta", delta))
                if emotion:
                    final_emotion = emotion
                    digital_human_engine.set_emotion(emotion)
            logger.info(f"LLM 回复完成: {full_reply[:50]}...")
            
            # 清理最终的情感标签文本
            clean_reply = re.sub(r'[【\[]情绪[：:]\w+[】\]]', '', full_reply).strip()
            
            # 为 TTS 语音合成进行过滤净化
            full_for_tts = sanitize_text_for_tts(clean_reply)
            
            if full_for_tts:
                logger.info("开始 TTS 语音合成...")
                audio = await tts_service.synthesize_base64(
                    full_for_tts,
                    voice=digital_human_engine.config["voice"],
                    speed=digital_human_engine.config["speed"],
                )
                logger.info("TTS 合成完成")
                await queue.put(("speech", audio))
            await queue.put(("done", None))
            await self._save_conversation(session_id, "user", message, user_id=user_id)
            await self._save_conversation(session_id, "assistant", clean_reply, final_emotion, user_id=user_id)

        full_reply = ""
        clean_reply = ""
        final_emotion = "neutral"

        producer = asyncio.create_task(llm_streamer())

        while True:
            item = await queue.get()
            if item[0] == "delta":
                yield f"data: {json.dumps({'type': 'delta', 'text': item[1]}, ensure_ascii=False)}\n\n"
            elif item[0] == "speech":
                yield f"data: {json.dumps({'type': 'speech', 'audio_base64': item[1]}, ensure_ascii=False)}\n\n"
            elif item[0] == "done":
                break

        digital_human_engine.set_state("speaking")

        yield f"data: {json.dumps({'type': 'done', 'reply': clean_reply, 'emotion': final_emotion}, ensure_ascii=False)}\n\n"

    async def process_text_message(
        self, session_id: str, message: str, user_id: int = None, use_rag: bool = True, preference: Optional[str] = None
    ) -> dict:
        digital_human_engine.set_state("thinking")

        context = None
        if use_rag:
            retrieved = await rag_service.retrieve(message)
            context = "\n".join(retrieved) if retrieved else None

        # 获取历史对话上下文作为多轮对话背景
        history = await self.get_conversation_history(session_id, limit=10)
        history_list = [{"role": item["role"], "content": item["content"]} for item in history]

        reply, emotion = await llm_service.chat(message, context=context, history=history_list, preference=preference)
        # 动态清洗可能夹带的字面 \\n
        reply = reply.replace("\\n", "\n")
        digital_human_engine.set_emotion(emotion)

        # 净化语音合成文本
        reply_for_tts = sanitize_text_for_tts(reply)

        audio_base64 = await tts_service.synthesize_base64(
            reply_for_tts,
            voice=digital_human_engine.config["voice"],
            speed=digital_human_engine.config["speed"],
        )

        digital_human_engine.set_state("speaking")

        await self._save_conversation(session_id, "user", message, user_id=user_id)
        await self._save_conversation(session_id, "assistant", reply, emotion, user_id=user_id)

        return {
            "session_id": session_id,
            "reply": reply,
            "emotion": emotion,
            "audio_base64": audio_base64,
        }

    async def _save_conversation(
        self, session_id: str, role: str, content: str, emotion: str = "neutral", user_id: int = None
    ):
        async with async_session() as db:
            db.add(Conversation(
                session_id=session_id, role=role,
                content=content, emotion=emotion,
                user_id=user_id
            ))
            await db.commit()

    async def process_voice_message(
        self, session_id: str, audio_data: bytes, user_id: int = None, preference: Optional[str] = None
    ) -> dict:
        audio_dir = settings.AUDIO_DIR
        audio_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{session_id}_{hashlib.md5(audio_data).hexdigest()[:8]}.wav"
        audio_path = audio_dir / filename
        audio_path.write_bytes(audio_data)

        text = await asr_service.transcribe(str(audio_path))
        digital_human_engine.set_state("listening")
        return await self.process_text_message(session_id, text, user_id=user_id, preference=preference)

    async def process_image_message(
        self, session_id: str, image_base64: str, user_id: int = None, preference: Optional[str] = None
    ) -> dict:
        description = await llm_service.analyze_image(image_base64)
        message = f"请介绍这张图片中的内容：{description}"
        return await self.process_text_message(session_id, message, user_id=user_id, preference=preference)

    async def get_conversation_history(
        self, session_id: str, limit: int = 50
    ) -> list[dict]:
        async with async_session() as db:
            stmt = (
                select(Conversation)
                .where(Conversation.session_id == session_id)
                .order_by(Conversation.created_at.asc())
                .limit(limit)
            )
            result = await db.execute(stmt)
            return [
                {
                    "id": item.id,
                    "role": item.role,
                    "content": item.content,
                    "emotion": item.emotion,
                    "time": item.created_at.strftime("%H:%M") if item.created_at else "",
                }
                for item in result.scalars().all()
            ]

    async def get_user_sessions(self, user_id: int) -> list[dict]:
        """获取当前用户的所有历史会话，返回会话列表及其最新提问和更新时间"""
        async with async_session() as db:
            stmt = (
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(Conversation.created_at.asc())
            )
            result = await db.execute(stmt)
            conversations = result.scalars().all()

            sessions = {}
            for item in conversations:
                sid = item.session_id
                if not sid or sid.strip() == "":
                    continue
                if sid not in sessions:
                    sessions[sid] = {
                        "id": sid,
                        "title": item.content if item.role == "user" else "新会话",
                        "time": item.created_at.strftime("%Y-%m-%d %H:%M") if item.created_at else "",
                        "updated_at": item.created_at
                    }
                else:
                    if sessions[sid]["title"] == "新会话" and item.role == "user":
                        sessions[sid]["title"] = item.content
                    if item.created_at:
                        sessions[sid]["time"] = item.created_at.strftime("%Y-%m-%d %H:%M")
                        sessions[sid]["updated_at"] = item.created_at

            sorted_sessions = sorted(
                sessions.values(),
                key=lambda x: x["updated_at"] if x["updated_at"] else datetime.min,
                reverse=True
            )
            for s in sorted_sessions:
                s.pop("updated_at", None)
            return sorted_sessions

    async def delete_conversation_session(self, session_id: str, user_id: int = None) -> bool:
        """删除指定会话及其所有聊天记录"""
        async with async_session() as db:
            from sqlalchemy import delete
            stmt = delete(Conversation).where(Conversation.session_id == session_id)
            if user_id is not None:
                stmt = stmt.where(Conversation.user_id == user_id)
            await db.execute(stmt)
            await db.commit()
            return True

    def get_current_state(self) -> dict:
        return digital_human_engine.get_state()

    def set_digital_human_state(self, state: str, emotion: str):
        digital_human_engine.set_state(state)
        digital_human_engine.set_emotion(emotion)

    async def get_stats(self) -> dict:
        async with async_session() as db:
            from sqlalchemy import func
            total = await db.scalar(select(func.count(Conversation.id)))
            sessions = await db.scalar(
                select(func.count(func.distinct(Conversation.session_id)))
            )
            return {
                "total_conversations": total or 0,
                "total_sessions": sessions or 0,
            }

    async def transcribe_audio(self, audio_data: bytes) -> str:
        import hashlib
        audio_dir = settings.AUDIO_DIR
        audio_dir.mkdir(parents=True, exist_ok=True)
        filename = f"temp_asr_{hashlib.md5(audio_data).hexdigest()[:8]}.wav"
        audio_path = audio_dir / filename
        audio_path.write_bytes(audio_data)

        try:
            text = await asr_service.transcribe(str(audio_path))
        finally:
            if audio_path.exists():
                audio_path.unlink()
        return text



chat_service = ChatService()
