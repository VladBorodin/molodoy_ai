from datetime import datetime

from pydantic import BaseModel
from pydantic import Field


class KnowledgeEntryCreateRequest(BaseModel):
	title: str = Field(min_length=1, max_length=255)
	content: str = Field(min_length=1)


class KnowledgeEntryUpdateRequest(BaseModel):
	title: str = Field(min_length=1, max_length=255)
	content: str = Field(min_length=1)
	is_active: bool = True


class KnowledgeEntryCreateResponse(BaseModel):
	entry_id: int
	chunks_count: int


class KnowledgeEntryUpdateResponse(BaseModel):
	entry_id: int
	chunks_count: int


class KnowledgeEntryListItemResponse(BaseModel):
	id: int
	title: str
	content_preview: str
	is_active: bool
	chunks_count: int
	created_at: datetime
	updated_at: datetime | None


class KnowledgeEntryResponse(BaseModel):
	id: int
	title: str
	content: str
	is_active: bool
	chunks_count: int
	created_at: datetime
	updated_at: datetime | None


class KnowledgeEntryDeleteResponse(BaseModel):
	deleted_entry_id: int


class ChatAskRequest(BaseModel):
	question: str = Field(min_length=1)


class ChatAskResponse(BaseModel):
	answer: str
	context_chunks: list[str]