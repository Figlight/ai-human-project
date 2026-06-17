import asyncio
import base64
import io
import os
import struct
import tempfile
from pathlib import Path
from backend.config import settings


class TTSService:
    def __init__(self):
        self._sapi_available = None

    def _check_sapi(self) -> bool:
        if self._sapi_available is None:
            try:
                import win32com.client
                win32com.client.Dispatch("SAPI.SpVoice")
                self._sapi_available = True
            except Exception:
                self._sapi_available = False
        return self._sapi_available

    async def synthesize(
        self, text: str, voice: str = "zh-CN-XiaoxiaoNeural", speed: float = 1.0
    ) -> bytes:
        # 优先使用高质量的 edge-tts
        result = await self._synthesize_edge_tts(text, voice, speed)
        if result:
            return result

        # 如果 edge-tts 失败且 SAPI5 可用，降级使用 SAPI5
        if self._check_sapi():
            result = await self._synthesize_sapi5(text)
            if result:
                return result

        # 兜底生成静音 WAV
        return self._generate_silent_wav(len(text) * 80)

    def _synthesize_sapi5_sync(self, text: str) -> bytes:
        import pythoncom
        import win32com.client
        pythoncom.CoInitialize()
        out = os.path.join(tempfile.gettempdir(), f"tts_{os.urandom(4).hex()}.wav")
        try:
            voice = win32com.client.Dispatch("SAPI.SpVoice")
            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            stream.Open(out, 3)
            voice.AudioOutputStream = stream
            voice.Speak(text)
            stream.Close()
            with open(out, "rb") as f:
                return f.read()
        except Exception:
            return b""
        finally:
            pythoncom.CoUninitialize()
            try:
                os.remove(out)
            except Exception:
                pass

    async def _synthesize_sapi5(self, text: str) -> bytes:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._synthesize_sapi5_sync, text)

    async def _synthesize_edge_tts(
        self, text: str, voice: str, speed: float
    ) -> bytes:
        try:
            import edge_tts
            rate = f"+{int((speed - 1) * 100)}%" if speed >= 1 else f"{int((speed - 1) * 100)}%"
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            audio_bytes = b""
            async with asyncio.timeout(15):
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_bytes += chunk["data"]
            if audio_bytes:
                return audio_bytes
        except (asyncio.TimeoutError, Exception):
            pass
        return b""

    def _generate_silent_wav(self, duration_ms: int) -> bytes:
        sample_rate = 24000
        num_samples = int(sample_rate * duration_ms / 1000)
        data = b""
        for i in range(num_samples):
            data += struct.pack("<h", 0)

        data_size = len(data)
        buf = io.BytesIO()
        buf.write(b"RIFF")
        buf.write(struct.pack("<I", 36 + data_size))
        buf.write(b"WAVE")
        buf.write(b"fmt ")
        buf.write(struct.pack("<I", 16))
        buf.write(struct.pack("<H", 1))
        buf.write(struct.pack("<H", 1))
        buf.write(struct.pack("<I", sample_rate))
        buf.write(struct.pack("<I", sample_rate * 2))
        buf.write(struct.pack("<H", 2))
        buf.write(struct.pack("<H", 16))
        buf.write(b"data")
        buf.write(struct.pack("<I", data_size))
        buf.write(data)
        return buf.getvalue()

    async def synthesize_base64(
        self, text: str, voice: str = "zh-CN-XiaoxiaoNeural", speed: float = 1.0
    ) -> str:
        audio_bytes = await self.synthesize(text, voice, speed)
        return base64.b64encode(audio_bytes).decode("utf-8")


tts_service = TTSService()
