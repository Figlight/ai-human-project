from fastapi import APIRouter
from backend.app.api.chat import router as chat_router
from backend.app.api.knowledge import router as knowledge_router
from backend.app.api.digital_human import router as digital_human_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.attractions import router as attractions_router
from backend.app.api.geocode import router as geocode_router

api_router = APIRouter()

api_router.include_router(chat_router, prefix="/chat", tags=["对话"])
api_router.include_router(knowledge_router, prefix="/knowledge", tags=["知识库"])
api_router.include_router(digital_human_router, prefix="/digital-human", tags=["数字人"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["数据分析"])
api_router.include_router(attractions_router, prefix="/attractions", tags=["景点"])
api_router.include_router(geocode_router, prefix="/geocode", tags=["地理编码"])
