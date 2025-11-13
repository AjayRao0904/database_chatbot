"""
Database utility for connecting to PostgreSQL and executing queries
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'olist_ecommerce'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
        
        conn_string = f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
        self.engine = create_engine(conn_string)
    
    def execute_query(self, query: str):
        """Execute a SQL query and return results"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                
                # Get column names
                columns = result.keys() if hasattr(result, 'keys') else []
                
                # Fetch all rows
                rows = result.fetchall()
                
                return {
                    'success': True,
                    'columns': list(columns),
                    'rows': [dict(zip(columns, row)) for row in rows],
                    'row_count': len(rows)
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def get_schema_info(self):
        """Get database schema information"""
        query = """
            SELECT 
                table_name,
                column_name,
                data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """
        return self.execute_query(query)
    
    def validate_query(self, query: str):
        """Basic SQL query validation"""
        if not query or not query.strip():
            logger.warning(f"Empty query received")
            return False, "Query is empty"
        
        query_lower = query.lower().strip()
        logger.info(f"Validating query (first 200 chars): {query_lower[:200]}")
        
        # Block dangerous operations
        dangerous_keywords = ['drop', 'delete', 'truncate', 'alter', 'create', 'insert', 'update']
        for keyword in dangerous_keywords:
            if keyword in query_lower:
                logger.warning(f"Found dangerous keyword: {keyword}")
                return False, f"Query contains forbidden keyword: {keyword}"
        
        # Must be a SELECT query
        if not query_lower.startswith('select'):
            logger.warning(f"Query doesn't start with SELECT. Full query: '{query}'")
            return False, "Only SELECT queries are allowed"
        
        logger.info(f"Query validation passed")
        return True, "Query is valid"
