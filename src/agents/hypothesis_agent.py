"""
Hypothesis Generation Agent - Analyzes "why" questions and generates theories
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.replicate_llm import ReplicateChatModel
from langchain_core.messages import HumanMessage, SystemMessage

class HypothesisAgent:
    def __init__(self, db_manager, sql_agent):
        self.db_manager = db_manager
        self.sql_agent = sql_agent

        # Use Replicate instead of OpenAI
        api_token = os.getenv('REPLICATE_API_TOKEN')
        if not api_token:
            raise ValueError("REPLICATE_API_TOKEN environment variable is not set")

        self.llm = ReplicateChatModel(
            model="openai/gpt-4o-mini",
            temperature=0.7,
            api_token=api_token
        )
    
    def generate_hypotheses(self, question: str, data: dict = None):
        """Generate hypotheses for analytical questions"""
        
        # First, gather relevant data if not provided
        if not data:
            data = self._gather_context(question)
        
        system_prompt = """You are an analytical expert for an e-commerce business in Brazil.
Your job is to analyze data and generate 3 possible hypotheses to explain patterns or answer "why" questions.

For each hypothesis:
1. Provide a clear explanation
2. Suggest what data would support or refute it
3. Recommend next steps for investigation

Be specific to e-commerce, Brazilian market, and the Olist platform context."""
        
        data_summary = self._format_data_summary(data) if data else "No data available"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""Question: {question}

Available Data:
{data_summary}

Generate 3 distinct hypotheses to answer this question.""")
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            'question': question,
            'hypotheses': self._parse_hypotheses(response.content),
            'data_used': data_summary
        }
    
    def _gather_context(self, question: str):
        """Gather relevant data for hypothesis generation"""
        # Extract key entities from question
        question_lower = question.lower()
        
        queries = []
        
        if 'sales' in question_lower or 'revenue' in question_lower:
            queries.append("""
                SELECT 
                    c.customer_state,
                    COUNT(DISTINCT o.order_id) as orders,
                    SUM(oi.price) as revenue
                FROM customers c
                JOIN orders o ON c.customer_id = o.customer_id
                JOIN order_items oi ON o.order_id = oi.order_id
                GROUP BY c.customer_state
                ORDER BY revenue DESC
                LIMIT 10
            """)
        
        if 'category' in question_lower or 'product' in question_lower:
            queries.append("""
                SELECT 
                    COALESCE(t.product_category_name_english, p.product_category_name) as category,
                    COUNT(*) as items_sold,
                    AVG(oi.price) as avg_price
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                LEFT JOIN product_category_translation t ON p.product_category_name = t.product_category_name
                GROUP BY category
                ORDER BY items_sold DESC
                LIMIT 10
            """)
        
        results = []
        for query in queries:
            result = self.db_manager.execute_query(query)
            if result['success']:
                results.append(result)
        
        return results
    
    def _format_data_summary(self, data):
        """Format data results into readable summary"""
        if not data:
            return "No data available"
        
        summary = []
        for result in data:
            if result.get('success') and result.get('rows'):
                summary.append(f"Found {len(result['rows'])} records")
                # Add top 3 rows
                for i, row in enumerate(result['rows'][:3]):
                    summary.append(f"  {i+1}. {row}")
        
        return "\n".join(summary)
    
    def _parse_hypotheses(self, content: str):
        """Parse LLM response into structured hypotheses"""
        # Simple parsing - split by numbered items
        lines = content.split('\n')
        hypotheses = []
        current = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if it's a hypothesis header (starts with number)
            if line[0].isdigit() and ('. ' in line or ') ' in line):
                if current:
                    hypotheses.append(current)
                current = line
            elif current:
                current += " " + line
        
        if current:
            hypotheses.append(current)
        
        return hypotheses[:3] if len(hypotheses) >= 3 else [content]
