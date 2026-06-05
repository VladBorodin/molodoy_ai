from pydantic import BaseModel
from pydantic import Field


class KnowledgeEntryCreateRequest(BaseModel):
	title: str = Field(min_length=1, max_length=255)
	content: str = Field(min_length=1)


class KnowledgeEntryCreateResponse(BaseModel):
	entry_id: int
	chunks_count: int


class KnowledgeEntryResponse(BaseModel):
	id: int
	title: str
	content: str
	is_active: bool

	class Config:
		from_attributes = True


class ChatAskRequest(BaseModel):
	question: str = Field(min_length=1)


class ChatAskResponse(BaseModel):
	answer: str
	context_chunks: list[str]