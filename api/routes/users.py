from fastapi import APIRouter, Depends, status
from api.controllers.user_controller import UserController
from api.dependencies import get_current_user
from api.dtos.user_dto import ChangePassword, UserCreate, UserRead, UserUpdate
from models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(skip: int = 0, limit: int = 100, controller: UserController = Depends()):
    return controller.list_users(skip=skip, limit=limit)


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, controller: UserController = Depends()):
    return controller.get_user(user_id)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, controller: UserController = Depends()):
    return controller.create_user(data)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, data: UserUpdate, controller: UserController = Depends()):
    return controller.update_user(user_id, data)


@router.post("/{user_id}/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    user_id: int,
    data: ChangePassword,
    controller: UserController = Depends(),
    current_user: User = Depends(get_current_user),
):
    controller.change_password(current_user, user_id, data)


@router.post("/{user_id}/activate", response_model=UserRead)
def activate_user(user_id: int, controller: UserController = Depends()):
    return controller.activate_user(user_id)


@router.post("/{user_id}/deactivate", response_model=UserRead)
def deactivate_user(user_id: int, controller: UserController = Depends()):
    return controller.deactivate_user(user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, controller: UserController = Depends()):
    controller.delete_user(user_id)
