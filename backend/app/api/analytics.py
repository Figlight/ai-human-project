from fastapi import APIRouter, Query
from backend.app.models.schemas import ApiResponse, FeedbackCreate
from backend.app.services.analytics_service import analytics_service

router = APIRouter()


@router.get("/summary", response_model=ApiResponse)
async def get_summary():
    data = await analytics_service.get_summary()
    return ApiResponse(data=data)


@router.get("/emotion-trend", response_model=ApiResponse)
async def get_emotion_trend(days: int = Query(7, ge=1, le=90)):
    data = await analytics_service.get_emotion_trend(days)
    return ApiResponse(data=data)


@router.get("/keywords", response_model=ApiResponse)
async def get_keywords():
    data = await analytics_service.get_keywords()
    return ApiResponse(data=data)


@router.get("/suggestions", response_model=ApiResponse)
async def get_suggestions():
    data = await analytics_service.get_suggestions()
    return ApiResponse(data=data)


@router.get("/conversation-samples", response_model=ApiResponse)
async def get_conversation_samples():
    data = await analytics_service.get_conversation_samples()
    return ApiResponse(data=data)


@router.get("/top-questions", response_model=ApiResponse)
async def get_top_questions(limit: int = Query(10, ge=1, le=50)):
    data = await analytics_service.get_top_questions(limit)
    return ApiResponse(data=data)


@router.post("/feedback", response_model=ApiResponse)
async def submit_feedback(req: FeedbackCreate):
    result = await analytics_service.submit_feedback(
        session_id=req.session_id,
        satisfaction=req.satisfaction,
        suggestion=req.suggestion,
    )
    return ApiResponse(data=result)
