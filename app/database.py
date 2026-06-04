import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.getenv(
	"DATABASE_URL",
	"postgresql+psycopg2://molodoy_user:molodoy_password@localhost:15432/molodoy_ai"
)

engine = create_engine(DATABASE_URL)

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