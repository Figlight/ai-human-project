from fastapi import APIRouter
from backend.app.models.schemas import ApiResponse, DigitalHumanConfig, CharacterInfo, VoiceInfo, OutfitInfo
from backend.app.core.digital_human import digital_human_engine

router = APIRouter()

CHARACTERS = [
    CharacterInfo(id="guide1", name="古风导游", emoji="👩‍🦰", bg="linear-gradient(135deg, #FFD5C2, #FFB088)"),
    CharacterInfo(id="guide2", name="现代导游", emoji="👩‍💼", bg="linear-gradient(135deg, #E8D5B7, #D4B896)"),
    CharacterInfo(id="guide3", name="卡通导游", emoji="🧝‍♀️", bg="linear-gradient(135deg, #C9F0FF, #A8D8EA)"),
    CharacterInfo(id="guide4", name="书生导游", emoji="👨‍🎓", bg="linear-gradient(135deg, #E8E0F0, #D0C8E0)"),
]

VOICES = [
    VoiceInfo(id="zh-CN-XiaoxiaoNeural", name="温柔女声", gender="female", style="亲切自然，适合讲解"),
    VoiceInfo(id="zh-CN-XiaoyiNeural", name="甜美女声", gender="female", style="活泼可爱，适合互动"),
    VoiceInfo(id="zh-CN-YunxiNeural", name="稳重男声", gender="male", style="沉稳大气，适合介绍"),
    VoiceInfo(id="zh-CN-XiaohanNeural", name="清亮童声", gender="female", style="天真活泼，适合亲子"),
    VoiceInfo(id="zh-CN-YunjianNeural", name="知性女声", gender="female", style="优雅端庄，适合文化讲解"),
]

OUTFITS = [
    OutfitInfo(id="outfit1", name="经典蓝", color="linear-gradient(135deg, #4F6CF7, #8B5CF6)"),
    OutfitInfo(id="outfit2", name="翠竹绿", color="linear-gradient(135deg, #10B981, #34D399)"),
    OutfitInfo(id="outfit3", name="暖阳橙", color="linear-gradient(135deg, #F59E0B, #F97316)"),
    OutfitInfo(id="outfit4", name="牡丹红", color="linear-gradient(135deg, #EC4899, #F43F5E)"),
    OutfitInfo(id="outfit5", name="水墨灰", color="linear-gradient(135deg, #64748B, #94A3B8)"),
    OutfitInfo(id="outfit6", name="高贵紫", color="linear-gradient(135deg, #8B5CF6, #A855F7)"),
]


@router.get("/config", response_model=ApiResponse)
async def get_config():
    data = await digital_human_engine.get_config()
    return ApiResponse(data=data)


@router.put("/config", response_model=ApiResponse)
async def update_config(config: DigitalHumanConfig):
    updated = await digital_human_engine.update_config({
        "name": config.name,
        "title": config.title,
        "character": config.character_id,
        "voice": config.voice_id,
        "outfit": config.outfit_id,
        "speed": config.speed,
    })
    return ApiResponse(data=updated)


@router.get("/characters", response_model=ApiResponse)
async def get_characters():
    return ApiResponse(data=[c.model_dump() for c in CHARACTERS])


@router.get("/voices", response_model=ApiResponse)
async def get_voices():
    return ApiResponse(data=[v.model_dump() for v in VOICES])


@router.get("/outfits", response_model=ApiResponse)
async def get_outfits():
    return ApiResponse(data=[o.model_dump() for o in OUTFITS])


@router.get("/state", response_model=ApiResponse)
async def get_state():
    return ApiResponse(data=digital_human_engine.get_state())


@router.post("/state", response_model=ApiResponse)
async def set_state(state: str = "idle", emotion: str = "neutral"):
    digital_human_engine.set_state(state)
    digital_human_engine.set_emotion(emotion)
    return ApiResponse(data=digital_human_engine.get_state())
