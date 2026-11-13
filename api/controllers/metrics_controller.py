from fastapi import Depends
from sqlalchemy.orm import Session

from api.dtos.metrics_dto import MetricsOverview, Period
from database.connection import get_db
from services.metrics_service import MetricsService


class MetricsController:
    def __init__(
        self,
        service: MetricsService = Depends(),
        db: Session = Depends(get_db),
    ) -> None:
        self.service = service
        self.db = db

    def overview(self, period: Period) -> MetricsOverview:
        return self.service.overview(period)
