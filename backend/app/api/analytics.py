from fastapi import APIRouter, Query, Depends
from backend.app.models.schemas import ApiResponse, FeedbackCreate
from backend.app.services.analytics_service import analytics_service
from backend.app.api.auth import get_current_admin
from backend.app.db.models import User

router = APIRouter()


@router.get("/summary", response_model=ApiResponse)
async def get_summary(current_admin: User = Depends(get_current_admin)):
    data = await analytics_service.get_summary()
    return ApiResponse(data=data)


@router.get("/emotion-trend", response_model=ApiResponse)
async def get_emotion_trend(days: int = Query(7, ge=1, le=90), current_admin: User = Depends(get_current_admin)):
    data = await analytics_service.get_emotion_trend(days)
    return ApiResponse(data=data)


@router.get("/keywords", response_model=ApiResponse)
async def get_keywords(current_admin: User = Depends(get_current_admin)):
    data = await analytics_service.get_keywords()
    return ApiResponse(data=data)


@router.get("/suggestions", response_model=ApiResponse)
async def get_suggestions(current_admin: User = Depends(get_current_admin)):
    data = await analytics_service.get_suggestions()
    return ApiResponse(data=data)


@router.get("/conversation-samples", response_model=ApiResponse)
async def get_conversation_samples(current_admin: User = Depends(get_current_admin)):
    data = await analytics_service.get_conversation_samples()
    return ApiResponse(data=data)


@router.get("/top-questions", response_model=ApiResponse)
async def get_top_questions(limit: int = Query(10, ge=1, le=50), current_admin: User = Depends(get_current_admin)):
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
