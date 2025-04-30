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
    summary="Персонализированный чат с доступом к данным"
)
async def chat_with_ai_and_db(payload: ExtendedChatRequest, db: Session = Depends(get_db)):
    try:
        # 1. Получаем данные клиента
        client = db.query(Client).filter(Client.phone == payload.client_phone).first()
        if not client:
            raise HTTPException(status_code=404, detail="Клиент не найден")

        # 2. Формируем персонализированный промпт
        prompt = (
            f"Ты - персональный ассистент клиента {client.full_name} в сервисном портале.\n"
            f"Информация о клиенте:\n"
            f"- Имя: {client.full_name}\n"
            f"- Тариф: {client.tariff or 'не указан'}\n"
            f"- Баланс: {client.balance}₸\n"
            f"- Долг: {client.debt}₸\n\n"
            
            f"Отвечай на русском языке, будь вежливым и профессиональным.\n"
            f"Если клиент спрашивает о балансе или платежах, уточняй конкретные цифры.\n"
            f"Если вопрос про заявки, проверяй их статус.\n\n"
            f"Вопрос клиента: {payload.message}"
        )

        # 3. Получаем ответ от AI
        response = client_ai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Ты персональный ассистент сервисного портала. "
                        "Отвечай кратко и по делу на русском языке. "
                        "Используй только факты из предоставленных данных."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=256
        )

        # 4. Возвращаем ответ
        ai_message = response.choices[0].message.content.strip()
        return ExtendedChatResponse(ai_message=ai_message)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка AI-ассистента: {str(e)}"
        )