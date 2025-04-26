from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config import settings

# Создаём SQLAlchemy Engine на основе настроек из config.py
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,                # логировать все SQL-запросы в консоль
    future=True               # использовать 2.0-style API
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
