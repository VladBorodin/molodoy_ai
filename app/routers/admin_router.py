from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_database_session
from app.models import KnowledgeChunk
from app.models import KnowledgeEntry
from app.schemas import KnowledgeEntryCreateRequest
from app.schemas import KnowledgeEntryCreateResponse
from app.services.chunk_service import ChunkService


router = APIRouter(
	prefix="/admin",
	tags=["Admin"]
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

	chunk_service = ChunkService()
	chunk_contents = chunk_service.split_text(request.content)

	for chunk_position, chunk_content in enumerate(chunk_contents):
		knowledge_chunk = KnowledgeChunk(
			entry_id=knowledge_entry.id,
			content=chunk_content,
			position=chunk_position
		)

		database_session.add(knowledge_chunk)

	database_session.commit()

	return KnowledgeEntryCreateResponse(
		entry_id=knowledge_entry.id,
		chunks_count=len(chunk_contents)
	)