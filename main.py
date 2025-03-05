from database import get_db_connection, save_query_to_log, get_top_frequent_queries
from config import FILM_DB_CONFIG


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


# Поиск по названию
def search_by_title():
    search_value = input("Введите ключевое слово для поиска в названии фильма: ")

    connection = get_db_connection(FILM_DB_CONFIG)
    cursor = connection.cursor()

    # Поиск по названию фильма
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

    save_query_to_log(f"Поиск по названию: {search_value}")


# Поиск по жанру и году
def search_by_genre_and_year():
    genres = get_all_genres()
    years = get_all_years()

    print("\nДоступные жанры:")
    print(", ".join(genres))
    genre = input("\nВведите жанр фильма: ")

    print("\nДоступные года выпуска:")
    print(", ".join(map(str, years)))

    while True:
        year = input("\nВведите год выпуска фильма (четыре цифры, например, 2020): ")
        if year.isdigit() and len(year) == 4:
            year = int(year)
            break
        else:
            print("Ошибка: Год должен быть четырёхзначным числом!")

    try:
        connection = get_db_connection(FILM_DB_CONFIG)
        cursor = connection.cursor()

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
                print(row[0])
        else:
            print("\nНичего не найдено.")

        save_query_to_log(f"Поиск по жанру: {genre}, год: {year}")

        cursor.close()
        connection.close()

    except ValueError:
        print("Год должен быть числом. Попробуй снова.")
        search_by_genre_and_year()


# Основное меню
def main():
    while True:
        print("\nВыберите вариант поиска:")
        print("1. Поиск по названию фильма.")
        print("2. Поиск по жанру и году выпуска.")
        print("3. Показать ТОП-10 запросов.")
        print("4. Выход из программы.")

        choice = input("\nВведите номер варианта (1-4): ")

        if choice == "1":
            search_by_title()
        elif choice == "2":
            search_by_genre_and_year()
        elif choice == "3":
            top_queries = get_top_frequent_queries()
            if top_queries:
                print("\nТоп-10 самых частых запросов:")
                for i, (query_text, count_query) in enumerate(top_queries, 1):
                    print(f"{i}. '{query_text}' – {count_query} раз(а).")
            else:
                print("\nЗапросы не найдены.")
        elif choice == "4":
            print("Выход из программы...")
            break
        else:
            print("Неверный выбор! Попробуйте снова.")


if __name__ == "__main__":
    main()

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
                for i, (query_text, count_query) in enumerate(top_queries, 1):
                    print(f"{i}. '{query_text}' – {count_query} раз(а).")
            else:
                print("\nЗапросы не найдены.")

        elif search_option == "4":
            print("Выход  из программы...")
            break

        else:
            print("Неверный выбор варианта поиска!")

if __name__ == "__main__":
    main()