import mysql.connector
from config import FILM_DB_CONFIG, LOG_DB_CONFIG

# Функция для подключения к базе данных
def get_db_connection(db_config):
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return None

# Функция для создания таблицы логов запросов
def init_log_table():
    connection = get_db_connection(LOG_DB_CONFIG)
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alex_search_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        query VARCHAR(255) UNIQUE,
        count INT DEFAULT 1
    )
    """)
    connection.commit()
    cursor.close()
    connection.close()

# Функция для получения топ-10 наиболее частых запросов
def get_top_frequent_queries():
    connection = get_db_connection(LOG_DB_CONFIG)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT query, count 
        FROM alex_search_logs 
        ORDER BY count DESC 
        LIMIT 10
    """)

    top_queries = cursor.fetchall()
    cursor.close()
    connection.close()

    return top_queries  # Возвращаем список ТОП-10 запросов

# Функция для получения всех жанров
def get_all_genres():
    connection = get_db_connection(FILM_DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT name FROM category")  # Таблица жанров
    genres = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return genres

# Функция для получения всех годов
def get_all_years():
    connection = get_db_connection(FILM_DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT release_year FROM film ORDER BY release_year DESC")  # Таблица фильмов
    years = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return years

# Функция для сохранения запроса в лог
def save_query_to_log(query, genre=None, year=None):
    connection = get_db_connection(LOG_DB_CONFIG)
    cursor = connection.cursor()

    # Формируем запрос в зависимости от наличия жанра и года
    if genre and year:
        query = f"Жанр: {genre}, Год: {year}"

    # Проверка, существует ли уже такой запрос в таблице
    cursor.execute("SELECT count FROM alex_search_logs WHERE query = %s", (query,))
    result = cursor.fetchone()

    if result:
        # Если запрос уже существует, увеличиваем счетчик
        cursor.execute("""
            UPDATE alex_search_logs
            SET count = count + 1
            WHERE query = %s
        """, (query,))
    else:
        # Если запрос новый, добавляем его в таблицу с начальным значением счетчика 1
        cursor.execute("""
            INSERT INTO alex_search_logs (query, count) 
            VALUES (%s, 1)
        """, (query,))

    connection.commit()
    cursor.close()
    connection.close()

# Инициализация таблицы для логов
init_log_table()