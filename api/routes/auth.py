from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from api.controllers.auth_controller import AuthController
from api.dtos.user_dto import LoginRequest, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(data: LoginRequest, controller: AuthController = Depends()):
    return controller.login(data)


@router.post("/token", response_model=Token, include_in_schema=False)
def token(form: OAuth2PasswordRequestForm = Depends(), controller: AuthController = Depends()):
    return controller.token(form.username, form.password)
