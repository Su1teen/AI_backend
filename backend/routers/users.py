# backend/routers/users.py

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from ..services.db import get_db
from ..models import Client, Payment

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
)

class UserResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    email: str
    tariff: Optional[str]
    services: Optional[List[str]]
    balance: Decimal
    debt: Decimal
    created_at: datetime

    class Config:
        orm_mode = True

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Профиль текущего клиента"
)
def get_me(
    x_client_phone: str = Header(..., description="Номер телефона клиента"),
    db: Session = Depends(get_db)
):
    client = db.query(Client).filter(Client.phone == x_client_phone).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент не найден"
        )
    return client
