from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from app.dependencies.auth_dependencies import require_admin
from app.schemas import AuthLoginRequest
from app.schemas import AuthLoginResponse
from app.schemas import AuthMeResponse
from app.services.auth_service import AuthService


router = APIRouter(
	prefix="/auth",
	tags=["Auth"]
)


@router.post("/login", response_model=AuthLoginResponse)
def login(request: AuthLoginRequest):
	auth_service = AuthService()

	is_authenticated = auth_service.authenticate_admin(
		username=request.username,
		password=request.password
	)

	if not is_authenticated:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid username or password"
		)

	access_token = auth_service.create_access_token(
		username=request.username
	)

	return AuthLoginResponse(
		access_token=access_token
	)


@router.get("/me", response_model=AuthMeResponse)
def get_current_admin(payload: dict = Depends(require_admin)):
	return AuthMeResponse(
		username=payload.get("sub", ""),
		is_admin=True
	)