import logging


# декоратор открытия сессии к базе данных с транзацией
# работает только с классами, у которых в self.pool лежит асинхронный пул бд
def db_session_with(func):
    async def wrapper(self, *args, **kwargs):

        # открывает доступ к бд и дает одно подключение, которое мы уже даем на вход нашей функции
        async with self.pool.begin() as db_session:
            try:
                res = await func(self, *args, **kwargs, db_session=db_session)

                # фиксация изменений
                await db_session.commit()
            except Exception as err:
                logging.error(f"DB error: {err}")
            else:
                return res

    return wrapper
