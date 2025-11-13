"""
Load Olist CSV data into PostgreSQL database
Handles data cleaning, type conversion, and batch insertion
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from tqdm import tqdm

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

# Mapping of CSV files to database tables
TABLE_MAPPINGS = {
    'olist_customers_dataset.csv': 'customers',
    'olist_sellers_dataset.csv': 'sellers',
    'olist_products_dataset.csv': 'products',
    'product_category_name_translation.csv': 'product_category_translation',
    'olist_orders_dataset.csv': 'orders',
    'olist_order_items_dataset.csv': 'order_items',
    'olist_order_payments_dataset.csv': 'order_payments',
    'olist_order_reviews_dataset.csv': 'order_reviews',
    'olist_geolocation_dataset.csv': 'geolocation'
}

def clean_dataframe(df, table_name):
    """Clean and prepare DataFrame for database insertion"""
    
    # Replace NaN with None for proper NULL insertion
    df = df.where(pd.notnull(df), None)
    
    # Fix column name typos in products table (CSV has typos)
    if table_name == 'products':
        column_fixes = {
            'product_name_lenght': 'product_name_length',
            'product_description_lenght': 'product_description_length'
        }
        df.rename(columns=column_fixes, inplace=True)
    
    # Special handling for specific tables
    if table_name == 'geolocation':
        # Remove duplicates in geolocation to avoid massive dataset
        print(f"   Original geolocation rows: {len(df):,}")
        df = df.drop_duplicates(subset=['geolocation_zip_code_prefix'])
        print(f"   After deduplication: {len(df):,}")
    
    return df

def insert_data(conn, cursor, table_name, df, batch_size=1000):
    """Insert DataFrame into database table in batches"""
    
    columns = df.columns.tolist()
    total_rows = len(df)
    
    # Convert DataFrame to list of tuples
    data = [tuple(row) for row in df.values]
    
    # Create insert query
    insert_query = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    
    # Insert in batches with progress bar
    with tqdm(total=total_rows, desc=f"   Inserting into {table_name}", unit=" rows") as pbar:
        for i in range(0, total_rows, batch_size):
            batch = data[i:i + batch_size]
            try:
                execute_values(cursor, insert_query, batch)
                conn.commit()
                pbar.update(len(batch))
            except Exception as e:
                print(f"\n   ⚠️  Error inserting batch at row {i}: {e}")
                conn.rollback()
                continue

def load_csv_to_db(data_dir):
    """Load all CSV files into the database"""
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("\n📊 Loading data into PostgreSQL...\n")
        
        total_files = len(TABLE_MAPPINGS)
        loaded_count = 0
        
        # Load in dependency order
        load_order = [
            'product_category_name_translation.csv',
            'olist_customers_dataset.csv',
            'olist_sellers_dataset.csv',
            'olist_products_dataset.csv',
            'olist_orders_dataset.csv',
            'olist_order_items_dataset.csv',
            'olist_order_payments_dataset.csv',
            'olist_order_reviews_dataset.csv',
            'olist_geolocation_dataset.csv'
        ]
        
        for csv_file in load_order:
            table_name = TABLE_MAPPINGS[csv_file]
            file_path = data_dir / csv_file
            
            if not file_path.exists():
                print(f"⚠️  File not found: {csv_file}")
                continue
            
            print(f"📄 Processing {csv_file}...")
            
            # Read CSV
            df = pd.read_csv(file_path, low_memory=False)
            print(f"   Rows: {len(df):,} | Columns: {len(df.columns)}")
            
            # Clean data
            df = clean_dataframe(df, table_name)
            
            # Insert into database
            insert_data(conn, cursor, table_name, df)
            
            loaded_count += 1
            print(f"   ✅ Loaded into '{table_name}'\n")
        
        # Get final counts
        print("\n📊 Database Summary:")
        print("-" * 50)
        
        for table_name in TABLE_MAPPINGS.values():
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   {table_name:<35} {count:>12,} rows")
        
        cursor.close()
        conn.close()
        
        print("-" * 50)
        print(f"\n✅ Successfully loaded {loaded_count}/{total_files} files!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False

def main():
    print("=" * 60)
    print("  Olist Data Loader")
    print("=" * 60)
    
    # Check if data directory exists
    data_dir = Path(__file__).parent.parent / "data"
    if not data_dir.exists():
        print(f"\n❌ Data directory not found: {data_dir}")
        print("\n📝 Please run: python scripts/download_dataset.py first")
        sys.exit(1)
    
    # Check if CSV files exist
    csv_files = list(data_dir.glob("*.csv"))
    if len(csv_files) == 0:
        print(f"\n❌ No CSV files found in: {data_dir}")
        print("\n📝 Please run: python scripts/download_dataset.py first")
        sys.exit(1)
    
    print(f"\n📁 Data directory: {data_dir}")
    print(f"📄 Found {len(csv_files)} CSV files")
    
    # Load data
    success = load_csv_to_db(data_dir)
    
    if success:
        print("\n✨ Data loading complete!")
        print("\n📝 Next steps:")
        print("   1. Connect to PostgreSQL and explore the data")
        print("   2. Test some queries:")
        print("      - SELECT * FROM order_summary LIMIT 10;")
        print("      - SELECT COUNT(*) FROM orders;")
        print("   3. Start building the agent system!")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
