import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from core import config


def main():
    # Создаем объект Engine, который будет использоваться объектами ниже для связи с БД
    # engine = create_engine(URL.create(**DATABASE))
    engine= create_async_engine(config.SQLALCHEMY_DATABASE_URL, echo=config.DB_DEBUG)

    # импортирую из schema
    from core.schema import Base

    # Метод create_all создает таблицы в БД , определенные с помощью  DeclarativeBase
    async def init_models():
        # движок асинхронный и надо создать подключение к бд
        async with engine.begin() as conn:
            # пересоздание бд
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    # асинхронный запуск функции
    asyncio.run(init_models())


if __name__ == "__main__":
    main()
