from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import models
from app.database import Base
from app.database import engine
from app.routers.admin_router import router as admin_router
from app.routers.chat_router import router as chat_router


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "static"
INDEX_HTML_PATH = FRONTEND_DIR / "index.html"


app = FastAPI(
	title="Molodoy AI",
	description="Простое приложение для вопросно-ответного поиска по дневнику кота Молодого.",
	version="0.1.0"
)


@app.on_event("startup")
def startup():
	Base.metadata.create_all(bind=engine)


app.include_router(admin_router)
app.include_router(chat_router)

app.mount(
	"/static",
	StaticFiles(directory=FRONTEND_DIR),
	name="static"
)


@app.get("/")
def read_index():
	return FileResponse(INDEX_HTML_PATH)


@app.get("/health")
def health_check():
	return {
		"status": "ok"
	}