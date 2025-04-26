from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from openai import OpenAI  # ✅ Новый импорт

from ..config import settings
from ..services.db import get_db
from ..models import Client, Ticket, Payment

# Инициализация клиента OpenAI
client_ai = OpenAI(api_key=settings.OPENAI_API_KEY)

# Схемы
class ExtendedChatRequest(BaseModel):
    message: str
    client_phone: str

class ExtendedChatResponse(BaseModel):
    ai_message: str

# Инициализация роутера
router = APIRouter(
    prefix="/api/ai",
    tags=["ai"],
)

@router.post(
    "/chat_with_db",
    response_model=ExtendedChatResponse,
    summary="Общение с AI + доступ к данным клиента"
)
async def chat_with_ai_and_db(payload: ExtendedChatRequest, db: Session = Depends(get_db)):
    try:
        # 1. Найти клиента
        client = db.query(Client).filter(Client.phone == payload.client_phone).first()
        if not client:
            raise HTTPException(status_code=404, detail="Клиент не найден")

        # 2. Найти его заявки
        tickets = db.query(Ticket).filter(Ticket.client_phone == payload.client_phone).order_by(Ticket.created_at.desc()).limit(5).all()

        # 3. Найти его платежи
        payments = db.query(Payment).filter(Payment.client_id == client.id).order_by(Payment.date.desc()).limit(5).all()

        # 4. Составить краткую информацию для AI
        client_info = (
            f"Имя: {client.full_name}, "
            f"Тариф: {client.tariff or '-'}, "
            f"Баланс: {client.balance}₸, "
            f"Долг: {client.debt}₸"
        )

        recent_tickets = "\n".join(
            f"Заявка #{t.id}: {t.subject or 'Без темы'}, статус: {t.status}" for t in tickets
        ) or "Нет заявок"

        recent_payments = "\n".join(
            f"Платёж: {p.amount}₸ за {p.service or 'услугу'}, статус: {p.status}" for p in payments
        ) or "Нет платежей"

        # 5. Формируем промпт для AI
        prompt = (
            f"Ты помощник клиентского портала.\n"
            f"Информация о клиенте:\n{client_info}\n\n"
            f"Последние заявки:\n{recent_tickets}\n\n"
            f"Последние платежи:\n{recent_payments}\n\n"
            f"Вопрос клиента: {payload.message}\n"
            f"Ответь, основываясь на этих данных."
        )

        response = client_ai.chat.completions.create(  # ✅ Новый вызов
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Отвечай вежливо, кратко и по делу."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        ai_message = response.choices[0].message.content.strip()
        return ExtendedChatResponse(ai_message=ai_message)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI chat with DB error: {e}")
