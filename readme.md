# Digital Client Portal

Прототип портала самообслуживания и личного кабинета для клиентов телекоммуникационной компании.

## 🔖 Обзор
Проект включает:
- **Backend** на FastAPI (Python).
- **Frontend** на чистом HTML/CSS/JS для тестирования.
- **База данных**: PostgreSQL.
- **AI-модуль**: классификация и генерация ответов через OpenAI API.

---

## 📦 Структура проекта
```
AI_backend/ 
├── backend/ # FastAPI-приложение 
│ ├── routers/ # Роутеры: auth, users, tickets, payments 
│ ├── services/ # DB, AI classifier 
│ ├── config.py # Настройки из .env 
│ ├── models.py # SQLAlchemy-модели 
│ └── main.py # Точка входа 
├── frontend-test/ # Простой HTML/CSS/JS интерфейс 
│ ├── index.html 
│ ├── style.css 
│ └── script.js 
├── .env.example # Пример файла с переменными окружения 
├── .gitignore 
└── requirements.txt
```

---

## 🚀 Начало работы

### 1. Клонирование репозитория
```bash
1.
git clone https://github.com/Su1teen/AI_backend.git
cd AI_backend

2.

python -m venv .venv       # Windows: python -m venv .venv
# PowerShell:
. .venv/Scripts/Activate.ps1
# Git Bash / Linux / macOS:
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```
### Запуск Backend
```
uvicorn backend.main:app --reload --host 0.0.0.0 --port 7000
```
### Запуск Frontend
```
cd frontend-test
python -m http.server 3000
```
 ### ну и по эндпойнтам:
 1. Auth

| Метод | Путь                        | Описание                       |
|-------|-----------------------------|--------------------------------|
| POST  | `/api/auth/register`        | Регистрация нового клиента     |
| POST  | `/api/auth/login`           | Вход по номеру телефона        |

---

2. Users

| Метод | Путь               | Описание                                  |
|-------|--------------------|-------------------------------------------|
| GET   | `/api/users/me`    | Получить профиль (Header `X-Client-Phone`)|

---

3. Tickets

| Метод | Путь                                             | Описание                                  |
|-------|--------------------------------------------------|-------------------------------------------|
| POST  | `/api/tickets`                                   | Создать заявку с AI-классификацией        |
| GET   | `/api/tickets?client_phone=<номер>`              | Список заявок по номеру                   |
| GET   | `/api/tickets/{ticket_id}`                       | Детали заявки                             |
| PATCH | `/api/tickets/{ticket_id}/status`                | Обновить статус заявки                    |
| POST  | `/api/tickets/{ticket_id}/response`              | Сгенерировать и сохранить AI-ответ        |

---

4. Payments

| Метод | Путь                                         | Описание                         |
|-------|----------------------------------------------|----------------------------------|
| GET   | `/api/payments?client_phone=<номер>`         | История платежей клиента         |


