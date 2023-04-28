from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core import config

# создаем асинхронный движок работы с бд
engine = create_async_engine(config.SQLALCHEMY_DATABASE_URL, echo=config.DB_DEBUG)

# фабрика подключений
pool_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
