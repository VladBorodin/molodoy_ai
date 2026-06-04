from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	username = Column(String(100), unique=True, nullable=False, index=True)
	password_hash = Column(String(255), nullable=False)
	is_admin = Column(Boolean, nullable=False, default=True)
	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class KnowledgeEntry(Base):
	__tablename__ = "knowledge_entries"

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(255), nullable=False)
	content = Column(Text, nullable=False)
	is_active = Column(Boolean, nullable=False, default=True)
	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
	updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

	chunks = relationship(
		"KnowledgeChunk",
		back_populates="entry",
		cascade="all, delete-orphan"
	)


class KnowledgeChunk(Base):
	__tablename__ = "knowledge_chunks"

	id = Column(Integer, primary_key=True, index=True)
	entry_id = Column(Integer, ForeignKey("knowledge_entries.id", ondelete="CASCADE"), nullable=False)
	content = Column(Text, nullable=False)
	position = Column(Integer, nullable=False, default=0)
	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

	entry = relationship("KnowledgeEntry", back_populates="chunks")


class ChatMessage(Base):
	__tablename__ = "chat_messages"

	id = Column(Integer, primary_key=True, index=True)
	role = Column(String(50), nullable=False)
	content = Column(Text, nullable=False)
	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)