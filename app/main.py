from fastapi import FastAPI

from app.database import Base
from app.database import engine
from app import models


app = FastAPI(
	title="Molodoy AI",
	description="Простое приложение для вопросно-ответного поиска по дневнику кота Молодого.",
	version="0.1.0"
)


@app.on_event("startup")
def startup():
	Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
	return {
		"message": "Molodoy AI backend is running"
	}


@app.get("/health")
def health_check():
	return {
		"status": "ok"
	}