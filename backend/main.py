# backend/main.py

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models import Base
from .services.db import engine

from .routers.auth import router as auth_router
from .routers.users import router as users_router
from .routers.tickets import router as tickets_router
from .routers.payments import router as payments_router

app = FastAPI(
    title="Digital Client Portal",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Подключаем все роутеры
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tickets_router)
app.include_router(payments_router)

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
    )
