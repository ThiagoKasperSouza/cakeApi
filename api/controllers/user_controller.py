from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.dtos.user_dto import ChangePassword, UserCreate, UserUpdate
from database.connection import get_db
from models.user import User
from services.user_service import UserService


class UserController:
    def __init__(
        self,
        service: UserService = Depends(),
        db: Session = Depends(get_db),
    ) -> None:
        self.service = service
        self.db = db

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.service.list_users(skip=skip, limit=limit)

    def get_user(self, user_id: int) -> User:
        user = self.service.get_user(user_id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuário não encontrado")
        return user

    def create_user(self, data: UserCreate) -> User:
        try:
            return self.service.create_user(data)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "E-mail já cadastrado") from None

    def update_user(self, user_id: int, data: UserUpdate) -> User:
        user = self.get_user(user_id)
        try:
            return self.service.update_user(user, data)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "E-mail já cadastrado") from None

    def change_password(self, current_user: User, user_id: int, data: ChangePassword) -> None:
        if current_user.id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Sem permissão para alterar esta senha")
        if not self.service.change_password(current_user, data.current_password, data.new_password):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Senha atual incorreta")

    def activate_user(self, user_id: int) -> User:
        return self.service.activate_user(self.get_user(user_id))

    def deactivate_user(self, user_id: int) -> User:
        return self.service.deactivate_user(self.get_user(user_id))

    def delete_user(self, user_id: int) -> None:
        self.service.delete_user(self.get_user(user_id))
