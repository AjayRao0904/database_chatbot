"""
Streamlit UI for the Olist Analyst Agent System
Beautiful F-pattern layout with single column chatbot
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path
import streamlit.components.v1 as components
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.db_manager import DatabaseManager
from src.agents.sql_agent import SQLAgent
from src.agents.hypothesis_agent import HypothesisAgent
from src.agents.proactive_agent import ProactiveInsightAgent
from src.agents.manager_agent import ManagerAgent

# Page configuration
st.set_page_config(
    page_title="Olist AI Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for F-pattern and beautiful design
st.markdown("""
<style>
    /* F-Pattern Layout */
    .main {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    }
    
    /* User message */
    .user-message {
        background: linear-gradient(135deg, #ff8c00 0%, #ff6b00 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 18px 18px 5px 18px;
        margin: 10px 0;
        margin-left: 60px;
        box-shadow: 0 2px 10px rgba(255, 140, 0, 0.4);
    }
    
    /* Assistant message */
    .assistant-message {
        background: #2d2d2d;
        color: #ffffff;
        padding: 15px 20px;
        border-radius: 18px 18px 18px 5px;
        margin: 10px 0;
        margin-right: 60px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        border: 1px solid #404040;
    }
    
    /* Header */
    .header-container {
        text-align: center;
        padding: 20px;
        background: #1a1a1a;
        border-radius: 20px;
        margin-bottom: 20px;
        box-shadow: 0 5px 20px rgba(255, 140, 0, 0.3);
        border: 2px solid #ff8c00;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ff8c00 0%, #ff6b00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        color: #cccccc;
    }
    
    /* Input box */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #ff8c00;
        padding: 15px 20px !important;
        font-size: 1rem;
        background: #2d2d2d;
        color: white !important;
        min-height: 50px !important;
        height: 50px !important;
        line-height: 1.5;
        box-sizing: border-box;
    }

    /* Remove floating label */
    .stTextInput > label {
        display: none !important;
    }

    .stTextInput > div > div > input:focus {
        outline: none !important;
        border-color: #ff8c00;
        box-shadow: none !important;
    }

    /* Remove the container focus effect */
    .stTextInput > div:focus-within {
        box-shadow: none !important;
    }

    /* Align input container */
    .stTextInput {
        margin-bottom: 0px;
    }

    /* Fix text input container to prevent cutoff */
    .stTextInput > div {
        overflow: visible !important;
    }

    .stTextInput > div > div {
        overflow: visible !important;
        height: auto !important;
        min-height: 50px !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #ff8c00 0%, #ff6b00 100%);
        color: white;
        border-radius: 25px;
        padding: 10px 20px;
        border: none;
        font-weight: 600;
        font-size: 1.2rem;
        transition: all 0.3s;
        min-height: 50px;
        height: 50px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(255, 140, 0, 0.5);
    }
    
    /* Voice button */
    #voiceBtn {
        background: linear-gradient(135deg, #ff8c00 0%, #ff6b00 100%);
        color: white;
        border-radius: 25px;
        padding: 10px 20px;
        border: none;
        font-weight: 600;
        font-size: 1.2rem;
        cursor: pointer;
        min-height: 50px;
        height: 50px;
        width: 100%;
        transition: all 0.3s;
    }
    
    #voiceBtn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(255, 140, 0, 0.5);
    }
    
    /* Metrics */
    .metric-card {
        background: #2d2d2d;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(255, 140, 0, 0.2);
        text-align: center;
        border: 1px solid #ff8c00;
    }
    
    /* Process indicator */
    .process-step {
        background: #2d2d2d;
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 4px solid #ff8c00;
        color: #ffffff;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #1a1a1a;
    }
    
    /* Sidebar text color */
    [data-testid="stSidebar"] {
        background: #1a1a1a;
        color: white;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Metric labels */
    [data-testid="stMetricLabel"] {
        color: #ff8c00 !important;
    }
    
    /* Metric values */
    [data-testid="stMetricValue"] {
        color: white !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Hide iframe borders and extra spacing */
    iframe {
        border: none !important;
    }

    /* Better dataframe styling */
    [data-testid="stDataFrame"] {
        background: #2d2d2d;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }

    /* Chart container styling */
    [data-testid="stPlotlyChart"] {
        background: #2d2d2d;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: #2d2d2d !important;
        border-radius: 10px;
        color: white !important;
    }

    /* Hide any stray divs from components */
    [data-testid="stVerticalBlock"] > div > div:empty {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'agents_initialized' not in st.session_state:
    with st.spinner("🚀 Initializing AI Analyst Team..."):
        try:
            db_manager = DatabaseManager()
            sql_agent = SQLAgent(db_manager)
            hypothesis_agent = HypothesisAgent(db_manager, sql_agent)
            proactive_agent = ProactiveInsightAgent(db_manager)
            manager_agent = ManagerAgent(db_manager, sql_agent, hypothesis_agent, proactive_agent)
            
            st.session_state.db_manager = db_manager
            st.session_state.manager_agent = manager_agent
            st.session_state.agents_initialized = True
        except Exception as e:
            st.error(f"❌ Failed to initialize agents: {e}")
            st.stop()

# Sidebar
with st.sidebar:
    st.markdown("### 🤖 Olist AI Analyst")
    st.markdown("---")
    
    # Language selection for voice
    voice_lang = st.selectbox(
        "🌐 Voice Language",
        options=[("English", "en-US"), ("Português", "pt-BR")],
        format_func=lambda x: x[0],
        key="voice_language"
    )
    
    st.markdown("---")
    
    # Database stats
    st.markdown("### 📊 Database Stats")
    
    try:
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM orders) as orders,
                (SELECT COUNT(*) FROM customers) as customers,
                (SELECT COUNT(*) FROM products) as products,
                (SELECT ROUND(SUM(price)::numeric, 2) FROM order_items) as revenue
        """
        stats_result = st.session_state.db_manager.execute_query(stats_query)
        
        if stats_result['success'] and stats_result['rows']:
            stats = stats_result['rows'][0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Orders", f"{stats['orders']:,}")
                st.metric("Products", f"{stats['products']:,}")
            with col2:
                st.metric("Customers", f"{stats['customers']:,}")
                st.metric("Revenue", f"R$ {stats['revenue']:,.2f}")
    except:
        pass
    
    st.markdown("---")
    
    # Frequently Asked Questions
    st.markdown("### ❓ Frequently Asked Questions")
    
    faq_questions = [
        "What are the top selling categories?",
        "Show me revenue by state",
        "Which payment method is most popular?",
        "What's the average order value?",
        "How many orders per month?",
        "Top performing sellers by revenue",
        "Which states have the most customers?",
        "What's the average delivery time?",
        "Revenue trend over time",
        "Most used payment installments"
    ]
    
    for question in faq_questions:
        if st.button(question, key=f"faq_{question}"):
            st.session_state.messages.append({
                "role": "user",
                "content": question,
                "timestamp": datetime.now()
            })
            st.rerun()

    st.markdown("---")

    # Clear chat
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### ⚙️ Agent Features")
    st.markdown("""
    - ✅ Self-Correcting SQL
    - ✅ Hypothesis Generation
    - ✅ Proactive Insights
    - ✅ Multi-Agent Orchestration
    - ✅ Portuguese Support
    - ✅ Voice Input 🎤
    """)

# Main content
# Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🤖 Olist AI Analyst</h1>
    <p class="header-subtitle">Your Autonomous E-Commerce Intelligence Assistant</p>
</div>
""", unsafe_allow_html=True)

# Chat container
chat_container = st.container()

with chat_container:
    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            # Escape HTML in user messages
            content = message["content"].replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(f"""
            <div class="user-message">
                <strong>You</strong><br/>
                {content}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Clean markdown formatting and escape HTML in assistant messages
            content = message["content"]

            # Remove bold/italic markdown
            content = content.replace("**", "")  # Remove bold
            content = content.replace("*", "")   # Remove italic/emphasis
            content = content.replace("__", "")  # Remove bold alternative
            content = content.replace("_", "")   # Remove italic alternative

            # Escape HTML
            content = content.replace("<", "&lt;").replace(">", "&gt;")

            # Convert newlines to line breaks
            content = content.replace("\n", "<br/>")

            st.markdown(f"""
            <div class="assistant-message">
                <strong>🤖 AI Analyst</strong><br/>
                {content}
            </div>
            """, unsafe_allow_html=True)

            # Show data table if available
            if "data" in message:
                st.dataframe(message["data"], use_container_width=True)

            # Show chart if available
            if "chart" in message:
                st.plotly_chart(message["chart"], use_container_width=True)

            # Show process steps if available
            if "process" in message:
                with st.expander("🔍 See how I worked"):
                    for step in message["process"]:
                        # Clean markdown and escape HTML in process steps
                        step_clean = step
                        # Remove markdown formatting
                        step_clean = step_clean.replace("**", "").replace("*", "")
                        step_clean = step_clean.replace("__", "").replace("_", "")
                        # Escape HTML
                        step_clean = step_clean.replace("<", "&lt;").replace(">", "&gt;")
                        st.markdown(f'<div class="process-step">{step_clean}</div>', unsafe_allow_html=True)

# Input area (fixed at bottom)
st.markdown("<br/><br/>", unsafe_allow_html=True)

# Create input container with proper spacing
input_container = st.container()
with input_container:
    col1, col2, col3 = st.columns([7, 1, 1])

    with col1:
        # Use voice text if available, otherwise empty
        default_value = st.session_state.get('voice_text', '')

        user_input = st.text_input(
            "Ask me anything about your e-commerce data...",
            key="user_input",
            placeholder="e.g., What are the top selling products?",
            label_visibility="collapsed",
            value=default_value
        )

        # Clear voice text after using it
        if default_value:
            st.session_state.voice_text = ""

    with col2:
        # Voice input using streamlit component
        voice_lang_code = st.session_state.get('voice_language', ('English', 'en-US'))[1]

        # Initialize voice counter for unique keys
        if 'voice_counter' not in st.session_state:
            st.session_state.voice_counter = 0

        # Create a unique key for voice input
        if 'voice_text' not in st.session_state:
            st.session_state.voice_text = ""

        voice_component = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
            }}
            #voiceBtn {{
                background: linear-gradient(135deg, #ff8c00 0%, #ff6b00 100%);
                color: white;
                border-radius: 25px;
                padding: 10px 20px;
                border: none;
                font-weight: 600;
                font-size: 1.2rem;
                cursor: pointer;
                min-height: 50px;
                height: 50px;
                width: 100%;
                transition: all 0.3s;
                display: flex;
                align-items: center;
                justify-content: center;
            }}

            #voiceBtn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(255, 140, 0, 0.5);
            }}

            #voiceBtn:disabled {{
                opacity: 0.6;
                cursor: not-allowed;
            }}
        </style>
    </head>
    <body>
        <button id="voiceBtn" onclick="startVoice()">🎤</button>

        <script>
        let recognition = null;
        let isListening = false;

        // Function to find and update the input field directly
        function updateInputField(text) {{
            try {{
                // Try multiple selectors to find the input field
                let inputField = window.parent.document.querySelector('input[data-testid="stTextInput"]') ||
                                window.parent.document.querySelector('input[placeholder*="e-commerce"]') ||
                                window.parent.document.querySelector('input[type="text"]');

                if (inputField) {{
                    // Set the value
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, "value").set;
                    nativeInputValueSetter.call(inputField, text);

                    // Trigger events to make React/Streamlit notice the change
                    inputField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    inputField.dispatchEvent(new Event('change', {{ bubbles: true }}));

                    // Focus the input field
                    inputField.focus();

                    console.log('Successfully updated input field with:', text);
                    return true;
                }} else {{
                    console.error('Could not find input field');
                    return false;
                }}
            }} catch (e) {{
                console.error('Error updating input field:', e);
                return false;
            }}
        }}

        // Check if browser supports speech recognition
        window.addEventListener('load', () => {{
            console.log('Voice component loaded');
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                const voiceBtn = document.getElementById('voiceBtn');
                voiceBtn.innerHTML = '❌';
                voiceBtn.disabled = true;
                voiceBtn.title = 'Speech recognition not supported. Please use Chrome or Edge.';
            }}
        }});

        function startVoice() {{
            console.log('Voice button clicked');
            const voiceBtn = document.getElementById('voiceBtn');

            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                alert('Speech recognition is not supported in this browser.\\n\\nPlease use:\\n- Google Chrome\\n- Microsoft Edge\\n- Safari (iOS)');
                return;
            }}

            if (isListening && recognition) {{
                console.log('Stopping recognition');
                recognition.stop();
                isListening = false;
                voiceBtn.innerHTML = '🎤';
                voiceBtn.style.background = 'linear-gradient(135deg, #ff8c00 0%, #ff6b00 100%)';
                voiceBtn.style.fontSize = '1.2rem';
                return;
            }}

            try {{
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();

                // Configuration
                recognition.lang = '{voice_lang_code}';
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.maxAlternatives = 1;

                // Show requesting permission
                voiceBtn.innerHTML = '⏳';
                voiceBtn.style.background = 'linear-gradient(135deg, #ffa500 0%, #ff8c00 100%)';

                recognition.onstart = () => {{
                    console.log('Recording started');
                    isListening = true;
                    voiceBtn.innerHTML = '🔴 Listening...';
                    voiceBtn.style.background = 'linear-gradient(135deg, #ff0000 0%, #cc0000 100%)';
                    voiceBtn.style.fontSize = '0.9rem';
                }};

                recognition.onresult = (event) => {{
                    const transcript = event.results[0][0].transcript;
                    const confidence = event.results[0][0].confidence;
                    console.log('Transcript received:', transcript, 'Confidence:', confidence);

                    // Show success feedback
                    voiceBtn.innerHTML = '✅';
                    voiceBtn.style.background = 'linear-gradient(135deg, #00cc00 0%, #009900 100%)';

                    // Update the input field directly
                    const success = updateInputField(transcript);

                    if (!success) {{
                        alert('Voice captured: "' + transcript + '"\\n\\nBut could not update input field automatically. Please type it manually.');
                    }}

                    // Reset button after a delay
                    setTimeout(() => {{
                        voiceBtn.innerHTML = '🎤';
                        voiceBtn.style.background = 'linear-gradient(135deg, #ff8c00 0%, #ff6b00 100%)';
                        voiceBtn.style.fontSize = '1.2rem';
                    }}, 1500);
                }};

                recognition.onerror = (event) => {{
                    console.error('Recognition error:', event.error);
                    isListening = false;
                    voiceBtn.innerHTML = '🎤';
                    voiceBtn.style.background = 'linear-gradient(135deg, #ff8c00 0%, #ff6b00 100%)';
                    voiceBtn.style.fontSize = '1.2rem';

                    let errorMessage = '';

                    switch(event.error) {{
                        case 'not-allowed':
                        case 'permission-denied':
                            errorMessage = 'Microphone access denied!\\n\\nPlease:\\n1. Click the 🔒 icon in your browser address bar\\n2. Allow microphone access\\n3. Refresh the page and try again';
                            break;
                        case 'no-speech':
                            errorMessage = 'No speech detected.\\n\\nPlease:\\n- Speak clearly into your microphone\\n- Check your microphone is working\\n- Try again';
                            break;
                        case 'audio-capture':
                            errorMessage = 'Microphone not found!\\n\\nPlease:\\n- Check your microphone is connected\\n- Ensure it is not being used by another application\\n- Try again';
                            break;
                        case 'network':
                            errorMessage = 'Network error occurred.\\n\\nPlease check your internet connection and try again.';
                            break;
                        case 'aborted':
                            console.log('Recognition aborted by user');
                            return; // Don't show alert for user abort
                        default:
                            errorMessage = 'Voice recognition error: ' + event.error + '\\n\\nPlease try again.';
                    }}

                    if (errorMessage) {{
                        alert(errorMessage);
                    }}
                }};

                recognition.onend = () => {{
                    console.log('Recording ended');
                    isListening = false;
                    if (voiceBtn.innerHTML !== '✅') {{
                        voiceBtn.innerHTML = '🎤';
                        voiceBtn.style.background = 'linear-gradient(135deg, #ff8c00 0%, #ff6b00 100%)';
                        voiceBtn.style.fontSize = '1.2rem';
                    }}
                }};

                console.log('Starting recognition with language:', '{voice_lang_code}');
                recognition.start();

            }} catch(e) {{
                console.error('Error starting recognition:', e);
                voiceBtn.innerHTML = '🎤';
                voiceBtn.style.background = 'linear-gradient(135deg, #ff8c00 0%, #ff6b00 100%)';
                voiceBtn.style.fontSize = '1.2rem';
                alert('Failed to start voice recognition.\\n\\nError: ' + e.message + '\\n\\nPlease ensure you are using Chrome, Edge, or Safari.');
            }}
        }}
        </script>
    </body>
    </html>
        """

        # Render the voice component (no need to capture return value)
        components.html(voice_component, height=60)

    with col3:
        send_button = st.button("▶", type="primary")

# Process new message
if send_button and user_input:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    # Process with agents
    with st.spinner("🤔 Thinking..."):
        try:
            result = st.session_state.manager_agent.process_question(user_input)
            
            # Add SQL query to process messages if available
            if result.get('sql_result') and result['sql_result'].get('query'):
                result['messages'].append(f"📝 Generated SQL: {result['sql_result']['query']}")
            
            # Prepare response
            response = {
                "role": "assistant",
                "content": result['final_answer'],
                "timestamp": datetime.now(),
                "process": result['messages']
            }
            
            # Add data table if available
            if result.get('sql_result') and result['sql_result'].get('success'):
                sql_result = result['sql_result']
                
                if sql_result['rows']:
                    df = pd.DataFrame(sql_result['rows'])
                    response["data"] = df
                    
                    # Create visualization if numeric data exists
                    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
                    
                    if len(numeric_cols) >= 1 and len(df) > 1:
                        # Create chart based on data
                        if len(df.columns) >= 2:
                            x_col = df.columns[0]
                            y_col = numeric_cols[0]
                            
                            # Limit to top 10 for readability
                            df_plot = df.head(10)
                            
                            fig = px.bar(
                                df_plot,
                                x=x_col,
                                y=y_col,
                                title=f"{y_col} by {x_col}",
                                color=y_col,
                                color_continuous_scale="Viridis"
                            )
                            
                            fig.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                xaxis_tickangle=-45,
                                height=400
                            )
                            
                            response["chart"] = fig
            
            st.session_state.messages.append(response)
            
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ I encountered an error: {str(e)}",
                "timestamp": datetime.now()
            })
    
    st.rerun()

# Welcome message
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div style='text-align: center; padding: 40px; color: white;'>
        <h2 style='color: #ff8c00;'>👋 Welcome! I'm your AI E-Commerce Analyst</h2>
        <p style='font-size: 1.1rem; margin-top: 20px; color: #ffffff;'>
            Ask me anything about your Olist e-commerce data!<br/>
            I can analyze sales, find patterns, and generate insights.
        </p>
        <p style='font-size: 0.9rem; margin-top: 20px; opacity: 0.8; color: #cccccc;'>
            Try one of the sample questions from the sidebar →
        </p>
    </div>
    """, unsafe_allow_html=True)
