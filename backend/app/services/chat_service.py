import hashlib
import json
import re
import asyncio
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


class ChatService:
    async def process_text_stream(self, session_id: str, message: str, use_rag: bool = True):
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
            nonlocal full_reply, final_emotion
            logger.info("开始调用 LLM...")
            async for delta, full, emotion in llm_service.chat_stream(message, context=context, history=history_list):
                if delta:
                    full_reply += delta
                    await queue.put(("delta", delta))
                if emotion:
                    final_emotion = emotion
                    digital_human_engine.set_emotion(emotion)
            logger.info(f"LLM 回复完成: {full_reply[:50]}...")
            full = full_reply.strip()
            if full:
                logger.info("开始 TTS 语音合成...")
                audio = await tts_service.synthesize_base64(
                    full,
                    voice=digital_human_engine.config["voice"],
                    speed=digital_human_engine.config["speed"],
                )
                logger.info("TTS 合成完成")
                await queue.put(("speech", audio))
            await queue.put(("done", None))
            await self._save_conversation(session_id, "user", message)
            await self._save_conversation(session_id, "assistant", full_reply, final_emotion)

        full_reply = ""
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

        yield f"data: {json.dumps({'type': 'done', 'reply': full_reply, 'emotion': final_emotion}, ensure_ascii=False)}\n\n"

    async def process_text_message(
        self, session_id: str, message: str, use_rag: bool = True
    ) -> dict:
        digital_human_engine.set_state("thinking")

        context = None
        if use_rag:
            retrieved = await rag_service.retrieve(message)
            context = "\n".join(retrieved) if retrieved else None

        # 获取历史对话上下文作为多轮对话背景
        history = await self.get_conversation_history(session_id, limit=10)
        history_list = [{"role": item["role"], "content": item["content"]} for item in history]

        reply, emotion = await llm_service.chat(message, context=context, history=history_list)
        digital_human_engine.set_emotion(emotion)

        audio_base64 = await tts_service.synthesize_base64(
            reply,
            voice=digital_human_engine.config["voice"],
            speed=digital_human_engine.config["speed"],
        )

        digital_human_engine.set_state("speaking")

        await self._save_conversation(session_id, "user", message)
        await self._save_conversation(session_id, "assistant", reply, emotion)

        return {
            "session_id": session_id,
            "reply": reply,
            "emotion": emotion,
            "audio_base64": audio_base64,
        }

    async def _save_conversation(
        self, session_id: str, role: str, content: str, emotion: str = "neutral"
    ):
        async with async_session() as db:
            db.add(Conversation(
                session_id=session_id, role=role,
                content=content, emotion=emotion,
            ))
            await db.commit()

    async def process_voice_message(
        self, session_id: str, audio_data: bytes
    ) -> dict:
        audio_dir = settings.AUDIO_DIR
        audio_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{session_id}_{hashlib.md5(audio_data).hexdigest()[:8]}.wav"
        audio_path = audio_dir / filename
        audio_path.write_bytes(audio_data)

        text = await asr_service.transcribe(str(audio_path))
        digital_human_engine.set_state("listening")
        return await self.process_text_message(session_id, text)

    async def process_image_message(
        self, session_id: str, image_base64: str
    ) -> dict:
        description = await llm_service.analyze_image(image_base64)
        message = f"请介绍这张图片中的内容：{description}"
        return await self.process_text_message(session_id, message)

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


chat_service = ChatService()
