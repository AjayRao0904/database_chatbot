# Olist Database Setup Guide

## 📋 Prerequisites

### 1. Install PostgreSQL

**Windows:**
- Download from: https://www.postgresql.org/download/windows/
- Or use Chocolatey: `choco install postgresql`

**Verify installation:**
```powershell
psql --version
```

### 2. Install Python Dependencies

```powershell
# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Kaggle API

**Option A: Using .env file (Recommended)**
1. Get your API credentials from: https://www.kaggle.com/settings
2. Copy `.env.example` to `.env`
3. Add your credentials:
   ```
   KAGGLE_USERNAME=your_username
   KAGGLE_KEY=your_api_key
   ```

**Option B: Using kaggle.json**
1. Download `kaggle.json` from: https://www.kaggle.com/settings
2. Place it in: `C:\Users\<YourUsername>\.kaggle\kaggle.json`

### 4. Configure Database Connection

Edit `.env` file with your PostgreSQL credentials:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=olist_ecommerce
DB_USER=postgres
DB_PASSWORD=your_password
```

## 🚀 Step-by-Step Setup

### Step 1: Download the Dataset

```powershell
python scripts/download_dataset.py
```

**Expected output:**
- 9 CSV files downloaded to `data/` folder
- Total size: ~126 MB

**Files downloaded:**
- `olist_customers_dataset.csv` (~9 MB)
- `olist_geolocation_dataset.csv` (largest)
- `olist_order_items_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_orders_dataset.csv`
- `olist_products_dataset.csv`
- `olist_sellers_dataset.csv`
- `product_category_name_translation.csv`

### Step 2: Explore the Data (Optional)

```powershell
python scripts/explore_data.py
```

This will show you:
- Column names and data types
- Sample data from each file
- Basic statistics
- Null value percentages

### Step 3: Create Database Schema

```powershell
python scripts/setup_database.py
```

**What this does:**
- Creates database `olist_ecommerce` (if it doesn't exist)
- Creates 9 tables with proper relationships
- Adds indexes for performance
- Creates a summary view for easy analysis

**Tables created:**
- `customers`
- `sellers`
- `products`
- `product_category_translation`
- `orders`
- `order_items`
- `order_payments`
- `order_reviews`
- `geolocation`

### Step 4: Load Data into PostgreSQL

```powershell
python scripts/load_data.py
```

**This process:**
- Reads all CSV files
- Cleans and validates data
- Inserts data in proper order (respecting foreign keys)
- Shows progress bars
- Handles duplicates in geolocation data

**Expected time:** 2-5 minutes depending on your system

## ✅ Verify Installation

### Connect to PostgreSQL

```powershell
psql -U postgres -d olist_ecommerce
```

### Run test queries:

```sql
-- Check table counts
SELECT 'orders' as table_name, COUNT(*) FROM orders
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products;

-- Sample order summary
SELECT * FROM order_summary LIMIT 5;

-- Top 5 cities by orders
SELECT customer_city, COUNT(*) as orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY customer_city
ORDER BY orders DESC
LIMIT 5;
```

## 📊 Database Schema Overview

```
customers
├── customer_id (PK)
├── customer_unique_id
├── customer_zip_code_prefix
├── customer_city
└── customer_state

orders
├── order_id (PK)
├── customer_id (FK → customers)
├── order_status
├── order_purchase_timestamp
├── order_approved_at
├── order_delivered_carrier_date
├── order_delivered_customer_date
└── order_estimated_delivery_date

order_items
├── order_id (FK → orders)
├── order_item_id
├── product_id (FK → products)
├── seller_id (FK → sellers)
├── shipping_limit_date
├── price
└── freight_value

products
├── product_id (PK)
├── product_category_name
├── product_name_length
├── product_description_length
├── product_photos_qty
├── product_weight_g
├── product_length_cm
├── product_height_cm
└── product_width_cm

sellers
├── seller_id (PK)
├── seller_zip_code_prefix
├── seller_city
└── seller_state

order_reviews
├── review_id (PK)
├── order_id (FK → orders)
├── review_score
├── review_comment_title
├── review_comment_message
├── review_creation_date
└── review_answer_timestamp

order_payments
├── order_id (FK → orders)
├── payment_sequential
├── payment_type
├── payment_installments
└── payment_value

geolocation
├── geolocation_zip_code_prefix
├── geolocation_lat
├── geolocation_lng
├── geolocation_city
└── geolocation_state
```

## 🔍 Sample Queries

See `scripts/sample_queries.sql` for a comprehensive collection of useful queries including:
- Sales analysis
- Customer behavior
- Product performance
- Delivery metrics
- Review analysis
- Geographic insights

## 🐛 Troubleshooting

### "Kaggle API credentials not found"
- Make sure you've added credentials to `.env` or placed `kaggle.json` in the right location
- Check file permissions

### "Password authentication failed for user postgres"
- Verify your PostgreSQL password in `.env`
- Try resetting your PostgreSQL password:
  ```sql
  ALTER USER postgres PASSWORD 'new_password';
  ```

### "Database already exists"
- The script will use the existing database
- To start fresh: `DROP DATABASE olist_ecommerce;` in psql

### "CSV files not found"
- Make sure Step 1 (download) completed successfully
- Check that files exist in `data/` folder

### Import errors (psycopg2, pandas, etc.)
- Make sure you activated the virtual environment
- Run: `pip install -r requirements.txt`

## 📚 Next Steps

Now that your database is set up, you can:

1. **Explore the data** using the sample queries
2. **Build the agent system** for autonomous analysis
3. **Create visualizations** of key metrics
4. **Develop the multi-agent architecture** with LangGraph

Check out the main README.md for the full project roadmap!
