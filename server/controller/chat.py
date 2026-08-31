import hashlib
import uuid

from fastapi import FastAPI, APIRouter, HTTPException
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

from db.models import Base
from db.session import engine, AsyncSessionLocal
from core.errors import InvalidInputError, NotFoundError, register_exception_handlers
from sqlalchemy import text
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


router = APIRouter()

class createChat(BaseModel):
    room_id: str
    content: str
    sender: str

class ChatDetail(BaseModel):
    room_id: str
    content: str
    sender: str


async def create_chat(chat_detail:createChat ):

    async with AsyncSessionLocal as session:
        result = await session.execute(text("""
        INSERT into chat_messages (id, room_id, content, sender)
        VALUES (id, room_id, content, sender)
        RETURNING *
"""),
        {"name": chat_detail.room_id, "content": chat_detail.content, "sender": chat_detail.sender})
        chat = result.scalar_one()
        await session.commit()

        print(f"chat: {chat}")


   
@router.post('/')
async def create_chat(chat_detail:createChat ):
    try:
          save_chat_response = await create_chat(chat_detail= chat_detail)
          print("chat_response", save_chat_response)
    except Exception as e:
         print(f'Error {e}')

    

   

@router.put("/chat/{chat_id}")
async def update_chat(chat_details: ChatDetail, chat_id : uuid.UUID):
    updates = chat_details.model_dump(exclude_unset=True)

    for field, value in updates.items():
        print(field, value)
    

    async with AsyncSessionLocal as session:
        result = await session.execute(text("""
            UPDATE chat_messages 
            SET{", ".join(set_clauses)}
            WHERE id = :id
            """), {"id": chat_id})
        updated_id = result.scalar_one_or_none()

        if updated_id is None:
                raise NotFoundError(f"No chat found for id={id}")

        await session.commit()
    return {"id": updated_id, "status": "updated"}


@router.get("/chat/{id}")
async def get_chat(id: uuid.UUID):  
    async with AsyncSessionLocal() as session:
           result = await session.execute(
        text("""
            SELECT id, room_id, content, sender FROM chat_messages
            WHERE id = :id
        """),
        {"id": id},
    )
    chat = result.mappings().one_or_none()

    if chat is None:
            raise NotFoundError(f"No chat found for id={id}")
    
    await session.commit()

    return {"chat": chat}


@router.get("/chat/{room_id}")
async def list_chat(room_id: uuid.UUID):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT id, room_id, content, sender, room, created_at FROM chat_messages WHERE room_id = :id"),
             {"room_id": room_id}
        )
        chat_list = result.mappings().all()

    return {"chat": [dict(d) for d in chat_list]}


@router.delete("/chat/{id}")
async def delete_chat(id: uuid.UUID):
    print('received details', id)
  
    async with AsyncSessionLocal() as session:
           result = await session.execute(
        text("""
            SELECT id, room_id, content, sender FROM chat_messages
            WHERE id = :id
        """),
        {"id": id},
    )
           
           if not result.mappings(). one_or_none():
                await session.execute(text("""
            DELETE FROM chat_messages 
                WHERE id = :id
            """), 
            {"id": id})
                
    await session.commit()

    return {"chat deleted"}

