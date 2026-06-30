import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env-файла
load_dotenv()

# База фильмов (Sakila)
FILM_DB_CONFIG = {
    'host': os.getenv('FILM_DB_HOST', 'default_host'),
    'user': os.getenv('FILM_DB_USER', 'default_user'),
    'password': os.getenv('FILM_DB_PASSWORD', 'default_password'),
    'database': os.getenv('FILM_DB_NAME', 'default_db')
}

# База логов и аналитики (ich_edit)
LOG_DB_CONFIG = {
    'host': os.getenv('LOG_DB_HOST', 'default_host'),
    'user': os.getenv('LOG_DB_USER', 'default_user'),
    'password': os.getenv('LOG_DB_PASSWORD', 'default_password'),
    'database': os.getenv('LOG_DB_NAME', 'default_db')
}

# Токен Telegram-бота
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'default_token')
