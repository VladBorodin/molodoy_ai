from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import get_database_session
from app.models import KnowledgeChunk
from app.models import KnowledgeEntry
from app.schemas import KnowledgeEntryCreateRequest
from app.schemas import KnowledgeEntryCreateResponse
from app.schemas import KnowledgeEntryDeleteResponse
from app.schemas import KnowledgeEntryListItemResponse
from app.schemas import KnowledgeEntryResponse
from app.schemas import KnowledgeEntryUpdateRequest
from app.schemas import KnowledgeEntryUpdateResponse
from app.services.chunk_service import ChunkService


router = APIRouter(
	prefix="/admin",
	tags=["Admin"]
)


@router.get("/entries", response_model=list[KnowledgeEntryListItemResponse])
def get_knowledge_entries(
	database_session: Session = Depends(get_database_session)
):
	entries = (
		database_session
		.query(KnowledgeEntry)
		.order_by(KnowledgeEntry.created_at.desc())
		.all()
	)

	return [
		KnowledgeEntryListItemResponse(
			id=entry.id,
			title=entry.title,
			content_preview=_build_content_preview(entry.content),
			is_active=entry.is_active,
			chunks_count=len(entry.chunks),
			created_at=entry.created_at,
			updated_at=entry.updated_at
		)
		for entry in entries
	]


@router.get("/entries/{entry_id}", response_model=KnowledgeEntryResponse)
def get_knowledge_entry(
	entry_id: int,
	database_session: Session = Depends(get_database_session)
):
	entry = _get_entry_or_404(
		entry_id=entry_id,
		database_session=database_session
	)

	return KnowledgeEntryResponse(
		id=entry.id,
		title=entry.title,
		content=entry.content,
		is_active=entry.is_active,
		chunks_count=len(entry.chunks),
		created_at=entry.created_at,
		updated_at=entry.updated_at
	)


@router.post("/entries", response_model=KnowledgeEntryCreateResponse)
def create_knowledge_entry(
	request: KnowledgeEntryCreateRequest,
	database_session: Session = Depends(get_database_session)
):
	knowledge_entry = KnowledgeEntry(
		title=request.title,
		content=request.content
	)

	database_session.add(knowledge_entry)
	database_session.commit()
	database_session.refresh(knowledge_entry)

	chunks_count = _rebuild_entry_chunks(
		entry_id=knowledge_entry.id,
		content=request.content,
		database_session=database_session
	)

	database_session.commit()

	return KnowledgeEntryCreateResponse(
		entry_id=knowledge_entry.id,
		chunks_count=chunks_count
	)


@router.put("/entries/{entry_id}", response_model=KnowledgeEntryUpdateResponse)
def update_knowledge_entry(
	entry_id: int,
	request: KnowledgeEntryUpdateRequest,
	database_session: Session = Depends(get_database_session)
):
	entry = _get_entry_or_404(
		entry_id=entry_id,
		database_session=database_session
	)

	entry.title = request.title
	entry.content = request.content
	entry.is_active = request.is_active

	chunks_count = _rebuild_entry_chunks(
		entry_id=entry.id,
		content=request.content,
		database_session=database_session
	)

	database_session.commit()

	return KnowledgeEntryUpdateResponse(
		entry_id=entry.id,
		chunks_count=chunks_count
	)


@router.delete("/entries/{entry_id}", response_model=KnowledgeEntryDeleteResponse)
def delete_knowledge_entry(
	entry_id: int,
	database_session: Session = Depends(get_database_session)
):
	entry = _get_entry_or_404(
		entry_id=entry_id,
		database_session=database_session
	)

	database_session.delete(entry)
	database_session.commit()

	return KnowledgeEntryDeleteResponse(
		deleted_entry_id=entry_id
	)


def _get_entry_or_404(
	entry_id: int,
	database_session: Session
) -> KnowledgeEntry:
	entry = (
		database_session
		.query(KnowledgeEntry)
		.filter(KnowledgeEntry.id == entry_id)
		.first()
	)

	if entry is None:
		raise HTTPException(
			status_code=404,
			detail="Knowledge entry not found"
		)

	return entry


def _rebuild_entry_chunks(
	entry_id: int,
	content: str,
	database_session: Session
) -> int:
	(
		database_session
		.query(KnowledgeChunk)
		.filter(KnowledgeChunk.entry_id == entry_id)
		.delete(synchronize_session=False)
	)

	chunk_service = ChunkService()
	chunk_contents = chunk_service.split_text(content)

	for chunk_position, chunk_content in enumerate(chunk_contents):
		knowledge_chunk = KnowledgeChunk(
			entry_id=entry_id,
			content=chunk_content,
			position=chunk_position
		)

		database_session.add(knowledge_chunk)

	return len(chunk_contents)


def _build_content_preview(content: str, preview_length: int = 180) -> str:
	normalized_content = " ".join(content.split())

	if len(normalized_content) <= preview_length:
		return normalized_content

	return normalized_content[:preview_length].rstrip() + "..."