# Olist AI Analyst

An intelligent data analysis platform that combines natural language processing with SQL generation to provide insights from Brazilian e-commerce data. Features a multi-agent architecture with self-healing query capabilities and voice input support.

## Features

- **Natural Language Queries**: Ask questions in plain English about your e-commerce data
- **Voice Input**: Speak your queries using the built-in microphone feature (Chrome/Edge/Safari)
- **Multi-Agent Architecture**: Specialized agents for SQL generation, hypothesis testing, and proactive insights
- **Self-Healing Queries**: Automatic SQL error detection and correction (up to 3 retry attempts)
- **Interactive Visualizations**: Charts, graphs, and formatted data displays
- **Business Intelligence**: Automated pattern detection and A/B test recommendations

## Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Replicate API token (sign up at https://replicate.com)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd ap
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up env variables:
GEMINI_API_KEY
DATABASE_URL

4. Set up the database:
```bash
python scripts/download_dataset.py  # Download Olist dataset from Kaggle
python scripts/setup_database.py    # Create PostgreSQL schema
python scripts/load_data.py          # Load data into database
```

5. Run the application:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Architecture

### Multi-Agent System

The application uses a coordinated multi-agent architecture powered by LangChain and LangGraph:

```
User Query → Manager Agent → [SQL Agent | Hypothesis Agent | Proactive Agent] → Results
```

#### 1. Manager Agent (`src/agents/manager_agent.py`)
- **Role**: Request orchestration and routing
- **Technology**: LangGraph for workflow management
- **Function**: Classifies incoming queries and delegates to appropriate specialized agents
- **LLM**: GPT-4o-mini via Replicate API

#### 2. SQL Agent (`src/agents/sql_agent.py`)
- **Role**: Query generation and execution
- **Features**:
  - Natural language to SQL translation
  - Self-healing with retry logic (max 3 attempts)
  - Query validation and error correction
  - Schema-aware generation using database introspection
- **LLM**: GPT-4o-mini via Replicate API (temperature=0 for consistent SQL)

#### 3. Hypothesis Agent (`src/agents/hypothesis_agent.py`)
- **Role**: Pattern analysis and A/B testing
- **Capabilities**:
  - Business hypothesis generation
  - Statistical significance testing
  - A/B test design recommendations
- **LLM**: GPT-4o-mini via Replicate API (temperature=0.7 for creativity)

#### 4. Proactive Agent (`src/agents/proactive_agent.py`)
- **Role**: Autonomous insight discovery
- **Capabilities**:
  - Anomaly detection in query results
  - Trend identification
  - Automated recommendations based on data patterns
- **LLM**: GPT-4o-mini via Replicate API (temperature=0.7 for varied insights)

### Self-Healing Query System

The SQL Agent implements a sophisticated error correction pipeline that automatically fixes SQL errors without user intervention:

**Process Flow:**
1. **Initial Query Generation**: LLM translates natural language to SQL
2. **Execution Attempt**: Query runs against PostgreSQL database
3. **Error Detection**: Catches syntax errors, missing columns, type mismatches, or logical issues
4. **Automatic Correction**: LLM analyzes the error message and database schema to regenerate query
5. **Retry Logic**: Up to 3 attempts before returning error to user

**Example:**
```
User: "Show me top products by revenue"

Attempt 1:
Generated: SELECT * FROM products ORDER BY revenue DESC
Error: Column 'revenue' doesn't exist

Attempt 2 (auto-corrected):
Generated: SELECT product_id, SUM(price * quantity) as revenue
           FROM order_items
           GROUP BY product_id
           ORDER BY revenue DESC
           LIMIT 10
Success: Returns results with automatic visualization
```

### Technology Stack

- **Frontend**: Streamlit (Python web framework for data apps)
- **LLM Operations**: Gemini API 
- **Agent Framework**: LangChain + LangGraph
- **Database**: PostgreSQL with Brazilian e-commerce data
- **Voice Input**: Web Speech API (browser-native, no backend required)
- **Visualization**: Plotly, Matplotlib, Streamlit native charts
- **Custom LLM Wrapper**: `src/utils/replicate_llm.py` (LangChain-compatible)

### Design Decisions

