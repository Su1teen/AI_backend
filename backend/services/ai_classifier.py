import openai
from fastapi import HTTPException
from ..config import settings

# Устанавливаем ключ
openai.api_key = settings.OPENAI_API_KEY

def classify_text(text: str) -> str:
    """
    Отправляет в OpenAI запрос на классификацию обращения.
    Возвращает категорию (e.g. 'жалоба', 'инцидент' и т.п.).
    """
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты — классификатор обращений телеком-портала. "
                        "Категории: подключение, инцидент, жалоба, информация."
                    )
                },
                {"role": "user", "content": text}
            ]
        )
        category = resp.choices[0].message.content.strip()
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
