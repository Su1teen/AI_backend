from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
from sqlalchemy.orm import Session
from ..services.db import get_db
from ..models import Ticket, Comment, Client, Payment
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/operator", tags=["operator"])

class TicketAdmin(BaseModel):
    id: int
    subject: Optional[str]
    category: Optional[str]
    status: str
    priority: str
    assigned_to: Optional[str]
    client_phone: str
    created_at: datetime
    class Config: orm_mode = True

@router.get("/tickets", response_model=List[TicketAdmin], summary="Список заявок (панель оператора)")
def list_tickets(
    category: Optional[str] = Query(None),
    status:   Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Ticket)
    if category: q = q.filter(Ticket.category == category)
    if status:   q = q.filter(Ticket.status   == status)
    return q.order_by(Ticket.created_at.desc()).all()

@router.patch("/tickets/{ticket_id}", response_model=TicketAdmin, summary="Обновить заявку (категория, статус, исполнитель)")
def update_ticket(
    ticket_id: int,
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Заявка не найдена")
    for field in ("category","status","assigned_to","priority"):
        if field in data:
            setattr(ticket, field, data[field])
    db.commit(); db.refresh(ticket)
    return ticket

class CommentCreate(BaseModel):
    author: str
    text:   str

class CommentOut(CommentCreate):
    id: int
    created_at: datetime
    class Config: orm_mode = True

@router.get("/tickets/{ticket_id}/comments", response_model=List[CommentOut])
def get_comments(ticket_id: int, db: Session = Depends(get_db)):
    return db.query(Comment).filter(Comment.ticket_id == ticket_id).order_by(Comment.created_at).all()

@router.post("/tickets/{ticket_id}/comments", response_model=CommentOut, status_code=201)
def add_comment(ticket_id: int, payload: CommentCreate, db: Session = Depends(get_db)):
    if not db.get(Ticket, ticket_id):
        raise HTTPException(404, "Заявка не найдена")
    c = Comment(ticket_id=ticket_id, author=payload.author, text=payload.text)
    db.add(c); db.commit(); db.refresh(c)
    return c

@router.get("/tickets/{ticket_id}/history", summary="История клиента по заявке")
def client_history(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Заявка не найдена")
    client = db.query(Client).filter(Client.phone == ticket.client_phone).first()
    payments = db.query(Payment).filter(Payment.client_id == client.id).order_by(Payment.date.desc()).limit(10).all()
    tickets  = db.query(Ticket).filter(Ticket.client_phone == ticket.client_phone).order_by(Ticket.created_at.desc()).limit(10).all()
    return {
        "client": client,
        "payments": payments,
        "tickets": tickets
    }
