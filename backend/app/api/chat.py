import base64
import json
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, Form, Depends
from fastapi.responses import StreamingResponse
from backend.app.models.schemas import ChatRequest, ApiResponse
from backend.app.services.chat_service import chat_service
from backend.app.api.auth import get_current_user
from backend.app.db.models import User

router = APIRouter()


@router.post("/text", response_model=ApiResponse)
async def chat_text(req: ChatRequest, current_user: User = Depends(get_current_user)):
    result = await chat_service.process_text_message(
        session_id=req.session_id,
        message=req.message,
        user_id=current_user.id,
        use_rag=req.use_rag,
        preference=req.preference,
    )
    return ApiResponse(data=result)


@router.post("/text/stream")
async def chat_text_stream(req: ChatRequest, current_user: User = Depends(get_current_user)):
    return StreamingResponse(
        chat_service.process_text_stream(
            session_id=req.session_id,
            message=req.message,
            user_id=current_user.id,
            use_rag=req.use_rag,
            preference=req.preference,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/voice", response_model=ApiResponse)
async def chat_voice(
    file: UploadFile = File(...),
    session_id: str = Form("default"),
    preference: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
):
    audio_data = await file.read()
    result = await chat_service.process_voice_message(
        session_id, audio_data, user_id=current_user.id, preference=preference
    )
    return ApiResponse(data=result)


@router.post("/asr", response_model=ApiResponse)
async def transcribe_voice(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    audio_data = await file.read()
    text = await chat_service.transcribe_audio(audio_data)
    return ApiResponse(data={"text": text})



@router.post("/image", response_model=ApiResponse)
async def chat_image(
    image_base64: str = Form(...), 
    session_id: str = Form("default"),
    preference: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    result = await chat_service.process_image_message(
        session_id, image_base64, user_id=current_user.id, preference=preference
    )
    return ApiResponse(data=result)


@router.get("/sessions", response_model=ApiResponse)
async def get_sessions(current_user: User = Depends(get_current_user)):
    sessions = await chat_service.get_user_sessions(user_id=current_user.id)
    return ApiResponse(data=sessions)


@router.delete("/session/{session_id}", response_model=ApiResponse)
@router.delete("/session/", response_model=ApiResponse)
@router.delete("/session", response_model=ApiResponse)
async def delete_session(session_id: str = "", current_user: User = Depends(get_current_user)):
    result = await chat_service.delete_conversation_session(session_id, user_id=current_user.id)
    return ApiResponse(data={"success": result})


@router.get("/history/{session_id}", response_model=ApiResponse)
async def get_history(session_id: str, current_user: User = Depends(get_current_user)):
    history = await chat_service.get_conversation_history(session_id)
    return ApiResponse(data=history)


@router.post("/tts", response_model=ApiResponse)
async def text_to_speech(req: ChatRequest, current_user: User = Depends(get_current_user)):
    from backend.app.services.chat_service import sanitize_text_for_tts
    from backend.app.core.tts import tts_service
    from backend.app.core.digital_human import digital_human_engine
    
    clean_text = sanitize_text_for_tts(req.message)
    if not clean_text:
        return ApiResponse(code=400, message="Text is empty after sanitization")
        
    config = digital_human_engine.config
    audio_base64 = await tts_service.synthesize_base64(
        clean_text,
        voice=config.get("voice", "zh-CN-XiaoxiaoNeural"),
        speed=config.get("speed", 1.0)
    )
    return ApiResponse(data={"audio_base64": audio_base64})


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "text")
            session_id = data.get("session_id", "default")
            preference = data.get("preference", None)

            if msg_type == "text":
                result = await chat_service.process_text_message(
                    session_id, data.get("message", ""), preference=preference
                )
                await websocket.send_json({
                    "type": "reply",
                    "data": result,
                    "state": chat_service.get_current_state(),
                })
            elif msg_type == "audio":
                audio_bytes = base64.b64decode(data.get("audio", ""))
                result = await chat_service.process_voice_message(
                    session_id, audio_bytes, preference=preference
                )
                await websocket.send_json({
                    "type": "reply",
                    "data": result,
                    "state": chat_service.get_current_state(),
                })
            elif msg_type == "state_change":
                chat_service.set_digital_human_state(
                    data.get("state", "idle"),
                    data.get("emotion", "neutral"),
                )
    except WebSocketDisconnect:
        pass
