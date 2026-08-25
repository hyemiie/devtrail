import uuid

from db.session import engine, AsyncSessionLocal
from sqlalchemy import text

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
    user_record
    if user is None:
            user_record = False
    user_record = True
    

    return user_record
