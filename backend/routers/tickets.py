from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Body, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import smtplib, email
from ..services.db import get_db
from ..services import ai_classifier
from ..models import Ticket, AILog
from ..config import settings
router = APIRouter(
    prefix="/api/tickets",
    tags=["tickets"],
)

# ----------------------------
# Pydantic-схемы
# ----------------------------
class TicketCreate(BaseModel):
    client_id: Optional[int] = Field(None, example=1)  # Assuming client_id is an integer
    client_phone: str = Field(..., example="+71234567890")
    subject: Optional[str] = Field(None, example="Проблема с интернетом")
    text: str = Field(..., example="Нет доступа к Wi-Fi с 10 утра")
    channel: Optional[str] = Field("web", example="web")



class TicketResponse(BaseModel):
    id: int
    client_phone: str
    subject: Optional[str]
    category: Optional[str]
    status: str
    channel: str
    created_at: datetime

    class Config:
        orm_mode = True


class TicketDetail(TicketResponse):
    text: str
    priority: str
    ai_response: Optional[str]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


# ----------------------------
# Эндпоинты
# ----------------------------

@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую заявку с AI-классификацией"
)

def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db)
):
    # Классификация
    category = ai_classifier.classify_text(payload.text)

    # Сохраняем тикет
    ticket = Ticket(
        client_phone=payload.client_phone,
        subject=payload.subject,
        text=payload.text,
        channel=payload.channel,
        category=category
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Логируем AI-действие
    ai_log = AILog(
        ticket_id=ticket.id,
        action="classify",
        request_payload={"text": payload.text},
        response_payload={"category": category},
        confidence=None
    )
    db.add(ai_log)
    db.commit()

    return ticket



@router.get(
    "",
    response_model=List[TicketResponse],
    summary="Список заявок по номеру телефона"
)
def list_tickets(
    client_phone: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if not client_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'client_phone' is required"
        )
    records = (
        db.query(Ticket)
        .filter(Ticket.client_phone == client_phone)
        .order_by(Ticket.created_at.desc())
        .all()
    )
    return records


@router.get(
    "/{ticket_id}",
    response_model=TicketDetail,
    summary="Детали конкретной заявки"
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return ticket


@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse,
    summary="Обновить статус заявки"
)
def update_status(
    ticket_id: int,
    data: dict = Body(..., example={"status": "in_progress"}),
    db: Session = Depends(get_db)
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    ticket.status = data.get("status", ticket.status)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.post(
    "/{ticket_id}/response",
    summary="Сгенерировать AI-ответ и сохранить в заявке"
)
def generate_response(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    ai_resp = ai_classifier.generate_response(ticket.text)

    ticket.ai_response = ai_resp
    db.commit()

    ai_log = AILog(
        ticket_id=ticket.id,
        action="generate_response",
        request_payload={"text": ticket.text},
        response_payload={"response": ai_resp},
        confidence=None
    )
    db.add(ai_log)
    db.commit()

    return {"ai_response": ai_resp}

@router.post("/{ticket_id}/send_response", summary="Сгенерировать + отправить ответ")
def respond_and_notify(
    ticket_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Заявка не найдена")

    # 1) Генерим AI-ответ
    answer = ai_classifier.generate_response(ticket.text)
    ticket.ai_response = answer
    db.commit()

    # 2) Отправляем email в фоне
    def send_mail(to_address: str, subject: str, body: str):
        msg = email.message.EmailMessage()
        msg["From"] = settings.EMAIL_USER
        msg["To"]   = to_address
        msg["Subject"] = f"Ответ по заявке #{ticket.id}"
        msg.set_content(body)
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
            smtp.send_message(msg)

    background_tasks.add_task(send_mail, ticket.client.email, f"Ответ на заявку #{ticket.id}", answer)
    return {"ai_response": answer, "message": "Ответ сгенерирован и отправляется клиенту"}

