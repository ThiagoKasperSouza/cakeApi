from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.dtos.budget_dto import BudgetCreate, BudgetUpdate
from database.connection import get_db
from models.budget import Budget, BudgetStatus
from services.budget_service import BudgetService


class BudgetController:
    def __init__(
        self,
        service: BudgetService = Depends(),
        db: Session = Depends(get_db),
    ) -> None:
        self.service = service
        self.db = db

    def list_budgets(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: BudgetStatus | None = None,
    ) -> list[Budget]:
        return self.service.list_budgets(skip=skip, limit=limit, status=status_filter)

    def get_budget(self, budget_id: int) -> Budget:
        budget = self.service.get_budget(budget_id)
        if budget is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Orçamento não encontrado")
        return budget

    def create_budget(self, data: BudgetCreate) -> Budget:
        try:
            return self.service.create_budget(data)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Código de orçamento já existe") from None

    def update_budget(self, budget_id: int, data: BudgetUpdate) -> Budget:
        budget = self.get_budget(budget_id)
        try:
            return self.service.update_budget(budget, data)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Código de orçamento já existe") from None

    def delete_budget(self, budget_id: int) -> None:
        self.service.delete_budget(self.get_budget(budget_id))
