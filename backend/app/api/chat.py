import base64
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from backend.app.models.schemas import ChatRequest, ApiResponse
from backend.app.services.chat_service import chat_service

router = APIRouter()


@router.post("/text", response_model=ApiResponse)
async def chat_text(req: ChatRequest):
    result = await chat_service.process_text_message(
        session_id=req.session_id,
        message=req.message,
        use_rag=req.use_rag,
    )
    return ApiResponse(data=result)


@router.post("/text/stream")
async def chat_text_stream(req: ChatRequest):
    return StreamingResponse(
        chat_service.process_text_stream(
            session_id=req.session_id,
            message=req.message,
            use_rag=req.use_rag,
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
):
    audio_data = await file.read()
    result = await chat_service.process_voice_message(session_id, audio_data)
    return ApiResponse(data=result)


@router.post("/image", response_model=ApiResponse)
async def chat_image(image_base64: str = Form(...), session_id: str = Form("default")):
    result = await chat_service.process_image_message(session_id, image_base64)
    return ApiResponse(data=result)


@router.get("/history/{session_id}", response_model=ApiResponse)
async def get_history(session_id: str):
    history = await chat_service.get_conversation_history(session_id)
    return ApiResponse(data=history)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "text")
            session_id = data.get("session_id", "default")

            if msg_type == "text":
                result = await chat_service.process_text_message(
                    session_id, data.get("message", "")
                )
                await websocket.send_json({
                    "type": "reply",
                    "data": result,
                    "state": chat_service.get_current_state(),
                })
            elif msg_type == "audio":
                audio_bytes = base64.b64decode(data.get("audio", ""))
                result = await chat_service.process_voice_message(session_id, audio_bytes)
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
