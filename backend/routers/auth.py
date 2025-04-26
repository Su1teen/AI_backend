from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from ..services.db import get_db
from ..models import Client

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)

# Схемы
class RegisterRequest(BaseModel):
    full_name: str = Field(..., example="Иван Иванов")
    phone: str = Field(..., example="+79001234567")
    email: EmailStr = Field(..., example="ivan@example.com")

class RegisterResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    email: EmailStr

class LoginRequest(BaseModel):
    phone: str = Field(..., example="+79001234567")

class LoginResponse(BaseModel):
    message: str


# Эндпоинты

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового клиента"
)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    # Проверяем, нет ли уже такого номера или email
    exists = db.query(Client).filter(
        (Client.phone == payload.phone) | (Client.email == payload.email)
    ).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Клиент с таким телефоном или email уже существует"
        )

    client = Client(
        full_name=payload.full_name,
        phone=payload.phone,
        email=payload.email,
    )
    db.add(client)
    db.commit()
    db.refresh(client)

    return RegisterResponse(
        id=client.id,
        full_name=client.full_name,
        phone=client.phone,
        email=client.email
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Вход по номеру телефона"
)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.phone == payload.phone).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент с таким номером не найден"
        )
    # Здесь можно выдавать JWT, но для простоты просто возвращаем сообщение
    return LoginResponse(message="Успешный вход")
