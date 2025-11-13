"""
Setup PostgreSQL database schema for Olist E-Commerce dataset
Creates all tables with proper relationships based on the Olist schema
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

sys.path.append(str(Path(__file__).parent.parent))
load_dotenv()

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'olist_ecommerce'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# SQL Schema based on Olist data structure
SCHEMA_SQL = """
-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS order_reviews CASCADE;
DROP TABLE IF EXISTS order_payments CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS sellers CASCADE;
DROP TABLE IF EXISTS geolocation CASCADE;
DROP TABLE IF EXISTS product_category_translation CASCADE;

-- Customers table
CREATE TABLE customers (
    customer_id VARCHAR(255) PRIMARY KEY,
    customer_unique_id VARCHAR(255) NOT NULL,
    customer_zip_code_prefix VARCHAR(10),
    customer_city VARCHAR(255),
    customer_state VARCHAR(10)
);

-- Sellers table
CREATE TABLE sellers (
    seller_id VARCHAR(255) PRIMARY KEY,
    seller_zip_code_prefix VARCHAR(10),
    seller_city VARCHAR(255),
    seller_state VARCHAR(10)
);

-- Products table
CREATE TABLE products (
    product_id VARCHAR(255) PRIMARY KEY,
    product_category_name VARCHAR(255),
    product_name_length INTEGER,
    product_description_length INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER
);

-- Product category translation (Portuguese to English)
CREATE TABLE product_category_translation (
    product_category_name VARCHAR(255) PRIMARY KEY,
    product_category_name_english VARCHAR(255)
);

-- Orders table
CREATE TABLE orders (
    order_id VARCHAR(255) PRIMARY KEY,
    customer_id VARCHAR(255) REFERENCES customers(customer_id),
    order_status VARCHAR(50),
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

-- Order items table
CREATE TABLE order_items (
    order_id VARCHAR(255) REFERENCES orders(order_id),
    order_item_id INTEGER,
    product_id VARCHAR(255) REFERENCES products(product_id),
    seller_id VARCHAR(255) REFERENCES sellers(seller_id),
    shipping_limit_date TIMESTAMP,
    price DECIMAL(10, 2),
    freight_value DECIMAL(10, 2),
    PRIMARY KEY (order_id, order_item_id, product_id, seller_id)
);

-- Order payments table
CREATE TABLE order_payments (
    order_id VARCHAR(255) REFERENCES orders(order_id),
    payment_sequential INTEGER,
    payment_type VARCHAR(50),
    payment_installments INTEGER,
    payment_value DECIMAL(10, 2),
    PRIMARY KEY (order_id, payment_sequential)
);

-- Order reviews table
CREATE TABLE order_reviews (
    review_id VARCHAR(255) PRIMARY KEY,
    order_id VARCHAR(255) REFERENCES orders(order_id),
    review_score INTEGER,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP
);

-- Geolocation table (Brazilian zip codes with lat/lng)
CREATE TABLE geolocation (
    geolocation_zip_code_prefix VARCHAR(10),
    geolocation_lat DECIMAL(10, 8),
    geolocation_lng DECIMAL(11, 8),
    geolocation_city VARCHAR(255),
    geolocation_state VARCHAR(10)
);

-- Create indexes for better query performance
CREATE INDEX idx_customers_unique ON customers(customer_unique_id);
CREATE INDEX idx_customers_city ON customers(customer_city);
CREATE INDEX idx_customers_state ON customers(customer_state);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_orders_purchase_date ON orders(order_purchase_timestamp);

CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_order_items_seller ON order_items(seller_id);

CREATE INDEX idx_products_category ON products(product_category_name);

CREATE INDEX idx_sellers_city ON sellers(seller_city);
CREATE INDEX idx_sellers_state ON sellers(seller_state);

CREATE INDEX idx_reviews_order ON order_reviews(order_id);
CREATE INDEX idx_reviews_score ON order_reviews(review_score);

CREATE INDEX idx_geolocation_zip ON geolocation(geolocation_zip_code_prefix);
CREATE INDEX idx_geolocation_city ON geolocation(geolocation_city);

-- Create a view for easy order analysis
CREATE OR REPLACE VIEW order_summary AS
SELECT 
    o.order_id,
    o.customer_id,
    c.customer_city,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    COUNT(DISTINCT oi.product_id) as total_items,
    SUM(oi.price) as total_price,
    SUM(oi.freight_value) as total_freight,
    AVG(r.review_score) as avg_review_score
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN order_reviews r ON o.order_id = r.order_id
GROUP BY o.order_id, o.customer_id, c.customer_city, c.customer_state, 
         o.order_status, o.order_purchase_timestamp, o.order_delivered_customer_date;
"""

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (default 'postgres' database)
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_CONFIG['database'],)
        )
        exists = cursor.fetchone()
        
        if not exists:
            print(f"📊 Creating database '{DB_CONFIG['database']}'...")
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(DB_CONFIG['database'])
                )
            )
            print("✅ Database created successfully!")
        else:
            print(f"✅ Database '{DB_CONFIG['database']}' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def setup_schema():
    """Create all tables and indexes"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("\n🏗️  Creating database schema...")
        cursor.execute(SCHEMA_SQL)
        conn.commit()
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"\n✅ Schema created successfully! Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up schema: {e}")
        return False

def main():
    print("=" * 60)
    print("  Olist Database Setup")
    print("=" * 60)
    
    print(f"\n📍 Connection Info:")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   Port: {DB_CONFIG['port']}")
    print(f"   Database: {DB_CONFIG['database']}")
    print(f"   User: {DB_CONFIG['user']}")
    
    # Step 1: Create database
    if not create_database():
        sys.exit(1)
    
    # Step 2: Setup schema
    if not setup_schema():
        sys.exit(1)
    
    print("\n✨ Database setup complete!")
    print("\n📝 Next steps:")
    print("   1. Review the database schema in PostgreSQL")
    print("   2. Run: python scripts/load_data.py")

if __name__ == "__main__":
    main()
