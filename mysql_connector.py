import pymysql
from config import MYSQL_CONFIG, RESULTS_PER_PAGE


def get_connection():
    """Создание подключения к MySQL базе данных sakila"""
    try:
        connection = pymysql.connect(**MYSQL_CONFIG)
        return connection
    except pymysql.Error as e:
        print(f"Ошибка подключения к MySQL: {e}")
        return None


def search_by_keyword(keyword, offset=0):
    """Поиск фильмов по ключевому слову в названии"""
    connection = get_connection()
    if not connection:
        return []

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
                SELECT f.film_id, f.title, f.release_year, f.rating, f.length,
                       GROUP_CONCAT(DISTINCT c.name ORDER BY c.name SEPARATOR ', ') as genres
                FROM film f
                LEFT JOIN film_category fc ON f.film_id = fc.film_id
                LEFT JOIN category c ON fc.category_id = c.category_id
                WHERE f.title LIKE %s
                GROUP BY f.film_id, f.title, f.release_year, f.rating, f.length
                ORDER BY f.title
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (f'%{keyword}%', RESULTS_PER_PAGE, offset))
            results = cursor.fetchall()
            return results
    except pymysql.Error as e:
        print(f"Ошибка выполнения запроса: {e}")
        return []
    finally:
        connection.close()


def get_all_genres():
    """Получить список всех жанров"""
    connection = get_connection()
    if not connection:
        return []

    try:
        with connection.cursor() as cursor:
            query = "SELECT name FROM category ORDER BY name"
            cursor.execute(query)
            results = cursor.fetchall()
            return [row[0] for row in results]
    except pymysql.Error as e:
        print(f"Ошибка получения жанров: {e}")
        return []
    finally:
        connection.close()


def get_year_range():
    """Получить минимальный и максимальный год выпуска фильмов"""
    connection = get_connection()
    if not connection:
        return None, None

    try:
        with connection.cursor() as cursor:
            query = "SELECT MIN(release_year) as min_year, MAX(release_year) as max_year FROM film"
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0], result[1]
    except pymysql.Error as e:
        print(f"Ошибка получения диапазона годов: {e}")
        return None, None
    finally:
        connection.close()


def search_by_genre_and_year(genre, year_from, year_to, offset=0):
    """Поиск фильмов по жанру и диапазону годов"""
    connection = get_connection()
    if not connection:
        return []

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
                SELECT f.film_id, f.title, f.release_year, f.rating, f.length,
                       GROUP_CONCAT(DISTINCT c.name ORDER BY c.name SEPARATOR ', ') as genres
                FROM film f
                LEFT JOIN film_category fc ON f.film_id = fc.film_id
                LEFT JOIN category c ON fc.category_id = c.category_id
                WHERE c.name = %s
                  AND f.release_year BETWEEN %s AND %s
                GROUP BY f.film_id, f.title, f.release_year, f.rating, f.length
                ORDER BY f.release_year DESC, f.title
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (genre, year_from, year_to, RESULTS_PER_PAGE, offset))
            results = cursor.fetchall()
            return results
    except pymysql.Error as e:
        print(f"Ошибка выполнения запроса: {e}")
        return []
    finally:
        connection.close()
