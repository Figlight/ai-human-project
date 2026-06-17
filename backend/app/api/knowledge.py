from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.database import get_db
from backend.app.models.schemas import (
    ApiResponse, QAItemCreate, QAItemUpdate, QAItemResponse, DocumentResponse,
)
from backend.app.services.knowledge_service import knowledge_service
from backend.app.services.rag_service import rag_service
from backend.config import settings

router = APIRouter()


@router.get("/qa", response_model=ApiResponse)
async def list_qa(
    search: str = Query(""),
    category: str = Query(""),
    db: AsyncSession = Depends(get_db),
):
    items = await knowledge_service.list_qa(db, search, category)
    return ApiResponse(data=[
        QAItemResponse.model_validate(item) for item in items
    ])


@router.post("/qa", response_model=ApiResponse)
async def create_qa(data: QAItemCreate, db: AsyncSession = Depends(get_db)):
    item = await knowledge_service.create_qa(db, data.question, data.answer, data.category)
    return ApiResponse(data=QAItemResponse.model_validate(item))


@router.put("/qa/{qa_id}", response_model=ApiResponse)
async def update_qa(qa_id: int, data: QAItemUpdate, db: AsyncSession = Depends(get_db)):
    item = await knowledge_service.update_qa(db, qa_id, data.model_dump(exclude_none=True))
    if not item:
        return ApiResponse(code=404, message="条目不存在")
    return ApiResponse(data=QAItemResponse.model_validate(item))


@router.delete("/qa/{qa_id}", response_model=ApiResponse)
async def delete_qa(qa_id: int, db: AsyncSession = Depends(get_db)):
    success = await knowledge_service.delete_qa(db, qa_id)
    if not success:
        return ApiResponse(code=404, message="条目不存在")
    return ApiResponse(message="删除成功")


@router.post("/upload", response_model=ApiResponse)
async def upload_document(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    file_path = settings.KNOWLEDGE_DIR / file.filename
    content = await file.read()
    file_path.write_bytes(content)

    result = await rag_service.add_document(str(file_path))

    from backend.app.db.models import Document
    doc = Document(
        name=file.filename,
        file_path=str(file_path),
        file_size=f"{len(content) / 1024:.0f}KB",
        status="indexed",
        chunks=result["chunks"],
    )
    db.add(doc)
    await db.commit()

    return ApiResponse(data=result)


@router.get("/documents", response_model=ApiResponse)
async def list_documents(db: AsyncSession = Depends(get_db)):
    docs = await knowledge_service.list_documents(db)
    return ApiResponse(data=[
        DocumentResponse.model_validate(doc) for doc in docs
    ])


@router.delete("/documents/{doc_id}", response_model=ApiResponse)
async def delete_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    success = await knowledge_service.delete_document(db, doc_id)
    if not success:
        return ApiResponse(code=404, message="文档不存在")
    return ApiResponse(message="删除成功")


@router.post("/rebuild", response_model=ApiResponse)
async def rebuild_index():
    await rag_service.rebuild_index()
    return ApiResponse(message="索引重建完成")
