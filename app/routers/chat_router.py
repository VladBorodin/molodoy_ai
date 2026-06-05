from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_database_session
from app.models import ChatMessage
from app.models import KnowledgeChunk
from app.schemas import ChatAskRequest
from app.schemas import ChatAskResponse
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
		.order_by(KnowledgeChunk.id.asc())
		.all()
	)

	chunk_contents = [
		chunk.content
		for chunk in chunks
	]

	search_service = SearchService()
	answer_service = AnswerService()

	relevant_chunks = search_service.find_relevant_chunks(
		question=request.question,
		chunk_contents=chunk_contents
	)

	answer = answer_service.build_answer(
		question=request.question,
		context_chunks=relevant_chunks
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
		context_chunks=relevant_chunks
	)