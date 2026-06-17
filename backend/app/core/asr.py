from pathlib import Path
from backend.config import settings


class ASRService:
    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                import whisper
                self._model = whisper.load_model(settings.ASR_MODEL)
            except Exception:
                self._model = None
        return self._model

    async def transcribe(self, audio_path: str | Path) -> str:
        if self.model:
            return await self._transcribe_real(audio_path)
        return self._mock_transcribe(audio_path)

    async def _transcribe_real(self, audio_path: str | Path) -> str:
        import asyncio
        try:
            result = await asyncio.to_thread(
                self.model.transcribe, str(audio_path),
                language="zh", fp16=False,
            )
            return result.get("text", "").strip()
        except Exception:
            return ""

    def _mock_transcribe(self, audio_path: str | Path) -> str:
        return "这座古塔是什么时候建造的？"


asr_service = ASRService()
