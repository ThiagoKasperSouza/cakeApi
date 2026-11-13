import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from core.security import decode_access_token
from models.user import User
from services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    service: UserService = Depends(),
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou ausentes",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exc
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub", ""))
    except (jwt.PyJWTError, ValueError):
        raise credentials_exc from None
    user = service.get_user(user_id)
    if user is None or not user.is_active:
        raise credentials_exc
    return user
