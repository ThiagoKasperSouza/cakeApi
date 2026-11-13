from datetime import date, timedelta

from fastapi import Depends
from sqlalchemy.orm import Session

from api.dtos.metrics_dto import (
    LowStockItem,
    MetricsOverview,
    MetricsWindow,
    Period,
    SeriesPoint,
    TopPaidItem,
)
from database.connection import get_db
from repositories.metrics_repository import MetricsRepository


class MetricsService:
    def __init__(self, db: Session = Depends(get_db)) -> None:
        self.repository = MetricsRepository(db)

    def overview(self, period: Period) -> MetricsOverview:
        today = date.today()
        if period == "day":
            start = today
        elif period == "week":
            start = today - timedelta(days=6)
        else:
            start = today.replace(day=1)

        sales_by_day = {d: (orders, sales) for d, orders, sales in self.repository.sales_by_day(start, today)}
        quotes_by_day = {d: quotes for d, quotes in self.repository.quotes_by_day(start, today)}

        series: list[SeriesPoint] = []
        current = start
        while current <= today:
            orders, sales = sales_by_day.get(current, (0, 0.0))
            series.append(
                SeriesPoint(
                    date=current,
                    label=current.strftime("%d"),
                    sales=round(float(sales), 2),
                    orders=int(orders),
                    quotes=quotes_by_day.get(current, 0),
                )
            )
            current += timedelta(days=1)

        sales_total = round(sum(point.sales for point in series), 2)
        orders_count = sum(point.orders for point in series)
        quotes_count = sum(point.quotes for point in series)
        average_ticket = round(sales_total / orders_count, 2) if orders_count else 0.0

        top_paid = [
            TopPaidItem(
                id=budget.id,
                code=budget.code,
                customer=budget.customer,
                amount=round(float(budget.amount), 2),
                date=budget.date,
            )
            for budget in self.repository.top_paid(start, today)
        ]

        low_stock = [
            LowStockItem(
                id=product.id,
                name=product.name,
                category_id=product.category_id,
                category_label=label,
                stock=product.stock,
            )
            for product, label in self.repository.low_stock()
        ]

        return MetricsOverview(
            period=period,
            window=MetricsWindow(from_=start, to=today),
            sales_total=sales_total,
            orders_count=orders_count,
            quotes_count=quotes_count,
            average_ticket=average_ticket,
            series=series,
            top_paid=top_paid,
            low_stock=low_stock,
        )
