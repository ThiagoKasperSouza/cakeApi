from fastapi import APIRouter, Depends, status

from api.controllers.budget_controller import BudgetController
from api.dtos.budget_dto import BudgetCreate, BudgetRead, BudgetUpdate
from models.budget import BudgetStatus

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetRead])
def list_budgets(
    skip: int = 0,
    limit: int = 100,
    status_filter: BudgetStatus | None = None,
    controller: BudgetController = Depends(),
):
    return controller.list_budgets(skip=skip, limit=limit, status_filter=status_filter)


@router.get("/{budget_id}", response_model=BudgetRead)
def get_budget(budget_id: int, controller: BudgetController = Depends()):
    return controller.get_budget(budget_id)


@router.post("", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
def create_budget(data: BudgetCreate, controller: BudgetController = Depends()):
    return controller.create_budget(data)


@router.patch("/{budget_id}", response_model=BudgetRead)
def update_budget(budget_id: int, data: BudgetUpdate, controller: BudgetController = Depends()):
    return controller.update_budget(budget_id, data)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: int, controller: BudgetController = Depends()):
    controller.delete_budget(budget_id)
