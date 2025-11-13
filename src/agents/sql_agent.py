"""
SQL Agent - Self-correcting SQL query generator and executor
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.replicate_llm import ReplicateChatModel
from langchain_core.messages import HumanMessage, SystemMessage
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLAgent:
    def __init__(self, db_manager):
        self.db_manager = db_manager

        # Use Replicate instead of OpenAI
        api_token = os.getenv('REPLICATE_API_TOKEN')
        if not api_token:
            raise ValueError("REPLICATE_API_TOKEN environment variable is not set")

        self.llm = ReplicateChatModel(
            model="openai/gpt-4o-mini",
            temperature=0,
            api_token=api_token
        )
        
        # Get schema information once
        schema_result = db_manager.get_schema_info()
        self.schema = self._format_schema(schema_result)
        
        self.system_prompt = f"""You are an expert PostgreSQL SQL query generator for an e-commerce database.

DATABASE SCHEMA:
{self.schema}

IMPORTANT RULES:
1. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP)
2. Use proper PostgreSQL syntax
3. Always use table aliases for clarity
4. Include LIMIT clause if not specified (default 100)
5. Handle Portuguese column names (product categories are in Portuguese)
6. Use LEFT JOIN when joining product_category_translation for English names
7. Use proper aggregations (COUNT, SUM, AVG) for analytical queries
8. Format currency as R$ (Brazilian Real)

COMMON PATTERNS:
- Top products: SELECT p.product_id, COUNT(*) FROM order_items oi JOIN products p...
- Sales by state: SELECT c.customer_state, SUM(oi.price) FROM customers c JOIN orders o...
- Payment methods: SELECT payment_type, COUNT(*) FROM order_payments...

Generate clean, working SQL queries based on the user's question."""
    
    def _format_schema(self, schema_result):
        """Format schema information for the prompt"""
        if not schema_result['success']:
            return "Schema information not available"
        
        tables = {}
        for row in schema_result['rows']:
            table = row['table_name']
            if table not in tables:
                tables[table] = []
            tables[table].append(f"{row['column_name']} ({row['data_type']})")
        
        schema_text = ""
        for table, columns in tables.items():
            schema_text += f"\n{table}:\n  " + "\n  ".join(columns) + "\n"
        
        return schema_text
    
    def generate_sql(self, question: str) -> str:
        """Generate SQL query from natural language question"""
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Generate a SQL query for: {question}")
        ]
        
        response = self.llm.invoke(messages)
        logger.info(f"LLM response content: {response.content}")
        sql = self._extract_sql(response.content)
        logger.info(f"Final extracted SQL: '{sql}'")
        logger.info(f"SQL length: {len(sql)}, SQL is empty: {not sql.strip()}")
        return sql
    
    def _extract_sql(self, text: str) -> str:
        """Extract SQL query from LLM response"""
        logger.info(f"Raw LLM response: {text}")
        
        # Remove markdown code blocks
        text = re.sub(r'```sql\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Extract SELECT statement
        lines = text.strip().split('\n')
        sql_lines = []
        in_query = False
        
        for line in lines:
            if line.strip().upper().startswith('SELECT'):
                in_query = True
            if in_query:
                sql_lines.append(line)
                if ';' in line:
                    break
        
        sql = '\n'.join(sql_lines).strip()
        
        # Remove trailing semicolon if present
        if sql.endswith(';'):
            sql = sql[:-1]
        
        logger.info(f"Extracted SQL: {sql}")
        
        return sql
    
    def execute_with_correction(self, question: str, max_retries: int = 2):
        """Execute query with self-correction on errors"""
        attempt = 0
        last_error = None
        
        logger.info(f"Processing question: {question}")
        
        while attempt < max_retries:
            # Generate SQL
            if attempt == 0:
                sql = self.generate_sql(question)
            else:
                # Fix the query based on the error
                sql = self._fix_query(sql, last_error, question)
            
            logger.info(f"Attempt {attempt + 1}, SQL to validate: '{sql}'")
            
            # Validate query
            is_valid, validation_msg = self.db_manager.validate_query(sql)
            logger.info(f"Validation result: is_valid={is_valid}, message={validation_msg}")
            
            if not is_valid:
                return {
                    'success': False,
                    'error': validation_msg,
                    'query': sql
                }
            
            # Execute query
            result = self.db_manager.execute_query(sql)
            
            if result['success']:
                result['query'] = sql
                result['attempts'] = attempt + 1
                return result
            
            # Store error for next iteration
            last_error = result['error']
            attempt += 1
        
        return {
            'success': False,
            'error': f"Failed after {max_retries} attempts. Last error: {last_error}",
            'query': sql,
            'attempts': attempt
        }
    
    def _fix_query(self, original_query: str, error: str, question: str) -> str:
        """Fix SQL query based on error message"""
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""The following SQL query for the question "{question}" produced an error:

ORIGINAL QUERY:
{original_query}

ERROR:
{error}

Please fix the query to resolve this error. Return only the corrected SQL query.""")
        ]
        
        response = self.llm.invoke(messages)
        return self._extract_sql(response.content)
