from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


# ========== Chat ==========
class ChatRequest(BaseModel):
    session_id: str = "default"
    message: str
    use_rag: bool = True


# ========== Knowledge ==========
class QAItemResponse(BaseModel):
    id: int
    question: str
    answer: str
    category: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
class QAItemCreate(BaseModel):
    question: str
    answer: str
    category: str = "景区概况"


class QAItemUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None



class DocumentResponse(BaseModel):
    id: int
    name: str
    file_size: str
    pages: int
    chunks: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Digital Human ==========
class DigitalHumanConfig(BaseModel):
    name: str = "小导"
    title: str = "智能导游"
    character_id: str = "guide1"
    voice_id: str = "zh-CN-XiaoxiaoNeural"
    outfit_id: str = "outfit1"
    speed: float = 1.0


class CharacterInfo(BaseModel):
    id: str
    name: str
    emoji: str
    bg: str


class VoiceInfo(BaseModel):
    id: str
    name: str
    gender: str
    style: str


class OutfitInfo(BaseModel):
    id: str
    name: str
    color: str


# ========== Analytics ==========
class EmotionTrend(BaseModel):
    date: str
    positive: float
    neutral: float
    negative: float


class KeywordItem(BaseModel):
    text: str
    count: int
    size: int
    color: str
    opacity: float


class SuggestionItem(BaseModel):
    id: int
    type: str
    title: str
    description: str
    urgency: str


class AnalyticsSummary(BaseModel):
    positive_ratio: float
    neutral_ratio: float
    negative_ratio: float
    avg_score: float
    total_conversations: int
    total_visitors: int


# ========== Attractions ==========
class AttractionInfo(BaseModel):
    name: str
    icon: str
    description: str
    color: str
    tags: list[str]


class RouteInfo(BaseModel):
    id: int
    name: str
    duration: str
    color: str
    description: str
    spots: list[str]
    distance: str
    time: str
    tag: str
    tags: list[str] = []


class RouteRecommendRequest(BaseModel):
    tags: list[str] = []


# ========== Feedback ==========
class FeedbackCreate(BaseModel):
    session_id: str
    satisfaction: int = Field(5, ge=1, le=5)
    suggestion: Optional[str] = None


# ========== Common ==========
class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None
