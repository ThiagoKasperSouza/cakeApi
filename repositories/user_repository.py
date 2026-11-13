from sqlalchemy import select

from models.user import User
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email_address: str) -> User | None:
        return self.db.scalar(select(User).where(User.email_address == email_address))
