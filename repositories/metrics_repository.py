from datetime import date

from sqlalchemy import func, select

from repositories.base_repository import BaseRepository
from models.budget import Budget, BudgetStatus
from models.category import Category
from models.product import Product


class MetricsRepository(BaseRepository[Budget]):
    model = Budget

    def sales_by_day(self, from_date: date, to_date: date) -> list[tuple[date, int, float]]:
        stmt = (
            select(
                Budget.date,
                func.coalesce(func.sum(Budget.amount), 0).label("sales"),
                func.count(Budget.id).label("orders"),
            )
            .where(
                Budget.status == BudgetStatus.paid,
                Budget.date >= from_date,
                Budget.date <= to_date,
            )
            .group_by(Budget.date)
            .order_by(Budget.date)
        )
        return [(row.date, int(row.orders), float(row.sales or 0)) for row in self.db.execute(stmt).all()]

    def quotes_by_day(self, from_date: date, to_date: date) -> list[tuple[date, int]]:
        stmt = (
            select(Budget.date, func.count(Budget.id).label("quotes"))
            .where(Budget.date >= from_date, Budget.date <= to_date)
            .group_by(Budget.date)
            .order_by(Budget.date)
        )
        return [(row.date, int(row.quotes)) for row in self.db.execute(stmt).all()]

    def top_paid(self, from_date: date, to_date: date, limit: int = 3) -> list[Budget]:
        stmt = (
            select(Budget)
            .where(
                Budget.status == BudgetStatus.paid,
                Budget.date >= from_date,
                Budget.date <= to_date,
            )
            .order_by(Budget.amount.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def low_stock(self, threshold: int = 5, limit: int = 6) -> list[tuple[Product, str]]:
        stmt = (
            select(Product, Category.label)
            .join(Category, Category.id == Product.category_id)
            .where(Product.stock <= threshold)
            .order_by(Product.stock.asc(), Product.name.asc())
            .limit(limit)
        )
        return [(row[0], row[1]) for row in self.db.execute(stmt).all()]
