import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_db_connection, save_query_to_log, get_all_genres, get_all_years, get_top_frequent_queries
from config import FILM_DB_CONFIG, LOG_DB_CONFIG, TELEGRAM_BOT_TOKEN
import time
import requests.exceptions

# Создаем бота
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Главное меню с кнопками
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    markup.add(KeyboardButton("🔍 Поиск по названию"), KeyboardButton("🎭 Поиск по жанру и году"))
    markup.add(KeyboardButton("📊 Топ-10 запросов"), KeyboardButton("👋 Выход"))
    return markup

# Инлайн-кнопка "Начать"
def start_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🚀 Начать", callback_data="start_menu"))
    return markup

# Отправка закрепленного сообщения
@bot.message_handler(commands=['start'])
def start(message):
    pinned_msg = bot.send_message(message.chat.id, "Привет! Я бот для поиска фильмов 🎬\n"
                                                   "Нажми 'Начать', чтобы открыть меню:",
                                  reply_markup=start_button())
    try:
        bot.pin_chat_message(message.chat.id, pinned_msg.message_id)
    except Exception as e:
        print(f"Ошибка закрепления: {e}")

# Обработчик нажатия на "Начать"
@bot.callback_query_handler(func=lambda call: call.data == "start_menu")
def show_main_menu(call):
    bot.send_message(call.message.chat.id, "Выбери действие из меню:", reply_markup=main_menu())

# Топ-10 частых запросов
def send_top_queries(message):
    try:
        top_queries = get_top_frequent_queries()
        if top_queries:
            print("\nТоп-10 самых частых запросов:")
            for i, (query, count) in enumerate(top_queries, 1):
                print(f"{i}. '{query}' – {count} раз(а).")
        else:
            print("\nЗапросы не найдены.")

        if top_queries:
            response = "📊 Топ-10 популярных запросов:\n"
            for i, (query, count) in enumerate(top_queries, 1):
                response += f"{i}. {query} – {count} раз(а)\n"
        else:
            response = "❌ Запросов пока нет."

        send_message_in_chunks(message.chat.id, response)
        bot.send_message(message.chat.id, "Что еще хотите сделать?", reply_markup=main_menu())
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Произошла ошибка при получении топ-10 запросов.")
        print(f"Ошибка: {e}")

# Обработчик кнопок меню
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if message.text == "🔍 Поиск по названию":
        bot.send_message(message.chat.id, "Введите ключевое слово из названия фильма:")
        bot.register_next_step_handler(message, search_by_title)
    elif message.text == "🎭 Поиск по жанру и году":
        choose_genre(message)
    elif message.text == "📊 Топ-10 запросов":
        send_top_queries(message)
    elif message.text == "👋 Выход":
        bot.send_message(message.chat.id, "👋 Бот завершает работу. До встречи! 👋",
                         reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, "👋 Я не понимаю эту команду. Выбери из меню.", reply_markup=main_menu())

# Поиск по названию фильма
def search_by_title(message):
    try:
        keyword = message.text
        connection = get_db_connection(FILM_DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("SELECT title FROM film WHERE title LIKE %s", (f"%{keyword}%",))
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        if results:
            response = "🎬 Найденные фильмы:\n" + "\n".join([f"- {row[0]}" for row in results])
        else:
            response = "❌ Ничего не найдено."

        save_query_to_log(f"Поиск по названию: {keyword}")
        send_message_in_chunks(message.chat.id, response)

    except Exception as e:
        bot.send_message(message.chat.id, "❌ Произошла ошибка при выполнении запроса.")
        print(f"Ошибка: {e}")

    bot.send_message(message.chat.id, "Что еще хотите сделать?", reply_markup=main_menu())

# Выбор жанра
def choose_genre(message):
    genres = get_all_genres()
    if not genres:
        bot.send_message(message.chat.id, "❌ Жанры не найдены в базе.")
        return

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for genre in genres:
        markup.add(KeyboardButton(genre))

    bot.send_message(message.chat.id, "Выберите жанр из списка:", reply_markup=markup)
    bot.register_next_step_handler(message, choose_year)

# Выбор года
def choose_year(message):
    genre = message.text
    years = sorted(get_all_years(), reverse=True)[:35]

    if not years:
        bot.send_message(message.chat.id, "❌ Годы не найдены в базе.")
        return

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for year in years:
        markup.add(KeyboardButton(str(year)))

    bot.send_message(message.chat.id, "Выберите год выпуска фильма:", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: search_by_genre_and_year(msg, genre))

# Поиск по жанру и году
def search_by_genre_and_year(message, genre):
    try:
        year = int(message.text)
        connection = get_db_connection(FILM_DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT f.title FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            WHERE c.name LIKE %s AND f.release_year = %s
        """, (f"%{genre}%", year))
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        if results:
            response = f"🎭 Фильмы в жанре '{genre}' за {year} год:\n" + "\n".join([f"- {row[0]}" for row in results])
        else:
            response = "❌ Ничего не найдено."

        save_query_to_log(f"Жанр: {genre}, Год: {year}")
        send_message_in_chunks(message.chat.id, response)

    except ValueError:
        bot.send_message(message.chat.id, "❌ Год должен быть числом. Попробуйте снова.")
        bot.register_next_step_handler(message, lambda msg: search_by_genre_and_year(msg, genre))

    bot.send_message(message.chat.id, "Что еще хотите сделать?", reply_markup=main_menu())

# Функция для отправки длинных сообщений
def send_message_in_chunks(chat_id, message):
    max_length = 4000
    while len(message) > max_length:
        bot.send_message(chat_id, message[:max_length])
        message = message[max_length:]
    if message:
        bot.send_message(chat_id, message)

# Перезапуск чатбота при разрыве соединения
while True:
    try:
        bot.polling(none_stop=True, timeout=60)
    except requests.exceptions.ReadTimeout:
        print("⚠️ Telegram API не отвечает, пытаемся переподключиться...")
        time.sleep(5)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)