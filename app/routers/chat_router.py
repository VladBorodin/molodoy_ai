from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.database import get_database_session
from app.models import ChatMessage
from app.models import KnowledgeChunk
from app.models import KnowledgeEntry
from app.schemas import ChatAskRequest
from app.schemas import ChatAskResponse
from app.schemas import ChatSourceResponse
from app.services.answer_service import AnswerService
from app.services.search_service import SearchService


router = APIRouter(
	prefix="/chat",
	tags=["Chat"]
)


@router.post("/ask", response_model=ChatAskResponse)
def ask_question(
	request: ChatAskRequest,
	database_session: Session = Depends(get_database_session)
):
	chunks = (
		database_session
		.query(KnowledgeChunk)
		.options(joinedload(KnowledgeChunk.entry))
		.join(KnowledgeEntry, KnowledgeChunk.entry_id == KnowledgeEntry.id)
		.filter(KnowledgeEntry.is_active.is_(True))
		.order_by(KnowledgeChunk.id.asc())
		.all()
	)

	search_service = SearchService()
	answer_service = AnswerService()

	search_results = search_service.find_relevant_chunks(
		question=request.question,
		chunks=chunks
	)

	if not search_results:
		search_results = search_service.get_general_context_chunks(
			chunks=chunks
		)

	answer = answer_service.build_answer(
		question=request.question,
		search_results=search_results
	)

	user_message = ChatMessage(
		role="user",
		content=request.question
	)

	assistant_message = ChatMessage(
		role="assistant",
		content=answer
	)

	database_session.add(user_message)
	database_session.add(assistant_message)
	database_session.commit()

	return ChatAskResponse(
		answer=answer,
		context_chunks=[
			result.content
			for result in search_results
		],
		sources=[
			ChatSourceResponse(
				entry_id=result.entry_id,
				entry_title=result.entry_title,
				chunk_id=result.chunk_id,
				position=result.position,
				score=result.score
			)
			for result in search_results
		]
	)