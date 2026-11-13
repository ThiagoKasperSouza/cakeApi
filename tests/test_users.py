import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
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


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as db:
        execute_seed_sql(db)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_category_product_relationship(client):
    cat = client.post(
        "/categories",
        json={"id": "test-cakes", "label": "Bolos de teste", "icon": "cake"},
    )
    assert cat.status_code == 201
    cat_id = cat.json()["id"]

    prod = client.post(
        "/products",
        json={"name": "Bolo de Chocolate", "price": 45.5, "category_id": cat_id, "stock": 10},
    )
    assert prod.status_code == 201
    assert prod.json()["category_id"] == cat_id

    detail = client.get(f"/categories/{cat_id}/products")
    assert detail.status_code == 200
    assert [p["name"] for p in detail.json()["products"]] == ["Bolo de Chocolate"]

    filtered = client.get("/products", params={"category_id": cat_id})
    assert len(filtered.json()) == 1


def test_product_requires_existing_category(client):
    resp = client.post(
        "/products",
        json={"name": "X", "price": 1.0, "category_id": "missing-category", "stock": 0},
    )
    assert resp.status_code == 400


def test_seeded_categories_and_products(client):
    with engine.begin() as db:
        execute_seed_sql(db)
    categories = client.get("/categories")
    assert categories.status_code == 200
    assert categories.json() == [
        {"id": "all", "label": "Tudo", "icon": "✳"},
        {"id": "cakes", "label": "Bolos", "icon": "▰"},
        {"id": "cupcakes", "label": "Cupcakes", "icon": "♧"},
        {"id": "cookies", "label": "Cookies", "icon": "◉"},
        {"id": "coffee", "label": "Cafés", "icon": "♨"},
    ]

    products = client.get("/products", params={"category_id": "all"})
    assert products.status_code == 200
    assert len(products.json()) == 6
    assert {product["category_id"] for product in products.json()} == {
        "cakes",
        "cupcakes",
        "cookies",
        "coffee",
    }
    assert client.post(
        "/categories",
        json={"id": "all", "label": "Tudo", "icon": "✳"},
    ).status_code == 400


def test_user_crud_and_auth(client):
    created = client.post(
        "/users",
        json={"name": "Thiago", "email_address": "thiago@example.com", "password": "supersecret"},
    )
    assert created.status_code == 201
    assert "password" not in created.json()

    login = client.post(
        "/auth/login",
        json={"email_address": "thiago@example.com", "password": "supersecret"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email_address"] == "thiago@example.com"

    deactivated = client.post(f"/users/{created.json()['id']}/deactivate")
    assert deactivated.json()["is_active"] is False


def test_budget_filter_by_status(client):
    client.post(
        "/budgets",
        json={
            "code": "B-001",
            "customer": "Maria",
            "date": "2026-11-12",
            "amount": "1500.00",
            "status": "approved",
        },
    )
    client.post(
        "/budgets",
        json={
            "code": "B-002",
            "customer": "João",
            "date": "2026-11-12",
            "amount": "800.00",
            "status": "pending",
        },
    )
    approved = client.get("/budgets", params={"status_filter": "approved"})
    assert [b["code"] for b in approved.json()] == ["B-001"]


def test_team_member_crud(client):
    created = client.post(
        "/team-members",
        json={
            "name": "Ana",
            "role": "Confeiteira",
            "email_address": "ana@example.com",
            "initials": "AN",
            "color": "#ff8800",
        },
    )
    assert created.status_code == 201
    member_id = created.json()["id"]

    updated = client.patch(f"/team-members/{member_id}", json={"status": "on_leave"})
    assert updated.json()["status"] == "on_leave"

    assert client.delete(f"/team-members/{member_id}").status_code == 204
    assert client.get(f"/team-members/{member_id}").status_code == 404
