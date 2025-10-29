from typing import Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from api.config.settings import get_settings


settings = get_settings()


# Example URLs:
# - Postgres: postgresql+asyncpg://user:pass@host:5432/autoteamai
# - SQLite (dev): sqlite+aiosqlite:///./autoteamai.db
engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)


AsyncSessionLocal = async_sessionmaker(
bind=engine,
autoflush=False,
expire_on_commit=False,
class_=AsyncSession,
)


Base = declarative_base()


async def get_session() -> Generator[AsyncSession, None, None]:
    async with AsyncSessionLocal() as session:
        yield session   