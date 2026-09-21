from pymongo import MongoClient
from datetime import datetime
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


def log_search(search_type, params, results_count):
    """Логирование поискового запроса в MongoDB"""
    collection = get_mongo_collection()
    if not collection:
        return False

    try:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'search_type': search_type,
            'params': params,
            'results_count': results_count
        }
        collection.insert_one(log_entry)
        return True
    except Exception as e:
        print(f"Ошибка записи в MongoDB: {e}")
        return False
