from fastapi import Depends
from sqlalchemy.orm import Session

from api.dtos.user_dto import UserCreate, UserUpdate
from core.security import hash_password, verify_password
from database.connection import get_db
from models.user import User
from repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db: Session = Depends(get_db)) -> None:
        self.repository = UserRepository(db)

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.repository.list(skip=skip, limit=limit)

    def get_user(self, user_id: int) -> User | None:
        return self.repository.get(user_id)

    def get_user_by_email(self, email_address: str) -> User | None:
        return self.repository.get_by_email(email_address)

    def create_user(self, data: UserCreate) -> User:
        user = User(
            name=data.name,
            email_address=data.email_address,
            password=hash_password(data.password),
        )
        return self.repository.add(user)

    def update_user(self, user: User, data: UserUpdate) -> User:
        payload = data.model_dump(exclude_unset=True)
        if payload.get("password") is not None:
            payload["password"] = hash_password(payload["password"])
        return self.repository.update(user, payload)

    def change_password(self, user: User, current_password: str, new_password: str) -> bool:
        if not verify_password(current_password, user.password):
            return False
        self.repository.update(user, {"password": hash_password(new_password)})
        return True

    def activate_user(self, user: User) -> User:
        return self.repository.update(user, {"is_active": True})

    def deactivate_user(self, user: User) -> User:
        return self.repository.update(user, {"is_active": False})

    def delete_user(self, user: User) -> None:
        self.repository.delete(user)

    def authenticate(self, email_address: str, password: str) -> User | None:
        user = self.get_user_by_email(email_address)
        if user is None or not verify_password(password, user.password):
            return None
        return user
