from fastapi import FastAPI
import uvicorn

# конфиг системы
from core import config

from routes.api_router import ApiRouter
from utils.logger import set_logger

# создание подключение к бд
from core.db import pool_session
from core.crud import Repo

# работа с базой данных
repo = Repo(pool_session)

# создание приложения на фастапи
app = FastAPI(debug=False)

# подюключение роутов
app.include_router(ApiRouter("api", repo).router)

# если скрипт запущен напрямую - только так запустится сервер
if __name__ == '__main__':

    # установка конфига логгера
    set_logger()

    # запуск из файла main и объекта app
    # запуск сервера
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
    )
