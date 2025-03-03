from database import get_db_connection, save_query_to_log, get_top_frequent_queries
from config import FILM_DB_CONFIG

# Поиск по названию
def search_by_title():
    search_value = input("Введите ключевое слово для поиска в названии фильма: ")

    connection = get_db_connection(FILM_DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT title FROM film WHERE title LIKE %s", (f"%{search_value}%",))
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    if results:
        print(f"\nРезультаты поиска по ключевому слову '{search_value}' в названии фильма:")
        for row in results:
            print(row[0])
    else:
        print("\nНичего не найдено.")

    # Сохраняем запрос в лог, независимо от того, найдены ли результаты
    save_query_to_log(f"Поиск по названию: {search_value}")

# Поиск по жанру и году
def search_by_genre_and_year():
    genre = input("Введите жанр фильма: ")
    year = input("Введите год выпуска фильма: ")

    try:
        year = int(year)
        connection = get_db_connection(FILM_DB_CONFIG)
        cursor = connection.cursor()

        # Запрашиваем фильмы по жанру и году
        cursor.execute("""
            SELECT f.title 
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            WHERE c.name LIKE %s AND f.release_year = %s
        """, (f"%{genre}%", year))

        results = cursor.fetchall()

        if results:
            print(f"\nРезультаты поиска по жанру '{genre}' и году выпуска '{year}':")
            for row in results:
                print(row[0])  # Выводим название фильма
        else:
            print("\nНичего не найдено.")

        # Сохраняем запрос в лог
        save_query_to_log(f"Жанр: {genre}, Год: {year}")
        connection.close()

    except ValueError:
        print("Год должен быть числом. Попробуйте снова.")
        search_by_genre_and_year()

# Основная функция
def main():
    while True:
        print("\nВыберите вариант поиска:")
        print("1. Поиск по ключевому слову из названия фильма.")
        print("2. Поиск по жанру и году выпуска.")
        print("3. Показать ТОП-10 запросов.")
        print("4. Выход из программы.")

        search_option = input("\nВведите номер варианта (1, 2, 3 или 4): ")

        if search_option == "1":
            search_by_title()

        elif search_option == "2":
            search_by_genre_and_year()

        elif search_option == "3":
            top_queries = get_top_frequent_queries()
            if top_queries:
                print("\nТоп-10 самых частых запросов:")
                for i, (query, count) in enumerate(top_queries, 1):
                    print(f"{i}. '{query}' – {count} раз(а).")
            else:
                print("\nЗапросы не найдены.")

        elif search_option == "4":
            print("Выход  из программы...")
            break

        else:
            print("Неверный выбор варианта поиска!")

if __name__ == "__main__":
    main()