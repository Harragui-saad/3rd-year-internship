from typing import Dict, Any
from .base import DatabaseInterface
from .sqlite_db import SQLiteDatabase
from .mongodb_db import MongoDBDatabase
from config import DATABASE_CONFIG

class DatabaseFactory:
    """Factory class for creating database instances"""
    
    @staticmethod
    def create_database(db_type: str, **kwargs) -> DatabaseInterface:
        """
        Create a database instance based on type
        
        Args:
            db_type: Type of database ('sqlite', 'mongodb', 'mysql', 'postgresql')
            **kwargs: Additional configuration parameters
            
        Returns:
            DatabaseInterface: Database instance
        """
        if db_type == 'sqlite':
            config = DATABASE_CONFIG['sqlite']
            return SQLiteDatabase(config['path'])
        
        elif db_type == 'mongodb':
            config = DATABASE_CONFIG['mongodb']
            host = kwargs.get('host', config['host'])
            port = kwargs.get('port', config['port'])
            database = kwargs.get('database', config['database'])
            return MongoDBDatabase(host, port, database)
        
        elif db_type == 'mysql':
            # MySQL implementation would go here
            raise NotImplementedError("MySQL database not yet implemented")
        
        elif db_type == 'postgresql':
            # PostgreSQL implementation would go here
            raise NotImplementedError("PostgreSQL database not yet implemented")
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    @staticmethod
    def get_available_types() -> list:
        """Get list of available database types"""
        return ['sqlite', 'mongodb', 'mysql', 'postgresql']
    
    @staticmethod
    def get_default_config(db_type: str) -> Dict[str, Any]:
        """Get default configuration for a database type"""
        if db_type in DATABASE_CONFIG:
            return DATABASE_CONFIG[db_type].copy()
        else:
            raise ValueError(f"Unknown database type: {db_type}")



