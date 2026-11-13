from sqlalchemy import select

from models.budget import Budget, BudgetStatus
from repositories.base_repository import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    model = Budget

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: BudgetStatus | None = None,
    ) -> list[Budget]:
        stmt = select(Budget)
        if status is not None:
            stmt = stmt.where(Budget.status == status)
        return list(self.db.scalars(stmt.offset(skip).limit(limit)).all())
