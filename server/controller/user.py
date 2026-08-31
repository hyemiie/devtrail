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

class UserDetail(BaseModel):
    password: str
    email: str
    name: str

class UserFullDetail(BaseModel):
    password_hash: str
    email: str
    name: str
    current_level: str
    submissions: str
    lesson_progress: str
    assessment_submissions: str
    chat_rooms:str

@router.post('/')
async def create_user(user_details:UserDetail ):
    print("user_detail", user_details)
    hashed_password = password_hash.hash(user_details.password)

    async with AsyncSessionLocal as session:
        result = await session.execute(text("""
        INSERT into users (id, name, email, password_hash)
        VALUES (id, name, email, password_hash)
        RETURNING id
"""),
        {"name": user_details.name, "email": user_details.email, "password_hash": hashed_password})
        user_id = result.scalar_one()
        await session.commit()

        print(f"user_id: {user_id}")

        return user_id
    
@router.post("/login")
async def user_login(email: str, password: str):

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT id, name, email, password_hash
                FROM users
                WHERE email = :email
            """),
            {"email": email},
        )

        retrieved_user = result.mappings().one_or_none()

        if retrieved_user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        if not password_hash.verify(
            password,
            retrieved_user["password_hash"]
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

    return {
        "message": "Login successful",
        "user_id": retrieved_user["id"],
        "name": retrieved_user["name"],
        "email": retrieved_user["email"],
    }


@router.put("/user/{user_id}")
async def update_user(user_details: UserFullDetail, user_id : uuid.UUID):
    updates = user_details.model_dump(exclude_unset=True)

    print("update user",updates)

    for field, value in updates.items():
        print(field, value)
    

    async with AsyncSessionLocal as session:
        result = await session.execute(text("""
            UPDATE users 
            SET{", ".join(set_clauses)}
            WHERE id = :id
            """), {"id": user_id})
        updated_id = result.scalar_one_or_none()

        if updated_id is None:
                raise NotFoundError(f"No user found for id={id}")

        await session.commit()
    return {"id": updated_id, "status": "updated"}



@router.get("/user/{id}")
async def get_user(id: uuid.UUID):
    print('received details', id)
  
    async with AsyncSessionLocal() as session:
           result = await session.execute(
        text("""
            SELECT id, name, email FROM users
            WHERE id = :id
        """),
        {"id": id},
    )
    user = result.mappings().one_or_none()

    if user is None:
            raise NotFoundError(f"No user found for id={id}")
    
    await session.commit()

    return {"user": user}


@router.get("/users")
async def list_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT id, name, email, created_at FROM users")
        )
        users = result.mappings().all()

    return {"users": [dict(d) for d in users]}


@router.delete("/user/{id}")
async def delete_user(id: uuid.UUID):
    print('received detials', id)
  
    async with AsyncSessionLocal() as session:
           result = await session.execute(
        text("""
            SELECT id, name, email FROM users
            WHERE id = :id
        """),
        {"id": id},
    )
           
           if not result.mappings(). one_or_none():
                await session.execute(text("""
            DELETE FROM users 
                WHERE id = :id
            """), 
            {"id": id})
                
    await session.commit()

    return {"user deleted"}

