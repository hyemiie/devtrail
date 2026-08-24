from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.models import Base
from db.session import engine
from core.errors import register_exception_handlers


async def create_tables() -> None:
    print("HELLO - create_tables() is running!")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Tables created!")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("HELLO - lifespan() is running!")

    await create_tables()

    print("HELLO - create_tables() finished!")

    yield

    print("Application shutting down...")


app = FastAPI(
    title="Identity Aggregator and Credit Scoring System",
    version="0.1.0",
    lifespan=lifespan,
)

register_exception_handlers(app)

# app.include_router(verify.router, prefix="/v1", tags=["verify"])
# app.include_router(users.router, prefix="/v1", tags=["Users"])