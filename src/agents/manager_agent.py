"""
Manager Agent - Orchestrates all worker agents using LangGraph
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.replicate_llm import ReplicateChatModel
from langchain_core.messages import HumanMessage, SystemMessage
import operator

class AgentState(TypedDict):
    """State shared across all agents"""
    messages: Annotated[Sequence[str], operator.add]
    question: str
    query_type: str  # 'data', 'analysis', 'hypothesis'
    sql_result: dict
    hypotheses: list
    insights: list
    final_answer: str
    error: str

class ManagerAgent:
    def __init__(self, db_manager, sql_agent, hypothesis_agent, proactive_agent):
        self.db_manager = db_manager
        self.sql_agent = sql_agent
        self.hypothesis_agent = hypothesis_agent
        self.proactive_agent = proactive_agent

        # Use Replicate instead of OpenAI
        api_token = os.getenv('REPLICATE_API_TOKEN')
        if not api_token:
            raise ValueError("REPLICATE_API_TOKEN environment variable is not set")

        self.llm = ReplicateChatModel(
            model="openai/gpt-4o-mini",
            temperature=0,
            api_token=api_token
        )
        
        # Build the agent graph
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify", self._classify_question)
        workflow.add_node("sql_query", self._execute_sql)
        workflow.add_node("generate_hypotheses", self._generate_hypotheses)
        workflow.add_node("generate_insights", self._generate_insights)
        workflow.add_node("synthesize", self._synthesize_answer)
        
        # Define edges
        workflow.set_entry_point("classify")
        
        # Conditional routing based on query type
        workflow.add_conditional_edges(
            "classify",
            self._route_query,
            {
                "sql": "sql_query",
                "hypothesis": "generate_hypotheses",
                "conversational": "synthesize",
                "error": END
            }
        )
        
        workflow.add_edge("sql_query", "generate_insights")
        workflow.add_edge("generate_insights", "synthesize")
        workflow.add_edge("generate_hypotheses", "synthesize")
        workflow.add_edge("synthesize", END)
        
        return workflow.compile()
    
    def _classify_question(self, state: AgentState) -> AgentState:
        """Classify the type of question"""
        question = state['question']
        
        system_prompt = """Classify the user's question into one of these categories:
        
1. "data" - Question asks for specific data, numbers, lists, or facts from a database
   Examples: "What are top products?", "Show me sales by state", "How many orders?"
   
2. "hypothesis" - Question asks WHY something happens or to explain a pattern
   Examples: "Why are sales low?", "What causes...", "Why is X happening?"

3. "conversational" - Greetings, thank you, general chat not related to data analysis
   Examples: "hello", "hi", "thank you", "how are you", "bye"
   
Respond with ONLY the category name: "data", "hypothesis", or "conversational"
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Classify this question: {question}")
        ]
        
        response = self.llm.invoke(messages)
        query_type = response.content.strip().lower()
        
        if query_type not in ['data', 'hypothesis', 'conversational']:
            query_type = 'data'  # Default to data query
        
        state['query_type'] = query_type
        state['messages'].append(f"🔍 Question classified as: {query_type}")
        
        return state
    
    def _route_query(self, state: AgentState) -> str:
        """Route to appropriate agent based on classification"""
        if state.get('error'):
            return "error"
        
        if state['query_type'] == 'hypothesis':
            return "hypothesis"
        elif state['query_type'] == 'conversational':
            return "conversational"
        else:
            return "sql"
    
    def _execute_sql(self, state: AgentState) -> AgentState:
        """Execute SQL query using SQL agent"""
        state['messages'].append("🤖 SQL Agent: Generating and executing query...")
        
        result = self.sql_agent.execute_with_correction(state['question'])
        state['sql_result'] = result
        
        if result['success']:
            state['messages'].append(f"✅ Query executed successfully ({result['row_count']} rows)")
        else:
            state['messages'].append(f"❌ Query failed: {result['error']}")
            state['error'] = result['error']
        
        return state
    
    def _generate_hypotheses(self, state: AgentState) -> AgentState:
        """Generate hypotheses for analytical questions"""
        state['messages'].append("🧠 Hypothesis Agent: Generating theories...")
        
        result = self.hypothesis_agent.generate_hypotheses(state['question'])
        state['hypotheses'] = result['hypotheses']
        state['messages'].append(f"✅ Generated {len(result['hypotheses'])} hypotheses")
        
        return state
    
    def _generate_insights(self, state: AgentState) -> AgentState:
        """Generate proactive insights from query results"""
        if not state.get('sql_result') or not state['sql_result'].get('success'):
            return state
        
        state['messages'].append("💡 Proactive Agent: Finding patterns...")
        
        insights = self.proactive_agent.generate_insights(
            state['sql_result'],
            state['question']
        )
        
        if insights:
            state['insights'] = insights
            state['messages'].append(f"✅ Found {len(insights)} insights")
        
        return state
    
    def _synthesize_answer(self, state: AgentState) -> AgentState:
        """Synthesize final answer from all agent outputs"""
        
        if state['query_type'] == 'conversational':
            # Handle conversational queries
            greetings = ['hello', 'hi', 'hey', 'greetings']
            thanks = ['thank', 'thanks']
            
            question_lower = state['question'].lower()
            
            if any(g in question_lower for g in greetings):
                answer = "👋 Hello! I'm your AI E-Commerce Analyst. I can help you analyze your Olist data. Try asking:\n\n"
                answer += "• What are the top selling products?\n"
                answer += "• Show me sales by state\n"
                answer += "• Why are sales low in certain regions?\n"
                answer += "• What's the monthly sales trend?\n\n"
                answer += "What would you like to explore?"
            elif any(t in question_lower for t in thanks):
                answer = "You're welcome! Let me know if you need any other analysis. 😊"
            else:
                answer = "I'm here to help you analyze your e-commerce data! Ask me anything about sales, products, customers, or trends."
        
        elif state['query_type'] == 'hypothesis':
            # Format hypothesis response
            answer = f"**Analysis: {state['question']}**\n\n"
            answer += "Here are three possible explanations:\n\n"
            
            for i, hyp in enumerate(state['hypotheses'], 1):
                answer += f"{hyp}\n\n"
        
        else:
            # Format data query response
            result = state['sql_result']
            
            if not result['success']:
                answer = f"❌ I encountered an error: {result['error']}"
            else:
                answer = f"**Results for: {state['question']}**\n\n"
                answer += f"Found {result['row_count']} results.\n\n"
                
                # Add insights if available
                if state.get('insights'):
                    answer += "**💡 Proactive Insights:**\n\n"
                    for insight in state['insights']:
                        answer += f"{insight['insight']}\n\n"
                        if insight.get('recommendation'):
                            answer += f"*Recommendation: {insight['recommendation']}*\n\n"
        
        state['final_answer'] = answer
        return state
    
    def process_question(self, question: str):
        """Process a question through the agent workflow"""
        
        initial_state = {
            'messages': [],
            'question': question,
            'query_type': '',
            'sql_result': {},
            'hypotheses': [],
            'insights': [],
            'final_answer': '',
            'error': ''
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        return final_state
