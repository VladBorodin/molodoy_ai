import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from app.settings import settings


engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(
	autocommit=False,
	autoflush=False,
	bind=engine
)

Base = declarative_base()


def get_database_session():
	database_session = SessionLocal()

	try:
		yield database_session
	finally:
		database_session.close()