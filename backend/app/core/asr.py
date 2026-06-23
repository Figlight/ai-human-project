import shutil
import logging
from pathlib import Path
from backend.config import settings

logger = logging.getLogger(__name__)


class ASRService:
    def __init__(self):
        self._model = None

    @property
    def model(self):
        # 尝试检测并动态注入 imageio-ffmpeg 库自带的 ffmpeg 并自动复制重命名为本地可识别的 ffmpeg.exe
        import os
        try:
            import imageio_ffmpeg
            target_dir = settings.DATA_DIR
            target_dir.mkdir(parents=True, exist_ok=True)
            target_ffmpeg = target_dir / "ffmpeg.exe"

            if not target_ffmpeg.exists():
                source_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
                shutil.copy(source_ffmpeg, target_ffmpeg)

            # 将目录动态追加进当前进程的 PATH 中
            target_dir_str = str(target_dir.resolve())
            if target_dir_str not in os.environ["PATH"]:
                os.environ["PATH"] = target_dir_str + os.pathsep + os.environ["PATH"]
        except Exception as e:
            logger.debug(f"尝试自动装载 imageio-ffmpeg 异常: {e}")

        if not shutil.which("ffmpeg"):
            logger.warning(
                "⚠️ 警告: 系统中未检测到 'ffmpeg' 二进制文件。语音识别 (ASR) 将回退到 Mock 演示模式！\n"
                "   如需启用真实语音识别，请安装 ffmpeg 并将其添加至系统的 PATH 环境变量中。"
            )
            return None



        if self._model is None:
            try:
                import whisper
                self._model = whisper.load_model(settings.ASR_MODEL)
            except Exception as e:
                logger.error(f"❌ 加载 Whisper ASR 模型失败: {e}")
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
            logger.exception("❌ ASR 语音识别在执行过程中发生异常:")
            return ""

    def _mock_transcribe(self, audio_path: str | Path) -> str:
        import random
        candidates = [
            "这座古塔是什么时候建造的？",
            "景区里有什么特色美食推荐吗？",
            "推荐一条好玩的半日游路线吧？",
            "介绍一下这里的历史文化背景。"
        ]
        return random.choice(candidates)


asr_service = ASRService()

