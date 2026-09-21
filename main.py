import sys
from mysql_connector import search_by_keyword, search_by_genre_and_year, get_all_genres, get_year_range
from log_writer import log_search
from log_stats import get_popular_searches, get_recent_searches
from formatter import format_movies, format_popular_searches, format_recent_searches, format_genres


def print_menu():
    """Вывод главного меню"""
    print("\n" + "="*60)
    print("  ПОИСК ФИЛЬМОВ В БАЗЕ ДАННЫХ SAKILA")
    print("="*60)
    print("\n1. Поиск по ключевому слову")
    print("2. Поиск по жанру и диапазону годов")
    print("3. Показать популярные запросы")
    print("4. Показать последние запросы")
    print("5. Выход")
    print("="*60)


def search_keyword_menu():
    """Меню поиска по ключевому слову"""
    keyword = input("\nВведите ключевое слово для поиска: ").strip()

    if not keyword:
        print("Ошибка: ключевое слово не может быть пустым.")
        return

    offset = 0
    total_shown = 0

    while True:
        results = search_by_keyword(keyword, offset)

        if not results:
            if offset == 0:
                print("\nФильмы не найдены.")
            else:
                print("\nБольше результатов нет.")
            break

        print(f"\n--- Результаты {offset + 1}-{offset + len(results)} ---")
        print(format_movies(results))

        total_shown += len(results)
        offset += len(results)

        if len(results) < 10:
            print("\nБольше результатов нет.")
            break

        choice = input("\nПоказать следующие 10 результатов? (y/n): ").strip().lower()
        if choice != 'y':
            break

    log_search('keyword', {'keyword': keyword}, total_shown)
    print(f"\nВсего найдено и показано: {total_shown} фильм(ов)")


def search_genre_year_menu():
    """Меню поиска по жанру и годам"""
    genres = get_all_genres()

    if not genres:
        print("Ошибка: не удалось загрузить жанры.")
        return

    print(format_genres(genres))

    min_year, max_year = get_year_range()
    if min_year and max_year:
        print(f"\nДиапазон годов в базе данных: {min_year} - {max_year}")

    genre = input("\nВведите название жанра: ").strip()

    if genre not in genres:
        print(f"Ошибка: жанр '{genre}' не найден в списке доступных жанров.")
        return

    try:
        year_from = int(input("Введите год ОТ: ").strip())
        year_to = int(input("Введите год ДО: ").strip())

        if year_from > year_to:
            print("Ошибка: начальный год не может быть больше конечного.")
            return

    except ValueError:
        print("Ошибка: год должен быть числом.")
        return

    offset = 0
    total_shown = 0

    while True:
        results = search_by_genre_and_year(genre, year_from, year_to, offset)

        if not results:
            if offset == 0:
                print("\nФильмы не найдены.")
            else:
                print("\nБольше результатов нет.")
            break

        print(f"\n--- Результаты {offset + 1}-{offset + len(results)} ---")
        print(format_movies(results))

        total_shown += len(results)
        offset += len(results)

        if len(results) < 10:
            print("\nБольше результатов нет.")
            break

        choice = input("\nПоказать следующие 10 результатов? (y/n): ").strip().lower()
        if choice != 'y':
            break

    log_search('genre_year', {'genre': genre, 'year_from': year_from, 'year_to': year_to}, total_shown)
    print(f"\nВсего найдено и показано: {total_shown} фильм(ов)")


def show_popular_searches():
    """Показать популярные запросы"""
    searches = get_popular_searches(5)
    print(format_popular_searches(searches))


def show_recent_searches():
    """Показать последние запросы"""
    searches = get_recent_searches(5)
    print(format_recent_searches(searches))


def main():
    """Главная функция приложения"""
    print("\nДобро пожаловать в систему поиска фильмов!")

    while True:
        print_menu()

        try:
            choice = input("\nВыберите действие (1-5): ").strip()

            if choice == '1':
                search_keyword_menu()
            elif choice == '2':
                search_genre_year_menu()
            elif choice == '3':
                show_popular_searches()
            elif choice == '4':
                show_recent_searches()
            elif choice == '5':
                print("\nСпасибо за использование системы поиска фильмов!")
                sys.exit(0)
            else:
                print("\nОшибка: выберите действие от 1 до 5.")

        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем.")
            sys.exit(0)
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")
            print("Попробуйте еще раз.")

        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()