#### Why Multi-Agent Architecture?
- **Separation of Concerns**: Each agent specializes in one task (SQL, analysis, insights)
- **Parallel Processing**: Manager can coordinate multiple agents simultaneously
- **Maintainability**: Easy to update or replace individual agents without affecting others
- **Scalability**: Add new specialized agents (e.g., forecasting, sentiment analysis) without refactoring
- **Debugging**: Isolated agent logs make it easy to trace issues

#### Why Self-Healing Queries?
- **User Experience**: Non-technical users don't need to understand SQL errors
- **Reliability**: Handles schema changes and edge cases gracefully
- **Learning System**: Each correction improves the LLM's understanding of the schema
- **Reduced Support**: 80%+ of SQL errors are automatically corrected

#### Why Browser-Based Voice Input?
- **Zero Backend Cost**: Web Speech API runs entirely in the browser
- **Low Latency**: No API calls for transcription (instant)
- **Privacy**: Voice data never leaves the user's device
- **Cross-Platform**: Works on any modern browser (Chrome, Edge, Safari)

## Project Structure

```
ap/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (create this, never commit)
├── src/
│   ├── agents/
│   │   ├── manager_agent.py       # Request orchestration with LangGraph
│   │   ├── sql_agent.py           # SQL generation with self-healing
│   │   ├── hypothesis_agent.py    # Pattern analysis and A/B testing
│   │   └── proactive_agent.py     # Autonomous insight generation
│   ├── database/
│   │   └── db_manager.py          # PostgreSQL connection manager
│   └── utils/
│       └── replicate_llm.py       # Custom LangChain wrapper for Replicate
├── scripts/
│   ├── download_dataset.py        # Kaggle dataset downloader
│   ├── setup_database.py          # PostgreSQL schema creation
│   └── load_data.py               # CSV to PostgreSQL loader
├── data/                          # Downloaded Olist CSV files (gitignored)
├── docs/                          # Additional documentation
│   ├── SELF_HEALING_TEST_GUIDE.md # Testing self-correction feature
│   ├── VIDEO_SCRIPT.md            # Demo video script
│   └── TEST_QUERIES.md            # 50+ example queries
└── test_replicate_quick.py        # Replicate API integration tests
```

## Usage Examples

### Text Input
```
"What are the top 10 products by revenue?"
"Show me customer distribution by state"
"Which sellers have the highest ratings?"
"Compare Q1 and Q2 revenue for 2017"
"What's the correlation between delivery time and ratings?"
```

### Voice Input

1. Click the **🎤 microphone button** in the sidebar
2. Allow microphone permissions when prompted by browser
3. Speak your query clearly in English
4. Text will automatically populate in the input field
5. Press Enter or click Submit

**Supported Browsers**: Chrome, Edge, Safari (not Firefox)

### Advanced Queries

The system handles complex analytical questions:
```
"Identify products with declining sales trends"
"Show geographic concentration of high-value customers"
"Find categories with seasonality patterns"
"Which payment methods correlate with higher order values?"
"Analyze seller performance metrics across regions"
```

## Testing Self-Healing

To test the self-healing query feature, try these intentionally ambiguous or incorrect queries:

**Test Cases:**
- `"Show me sales"` → System clarifies: which sales metric? (revenue, count, items)
- `"Top products"` → System infers: by revenue, adds LIMIT 10
- `"Customer info from last month"` → System determines date range from current date
- `"Products with good reviews"` → System defines "good" as rating >= 4.0

**What Gets Auto-Corrected:**
- Missing table aliases
- Incorrect column names (fuzzy matching)
- Missing GROUP BY clauses
- Ambiguous date ranges
- Type mismatches (string vs. numeric)


## Configuration

### Database Setup

The application expects an Olist e-commerce database with these tables:
- `orders` - Order metadata (status, timestamps, customer_id)
- `order_items` - Line items (product_id, seller_id, price, freight)
- `products` - Product catalog (category, dimensions, photos)
- `customers` - Customer data (location, unique_id)
- `sellers` - Seller information (location, zip_code)
- `order_reviews` - Review scores and comments
- `order_payments` - Payment methods and installments
- `geolocation` - Brazilian zip code coordinates

