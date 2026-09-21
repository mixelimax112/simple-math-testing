import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MySQL configuration
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'sakila'),
    'charset': os.getenv('MYSQL_CHARSET', 'utf8mb4')
}

# MongoDB configuration
MONGO_CONFIG = {
    'host': os.getenv('MONGO_HOST', 'localhost'),
    'port': int(os.getenv('MONGO_PORT', 27017)),
    'database': os.getenv('MONGO_DATABASE', 'movie_search'),
    'collection': os.getenv('MONGO_COLLECTION', 'final_project_121225-ptm_maxim_kravchenko')
}

# Pagination settings
RESULTS_PER_PAGE = 10
