from fastapi import Depends, HTTPException, status

from api.dtos.user_dto import LoginRequest, Token
from core.security import create_access_token
from services.user_service import UserService


class AuthController:
    def __init__(self, service: UserService = Depends()) -> None:
        self.service = service

    def login(self, data: LoginRequest) -> Token:
        user = self.service.authenticate(data.email_address, data.password)
        if user is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha incorretos")
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuário desativado")
        return Token(access_token=create_access_token(str(user.id)))

    def token(self, username: str, password: str) -> Token:
        user = self.service.authenticate(username, password)
        if user is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha incorretos")
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuário desativado")
        return Token(access_token=create_access_token(str(user.id)))
