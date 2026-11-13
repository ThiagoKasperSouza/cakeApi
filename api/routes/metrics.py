from fastapi import APIRouter, Depends

from api.controllers.metrics_controller import MetricsController
from api.dependencies import get_current_user
from api.dtos.metrics_dto import MetricsOverview, Period
from models.user import User

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/overview", response_model=MetricsOverview)
def overview(
    period: Period = "week",
    controller: MetricsController = Depends(),
    _current_user: User = Depends(get_current_user),
):
    return controller.overview(period)
