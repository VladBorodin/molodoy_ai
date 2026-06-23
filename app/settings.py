import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


def get_string(name: str, default: str) -> str:
	return os.getenv(name, default)


def get_int(name: str, default: int) -> int:
	value = os.getenv(name)

	if value is None:
		return default

	try:
		return int(value)
	except ValueError:
		return default


def get_float(name: str, default: float) -> float:
	value = os.getenv(name)

	if value is None:
		return default

	try:
		return float(value)
	except ValueError:
		return default


def get_bool(name: str, default: bool) -> bool:
	value = os.getenv(name)

	if value is None:
		return default

	return value.lower() in ("true", "1", "yes", "y", "on")


@dataclass(frozen=True)
class Settings:
	app_name: str = get_string("APP_NAME", "Molodoy AI")
	app_env: str = get_string("APP_ENV", "development")
	app_debug: bool = get_bool("APP_DEBUG", True)

	database_url: str = get_string(
		"DATABASE_URL",
		"postgresql+psycopg2://molodoy_user:molodoy_password@localhost:15432/molodoy_ai"
	)

	llm_provider: str = get_string("LLM_PROVIDER", "openai_compatible")
	llm_api_url: str = get_string("LLM_API_URL", "")
	llm_api_key: str = get_string("LLM_API_KEY", "")
	llm_model: str = get_string("LLM_MODEL", "")
	llm_timeout_seconds: int = get_int("LLM_TIMEOUT_SECONDS", 60)
	llm_temperature: float = get_float("LLM_TEMPERATURE", 0.3)
	llm_max_tokens: int = get_int("LLM_MAX_TOKENS", 800)

	rag_max_context_chunks: int = get_int("RAG_MAX_CONTEXT_CHUNKS", 3)
	rag_max_context_chars: int = get_int("RAG_MAX_CONTEXT_CHARS", 3500)

	chunk_size: int = get_int("CHUNK_SIZE", 900)
	chunk_overlap_sentences: int = get_int("CHUNK_OVERLAP_SENTENCES", 1)
	chunk_max_overlap_length: int = get_int("CHUNK_MAX_OVERLAP_LENGTH", 220)
	chunk_min_tail_length: int = get_int("CHUNK_MIN_TAIL_LENGTH", 300)

	auth_secret_key: str = get_string("AUTH_SECRET_KEY", "development_secret_key")
	auth_access_token_expire_minutes: int = get_int("AUTH_ACCESS_TOKEN_EXPIRE_MINUTES", 1440)
	auth_algorithm: str = get_string("AUTH_ALGORITHM", "HS256")
	initial_admin_username: str = get_string("INITIAL_ADMIN_USERNAME", "admin")
	initial_admin_password: str = get_string("INITIAL_ADMIN_PASSWORD", "admin")


settings = Settings()