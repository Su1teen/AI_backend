from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, Numeric, JSON, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Client(Base):
    """
    Клиент телеком-компании.
    """
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    tariff = Column(String(100), nullable=True)
    services = Column(JSON, nullable=True)  # Список подключенных услуг
    balance = Column(Numeric(12, 2), default=0)
    debt = Column(Numeric(12, 2), default=0)
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    tickets = relationship("Ticket", back_populates="client")
    payments = relationship("Payment", back_populates="client")


class Ticket(Base):
    """
    Заявка клиента.
    """
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    client_phone = Column(String(20), index=True)  # Для незарегистрированных
    subject = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    channel = Column(String(50), default="web")     # web, email, telegram и т.п.
    category = Column(String(100), nullable=True)
    priority = Column(String(50), default="normal")
    status = Column(String(50), default="new")      # new, in_progress, closed...
    ai_response = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Связи
    client = relationship("Client", back_populates="tickets")
    ai_logs = relationship("AILog", back_populates="ticket")


class Payment(Base):
    """
    Запись о платеже.
    """
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    date = Column(DateTime, server_default=func.now())
    service = Column(String(100), nullable=True)
    status = Column(String(50), default="completed")  # pending, completed, failed...

    # Связь
    client = relationship("Client", back_populates="payments")


class Template(Base):
    """
    Шаблон ответа для AI или оператора.
    """
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(100), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class AILog(Base):
    """
    Логи работы AI-модуля (классификация, генерация ответа и т.п.).
    """
    __tablename__ = "ai_logs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    action = Column(String(50), nullable=False)  # classify, generate_response...
    request_payload = Column(JSON, nullable=True)
    response_payload = Column(JSON, nullable=True)
    confidence = Column(Numeric(5, 4), nullable=True)  # при наличии
    created_at = Column(DateTime, server_default=func.now())

    # Связь
    ticket = relationship("Ticket", back_populates="ai_logs")
