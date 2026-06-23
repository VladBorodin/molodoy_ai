from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from app.services.auth_service import AuthService


bearer_scheme = HTTPBearer(auto_error=False)


def require_admin(
	credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)
) -> dict:
	if credentials is None:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Authorization token is required"
		)

	auth_service = AuthService()
	payload = auth_service.decode_access_token(credentials.credentials)

	if payload is None:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid or expired token"
		)

	if not payload.get("is_admin"):
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Admin access is required"
		)

	return payload