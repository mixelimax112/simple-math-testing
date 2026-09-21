from tabulate import tabulate


def format_movies(movies):
    """Форматирование списка фильмов в виде таблицы"""
    if not movies:
        return "Фильмы не найдены."

    headers = ["ID", "Название", "Год", "Рейтинг", "Длительность (мин)", "Жанры"]
    table_data = []

    for movie in movies:
        table_data.append([
            movie.get('film_id', 'N/A'),
            movie.get('title', 'N/A'),
            movie.get('release_year', 'N/A'),
            movie.get('rating', 'N/A'),
            movie.get('length', 'N/A'),
            movie.get('genres', 'N/A')
        ])

    return tabulate(table_data, headers=headers, tablefmt="grid")


def format_popular_searches(searches):
    """Форматирование популярных запросов"""
    if not searches:
        return "История запросов пуста."

    output = "\n=== ТОП-5 ПОПУЛЯРНЫХ ЗАПРОСОВ ===\n"

    for idx, search in enumerate(searches, 1):
        search_type = search['_id']['search_type']
        params = search['_id']['params']
        count = search['count']

        output += f"\n{idx}. Тип: {search_type} | Количество запросов: {count}\n"
        output += f"   Параметры: {format_params(params)}\n"

    return output


def format_recent_searches(searches):
    """Форматирование последних запросов"""
    if not searches:
        return "История запросов пуста."

    output = "\n=== ПОСЛЕДНИЕ 5 ЗАПРОСОВ ===\n"

    for idx, search in enumerate(searches, 1):
        search_type = search['_id']['search_type']
        params = search['_id']['params']
        timestamp = search['last_search']
        results_count = search.get('results_count', 0)

        output += f"\n{idx}. Тип: {search_type} | Время: {timestamp}\n"
        output += f"   Параметры: {format_params(params)}\n"
        output += f"   Найдено результатов: {results_count}\n"

    return output


def format_params(params):
    """Форматирование параметров запроса"""
    if not params:
        return "N/A"

    param_str = ", ".join([f"{k}: {v}" for k, v in params.items()])
    return param_str


def format_genres(genres):
    """Форматирование списка жанров"""
    if not genres:
        return "Жанры не найдены."

    output = "\n=== ДОСТУПНЫЕ ЖАНРЫ ===\n"
    for idx, genre in enumerate(genres, 1):
        output += f"{idx}. {genre}\n"

    return output
