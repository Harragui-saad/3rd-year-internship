import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_CONFIG = {
    'sqlite': {
        'type': 'sqlite',
        'path': 'warehouse.db'
    },
    'mysql': {
        'type': 'mysql',
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'database': os.getenv('MYSQL_DB', 'warehouse'),
        'username': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', '')
    },
    'postgresql': {
        'type': 'postgresql',
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'database': os.getenv('POSTGRES_DB', 'warehouse'),
        'username': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', '')
    },
    'mongodb': {
        'type': 'mongodb',
        'host': os.getenv('MONGO_HOST', 'localhost'),
        'port': int(os.getenv('MONGO_PORT', 27017)),
        'database': os.getenv('MONGO_DB', 'warehouse')
    }
}

# Warehouse Configuration
WAREHOUSE_CONFIG = {
    'zones': ['Zone1', 'Zone2', 'Zone3', 'Zone4', 'Zone5'],
    'max_products_per_zone': 1000,
    'priority_levels': ['urgent', 'normal', 'low'],
    'optimization_timeout': 2.0,  # seconds
    'report_path': 'reports/'
}

# Q-Learning Configuration
QL_CONFIG = {
    'learning_rate': 0.1,
    'discount_factor': 0.9,
    'epsilon': 0.1,
    'max_iterations': 1000
}



