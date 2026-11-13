from fastapi import Depends
from sqlalchemy.orm import Session

from api.dtos.budget_dto import BudgetCreate, BudgetUpdate
from database.connection import get_db
from models.budget import Budget, BudgetStatus
from repositories.budget_repository import BudgetRepository


class BudgetService:
    def __init__(self, db: Session = Depends(get_db)) -> None:
        self.repository = BudgetRepository(db)

    def list_budgets(
        self,
        skip: int = 0,
        limit: int = 100,
        status: BudgetStatus | None = None,
    ) -> list[Budget]:
        return self.repository.list(skip=skip, limit=limit, status=status)

    def get_budget(self, budget_id: int) -> Budget | None:
        return self.repository.get(budget_id)

    def create_budget(self, data: BudgetCreate) -> Budget:
        return self.repository.add(Budget(**data.model_dump()))

    def update_budget(self, budget: Budget, data: BudgetUpdate) -> Budget:
        return self.repository.update(budget, data.model_dump(exclude_unset=True))

    def delete_budget(self, budget: Budget) -> None:
        self.repository.delete(budget)
