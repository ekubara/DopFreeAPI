import os
from enum import Enum

from dotenv import load_dotenv

# инициализация .env конфига окружения
load_dotenv()

# дальше мы берем данные из .env


# SERVER
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
UPLOADED_IMAGES_PATH = "images/"

# DATABASE
DB_DRIVER = "postgresql+asyncpg"
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_DEBUG = True

# составление пути до базы данных - как ссылка до бд
SQLALCHEMY_DATABASE_URL = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
