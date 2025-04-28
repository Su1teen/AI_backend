import openai
from fastapi import HTTPException
from ..config import settings

# Устанавливаем ключ
openai.api_key = settings.OPENAI_API_KEY

ALLOWED_CATEGORIES = {"подключение", "инцидент", "жалоба", "информация"}

def classify_text(text: str) -> str:
    """
    Отправляет в OpenAI запрос на классификацию обращения.
    Возвращает одну из 4 категорий: 'подключение', 'инцидент', 'жалоба', 'информация'.
    """
    try:
        resp = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты — классификатор обращений клиентского портала. "
                        "Ответь только ОДНИМ словом, без пояснений: "
                        "подключение, инцидент, жалоба или информация. "
                        "Только одно слово из этого списка."
                    )
                },
                {"role": "user", "content": text}
            ]
        )
        category = resp.choices[0].message.content.strip().lower()

        # Проверка на допустимые значения
        if category not in ALLOWED_CATEGORIES:
            raise ValueError(f"Unexpected category from AI: {category}")

        return category
    except Exception as e:
        # пробросим как HTTP-ошибку для FastAPI
        raise HTTPException(status_code=500, detail=f"AI classification error: {e}")

def generate_response(text: str) -> str:
    """
    Генерирует вежливый ответ на обращение клиента.
    """
    try:
        resp = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.7,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты — AI-ассистент клиентского портала. "
                        "Сформулируй вежливый и информативный ответ на обращение."
                    )
                },
                {"role": "user", "content": text}
            ]
        )
        answer = resp.choices[0].message.content.strip()
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI response generation error: {e}")
