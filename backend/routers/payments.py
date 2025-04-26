# backend/routers/payments.py

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from ..services.db import get_db
from ..models import Client, Payment

router = APIRouter(
    prefix="/api/payments",
    tags=["payments"],
)

class PaymentResponse(BaseModel):
    id: int
    amount: Decimal
    date: datetime
    service: Optional[str]
    status: str

    class Config:
        orm_mode = True

@router.get(
    "",
    response_model=List[PaymentResponse],
    summary="История платежей клиента"
)
def list_payments(
    client_phone: str = Query(..., description="Номер телефона клиента"),
    db: Session = Depends(get_db)
):
    client = db.query(Client).filter(Client.phone == client_phone).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент не найден"
        )
    payments = (
        db.query(Payment)
        .filter(Payment.client_id == client.id)
        .order_by(Payment.date.desc())
        .all()
    )
    return payments
