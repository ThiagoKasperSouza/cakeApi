from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import auth, budgets, categories, products, team_members, users
from database.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Cake API", version="0.1.0", lifespan=lifespan)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(budgets.router)
app.include_router(team_members.router)
