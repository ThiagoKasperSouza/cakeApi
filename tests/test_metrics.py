import os
from datetime import date, timedelta

import pytest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.base import Base
from database.connection import execute_seed_sql, get_db
from main import app

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _override_get_db():
    previous = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    yield
    if previous is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = previous


def make_client():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as db:
        execute_seed_sql(db)
    return TestClient(app)


def auth_headers(client: TestClient) -> dict[str, str]:
    client.post(
        "/users",
        json={"name": "Metrics Tester", "email_address": "metrics@example.com", "password": "supersecret"},
    )
    response = client.post(
        "/auth/login",
        json={"email_address": "metrics@example.com", "password": "supersecret"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def teardown():
    Base.metadata.drop_all(bind=engine)


def budget(code: str, amount: float, status: str, day: date) -> dict:
    return {
        "code": code,
        "customer": f"Cliente {code}",
        "description": f"Orçamento {code}",
        "date": day.isoformat(),
        "amount": amount,
        "status": status,
        "initials": "CT",
    }


def test_overview_requires_auth():
    client = make_client()
    try:
        response = client.get("/metrics/overview?period=week")
        assert response.status_code == 401
    finally:
        teardown()


def test_overview_empty_returns_zeros():
    client = make_client()
    try:
        headers = auth_headers(client)
        response = client.get("/metrics/overview?period=week", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert body["sales_total"] == 0.0
        assert body["orders_count"] == 0
        assert body["quotes_count"] == 0
        assert body["average_ticket"] == 0.0
        assert len(body["series"]) == 7
        assert body["top_paid"] == []
        # seed cria 6 produtos com stock = 0
        assert len(body["low_stock"]) == 6
        assert all(item["stock"] <= 5 for item in body["low_stock"])
        stocks = [item["stock"] for item in body["low_stock"]]
        assert stocks == sorted(stocks)
    finally:
        teardown()


def test_overview_aggregates_paid_only():
    client = make_client()
    try:
        headers = auth_headers(client)
        today = date.today()
        yesterday = today - timedelta(days=1)

        client.post("/budgets", json=budget("ORC-9001", 1250.50, "paid", yesterday), headers=headers)
        client.post("/budgets", json=budget("ORC-9002", 2500.00, "paid", today), headers=headers)
        client.post("/budgets", json=budget("ORC-9003", 9999.00, "pending", today), headers=headers)

        response = client.get("/metrics/overview?period=week", headers=headers)
        assert response.status_code == 200
        body = response.json()

        assert body["sales_total"] == 3750.50
        assert body["orders_count"] == 2          # só paid; pending não conta
        assert body["quotes_count"] == 3          # todos os status
        assert body["average_ticket"] == 1875.25

        series = {point["date"]: point for point in body["series"]}
        assert series[yesterday.isoformat()]["sales"] == 1250.50
        assert series[yesterday.isoformat()]["orders"] == 1
        assert series[today.isoformat()]["sales"] == 2500.00
        assert series[today.isoformat()]["orders"] == 1
        assert series[today.isoformat()]["quotes"] == 2

        assert [item["amount"] for item in body["top_paid"]] == [2500.00, 1250.50]
        assert body["top_paid"][0]["code"] == "ORC-9002"
    finally:
        teardown()


def test_overview_month_window_starts_on_day_one():
    client = make_client()
    try:
        headers = auth_headers(client)
        today = date.today()
        response = client.get("/metrics/overview?period=month", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert body["window"]["from"] == today.replace(day=1).isoformat()
        assert body["window"]["to"] == today.isoformat()
        assert body["series"][0]["date"] == today.replace(day=1).isoformat()
        assert body["series"][-1]["date"] == today.isoformat()
        assert len(body["series"]) == today.day
    finally:
        teardown()


def test_overview_day_window_is_single_point():
    client = make_client()
    try:
        headers = auth_headers(client)
        today = date.today()
        response = client.get("/metrics/overview?period=day", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert len(body["series"]) == 1
        assert body["series"][0]["date"] == today.isoformat()
    finally:
        teardown()


def test_overview_rejects_invalid_period():
    client = make_client()
    try:
        headers = auth_headers(client)
        response = client.get("/metrics/overview?period=year", headers=headers)
        assert response.status_code == 422
    finally:
        teardown()
