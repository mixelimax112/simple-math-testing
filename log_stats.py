from pymongo import MongoClient
from config import MONGO_CONFIG


def get_mongo_collection():
    """Получить коллекцию MongoDB для логирования"""
    try:
        client = MongoClient(MONGO_CONFIG['host'], MONGO_CONFIG['port'])
        db = client[MONGO_CONFIG['database']]
        collection = db[MONGO_CONFIG['collection']]
        return collection
    except Exception as e:
        print(f"Ошибка подключения к MongoDB: {e}")
        return None


def get_popular_searches(limit=5):
    """Получить топ популярных запросов по частоте"""
    collection = get_mongo_collection()
    if not collection:
        return []

    try:
        pipeline = [
            {
                '$group': {
                    '_id': {
                        'search_type': '$search_type',
                        'params': '$params'
                    },
                    'count': {'$sum': 1},
                    'last_search': {'$max': '$timestamp'}
                }
            },
            {
                '$sort': {'count': -1, 'last_search': -1}
            },
            {
                '$limit': limit
            }
        ]

        results = list(collection.aggregate(pipeline))
        return results
    except Exception as e:
        print(f"Ошибка получения статистики: {e}")
        return []


def get_recent_searches(limit=5):
    """Получить последние уникальные запросы"""
    collection = get_mongo_collection()
    if not collection:
        return []

    try:
        pipeline = [
            {
                '$sort': {'timestamp': -1}
            },
            {
                '$group': {
                    '_id': {
                        'search_type': '$search_type',
                        'params': '$params'
                    },
                    'last_search': {'$first': '$timestamp'},
                    'results_count': {'$first': '$results_count'}
                }
            },
            {
                '$sort': {'last_search': -1}
            },
            {
                '$limit': limit
            }
        ]

        results = list(collection.aggregate(pipeline))
        return results
    except Exception as e:
        print(f"Ошибка получения последних запросов: {e}")
        return []
