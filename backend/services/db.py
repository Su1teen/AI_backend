import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config import settings

# Создаём SQLAlchemy Engine на основе настроек из config.py
print("DATABASE_URL (str):", settings.DATABASE_URL)
print("DATABASE_URL (bytes):", settings.DATABASE_URL.encode("utf-8", errors="replace"))
print("DB_USER (repr):", repr(settings.DB_USER))
print("DB_PASSWORD (repr):", repr(settings.DB_PASSWORD))
print("DB_HOST (repr):", repr(settings.DB_HOST))
print("DB_PORT (repr):", repr(settings.DB_PORT))
print("DB_NAME (repr):", repr(settings.DB_NAME))

engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

# Готовим фабрику сессий
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True
)

def get_db():
    """
    Зависимость FastAPI для получения сессии БД.
    Использовать так: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
