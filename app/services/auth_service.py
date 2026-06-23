from datetime import datetime
from datetime import timedelta
from datetime import timezone

from jose import JWTError
from jose import jwt

from app.settings import settings


class AuthService:
	def authenticate_admin(self, username: str, password: str) -> bool:
		return (
			username == settings.initial_admin_username
			and password == settings.initial_admin_password
		)

	def create_access_token(self, username: str) -> str:
		expire_at = datetime.now(timezone.utc) + timedelta(
			minutes=settings.auth_access_token_expire_minutes
		)

		payload = {
			"sub": username,
			"is_admin": True,
			"exp": expire_at
		}

		return jwt.encode(
			payload,
			settings.auth_secret_key,
			algorithm=settings.auth_algorithm
		)

	def decode_access_token(self, token: str) -> dict | None:
		try:
			payload = jwt.decode(
				token,
				settings.auth_secret_key,
				algorithms=[settings.auth_algorithm]
			)

			return payload
		except JWTError:
			return None