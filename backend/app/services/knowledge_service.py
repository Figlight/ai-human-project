from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models import QAItem, Document
from backend.app.services.rag_service import rag_service
from backend.config import settings


class KnowledgeService:
    async def list_qa(
        self, db: AsyncSession, search: str = "", category: str = ""
    ) -> list[QAItem]:
        stmt = select(QAItem).order_by(QAItem.created_at.desc())
        if search:
            stmt = stmt.where(
                QAItem.question.contains(search) | QAItem.answer.contains(search)
            )
        if category:
            stmt = stmt.where(QAItem.category == category)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_qa(
        self, db: AsyncSession, question: str, answer: str, category: str
    ) -> QAItem:
        item = QAItem(question=question, answer=answer, category=category)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        await rag_service.add_qa_pair(question, answer)
        return item

    async def update_qa(
        self, db: AsyncSession, qa_id: int, data: dict
    ) -> QAItem | None:
        item = await db.get(QAItem, qa_id)
        if not item:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(item, key, value)
        await db.commit()
        await db.refresh(item)

        # Sync RAG: remove old + add new
        if "question" in data or "answer" in data:
            await rag_service.add_qa_pair(item.question, item.answer)

        return item

    async def delete_qa(self, db: AsyncSession, qa_id: int) -> bool:
        item = await db.get(QAItem, qa_id)
        if not item:
            return False
        await db.delete(item)
        await db.commit()
        return True

    async def list_documents(self, db: AsyncSession) -> list[Document]:
        result = await db.execute(
            select(Document).order_by(Document.created_at.desc())
        )
        return result.scalars().all()

    async def delete_document(self, db: AsyncSession, doc_id: int) -> bool:
        item = await db.get(Document, doc_id)
        if not item:
            return False
        # Delete file from disk
        if item.file_path:
            path = settings.KNOWLEDGE_DIR / item.name
            if path.exists():
                path.unlink()
        await db.delete(item)
        await db.commit()
        return True


knowledge_service = KnowledgeService()
