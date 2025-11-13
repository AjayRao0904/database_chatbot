"""
Proactive Insight Agent - Finds patterns and generates insights automatically
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.replicate_llm import ReplicateChatModel
from langchain_core.messages import HumanMessage, SystemMessage

class ProactiveInsightAgent:
    def __init__(self, db_manager):
        self.db_manager = db_manager

        # Use Replicate instead of OpenAI
        api_token = os.getenv('REPLICATE_API_TOKEN')
        if not api_token:
            raise ValueError("REPLICATE_API_TOKEN environment variable is not set")

        self.llm = ReplicateChatModel(
            model="openai/gpt-4o-mini",
            temperature=0.7,
            api_token=api_token
        )
    
    def generate_insights(self, query_result: dict, original_question: str):
        """Generate proactive insights from query results"""
        
        if not query_result.get('success') or not query_result.get('rows'):
            return None
        
        # Analyze the data for patterns
        insights = []
        
        # Check for correlations
        correlation_insight = self._find_correlations(query_result)
        if correlation_insight:
            insights.append(correlation_insight)
        
        # Generate AI-powered insight
        ai_insight = self._generate_ai_insight(query_result, original_question)
        if ai_insight:
            insights.append(ai_insight)
        
        return insights
    
    def _find_correlations(self, result: dict):
        """Find interesting correlations in the data"""
        rows = result['rows']
        
        if len(rows) < 2:
            return None
        
        # Look for patterns
        insights = []
        
        # Check for concentration (e.g., 80/20 rule)
        if len(rows) >= 5:
            # Calculate percentage of first item vs total
            first_row = rows[0]
            
            # Find numeric columns
            numeric_cols = [k for k, v in first_row.items() if isinstance(v, (int, float))]
            
            for col in numeric_cols:
                total = sum(row.get(col, 0) for row in rows)
                if total > 0:
                    top_pct = (first_row.get(col, 0) / total) * 100
                    
                    if top_pct > 30:  # Significant concentration
                        label_col = [k for k in first_row.keys() if k != col][0]
                        return {
                            'type': 'concentration',
                            'insight': f"⚡ **Concentration Alert**: {first_row[label_col]} accounts for {top_pct:.1f}% of total {col}. This suggests high dependency on a single segment.",
                            'recommendation': f"Consider diversifying to reduce risk associated with over-reliance on {first_row[label_col]}."
                        }
        
        return None
    
    def _generate_ai_insight(self, result: dict, question: str):
        """Use AI to generate deeper insights"""
        
        # Prepare data summary
        data_summary = self._summarize_data(result)
        
        system_prompt = """You are a business intelligence analyst for an e-commerce platform.
Your job is to find ONE interesting, actionable insight from data that the user didn't explicitly ask for.

The insight should:
1. Be genuinely interesting and surprising
2. Suggest a specific business action
3. Be concise (2-3 sentences max)
4. Start with an emoji that fits the insight

Focus on: patterns, outliers, opportunities, or risks."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""The user asked: "{question}"

Here's the data:
{data_summary}

What's ONE interesting proactive insight you notice?""")
        ]
        
        try:
            response = self.llm.invoke(messages)
            
            return {
                'type': 'ai_generated',
                'insight': response.content.strip(),
                'recommendation': ''
            }
        except:
            return None
    
    def _summarize_data(self, result: dict):
        """Create a concise summary of the data"""
        rows = result['rows']
        
        if len(rows) > 5:
            summary_rows = rows[:5]
            summary = f"Top 5 results (out of {len(rows)} total):\n"
        else:
            summary_rows = rows
            summary = f"All {len(rows)} results:\n"
        
        for i, row in enumerate(summary_rows, 1):
            row_str = ", ".join(f"{k}: {v}" for k, v in row.items())
            summary += f"{i}. {row_str}\n"
        
        return summary
