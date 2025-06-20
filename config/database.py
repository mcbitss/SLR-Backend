"""
Simple Database Configuration
"""
import os

class DatabaseConfig:
    """Simple database configuration"""
    
    # Database connection settings
    HOST = os.getenv("DB_HOST", "localhost")
    PORT = int(os.getenv("DB_PORT", 5432))
    USER = os.getenv("DB_USER", "sathyan")
    PASSWORD = os.getenv("DB_PASSWORD", "kiki8305")
    DATABASE = os.getenv("DB_NAME", "openalex_db")
    
    # Table settings
    TABLE = os.getenv("DB_TABLE", "ibd_rcts")
    
    def get_psycopg2_params(self):
        """Get psycopg2 connection parameters"""
        return {
            'host': self.HOST,
            'port': self.PORT,
            'user': self.USER,
            'password': self.PASSWORD,
            'database': self.DATABASE
        }