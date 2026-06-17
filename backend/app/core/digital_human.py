from sqlalchemy import select
from backend.app.db.database import async_session
from backend.app.db.models import Conversation, DHConfig


class DigitalHumanEngine:
    STATE_IDLE = "idle"
    STATE_LISTENING = "listening"
    STATE_THINKING = "thinking"
    STATE_SPEAKING = "speaking"

    def __init__(self):
        self.state = self.STATE_IDLE
        self.emotion = "neutral"
        self._ws_connections = set()
        self._cached_config = None

    async def _ensure_config(self):
        async with async_session() as db:
            result = await db.execute(select(DHConfig).limit(1))
            cfg = result.scalar_one_or_none()
            if not cfg:
                cfg = DHConfig()
                db.add(cfg)
                await db.commit()
                await db.refresh(cfg)
            self._cached_config = cfg

    async def _get_config_row(self):
        if self._cached_config is None:
            await self._ensure_config()
        return self._cached_config

    @property
    def config(self) -> dict:
        if self._cached_config:
            return {
                "name": self._cached_config.name,
                "title": self._cached_config.title,
                "character": self._cached_config.character,
                "voice": self._cached_config.voice,
                "outfit": self._cached_config.outfit,
                "speed": self._cached_config.speed,
            }
        return {
            "name": "小导",
            "title": "智能导游",
            "character": "guide1",
            "voice": "zh-CN-XiaoxiaoNeural",
            "outfit": "outfit1",
            "speed": 1.0,
        }

    def register_ws(self, ws):
        self._ws_connections.add(ws)

    def unregister_ws(self, ws):
        self._ws_connections.discard(ws)

    def set_state(self, state: str):
        self.state = state

    def set_emotion(self, emotion: str):
        self.emotion = emotion

    async def update_config(self, config: dict) -> dict:
        async with async_session() as db:
            result = await db.execute(select(DHConfig).limit(1))
            row = result.scalar_one()
            for k, v in config.items():
                setattr(row, k, v)
            await db.commit()
            self._cached_config = row
        return self.config

    async def get_config(self) -> dict:
        await self._get_config_row()
        return self.config

    def get_state(self) -> dict:
        return {"state": self.state, "emotion": self.emotion}

    async def generate_lip_sync(self, audio_duration_ms: int) -> list[dict]:
        import random
        num_frames = min(audio_duration_ms // 40, 100)
        visemes = ["B", "C", "D", "E", "F", "G", "H", "X"]
        return [
            {"time": i * 40, "viseme": random.choice(visemes), "intensity": random.uniform(0.3, 1.0)}
            for i in range(num_frames)
        ]

    def get_emotion_facial_params(self, emotion: str) -> dict:
        params = {
            "happy": {"browUp": 0.6, "mouthSmile": 0.8, "eyeOpen": 0.7},
            "sad": {"browDown": 0.5, "mouthFrown": 0.6, "eyeOpen": 0.4},
            "surprised": {"browUp": 0.9, "mouthOpen": 0.7, "eyeOpen": 0.9},
            "neutral": {"browUp": 0.3, "mouthSmile": 0.3, "eyeOpen": 0.5},
            "excited": {"browUp": 0.8, "mouthSmile": 0.9, "eyeOpen": 0.8},
        }
        return params.get(emotion, params["neutral"])

    async def get_stats(self) -> dict:
        async with async_session() as db:
            from sqlalchemy import func
            total = await db.scalar(select(func.count(Conversation.id))) or 0
            sessions = await db.scalar(
                select(func.count(func.distinct(Conversation.session_id)))
            ) or 0
            return {"total_conversations": total, "total_sessions": sessions}


digital_human_engine = DigitalHumanEngine()