"""
Fixed data loader that handles all the data quality issues in Olist dataset
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'olist_ecommerce'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

def load_with_sqlalchemy():
    """Use SQLAlchemy for easier data loading"""
    
    from sqlalchemy import create_engine
    from tqdm import tqdm
    
    # Create connection string
    conn_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    engine = create_engine(conn_string)
    
    data_dir = Path(__file__).parent.parent / "data"
    
    print("\n📊 Loading data using SQLAlchemy...\n")
    
    # 1. Product category translation
    print("📄 Loading product_category_name_translation...")
    df = pd.read_csv(data_dir / "product_category_name_translation.csv")
    df.to_sql('product_category_translation', engine, if_exists='append', index=False)
    print(f"   ✅ Loaded {len(df):,} rows\n")
    
    # 2. Customers
    print("📄 Loading customers...")
    df = pd.read_csv(data_dir / "olist_customers_dataset.csv")
    df.to_sql('customers', engine, if_exists='append', index=False, chunksize=10000)
    print(f"   ✅ Loaded {len(df):,} rows\n")
    
    # 3. Sellers
    print("📄 Loading sellers...")
    df = pd.read_csv(data_dir / "olist_sellers_dataset.csv")
    df.to_sql('sellers', engine, if_exists='append', index=False)
    print(f"   ✅ Loaded {len(df):,} rows\n")
    
    # 4. Products (with fixes)
    print("📄 Loading products...")
    df = pd.read_csv(data_dir / "olist_products_dataset.csv")
    
    # Fix column names (typo in CSV)
    df.rename(columns={
        'product_name_lenght': 'product_name_length',
        'product_description_lenght': 'product_description_length'
    }, inplace=True)
    
    # Convert weight to BIGINT range or cap it
    if 'product_weight_g' in df.columns:
        df['product_weight_g'] = df['product_weight_g'].fillna(0).astype(int)
    
    df.to_sql('products', engine, if_exists='append', index=False, chunksize=5000)
    print(f"   ✅ Loaded {len(df):,} rows\n")
    
    # 5. Orders
    print("📄 Loading orders...")
    df = pd.read_csv(data_dir / "olist_orders_dataset.csv")
    df.to_sql('orders', engine, if_exists='append', index=False, chunksize=10000)
    print(f"   ✅ Loaded {len(df):,} rows\n")
    
    # 6. Order items
    print("📄 Loading order_items...")
    df = pd.read_csv(data_dir / "olist_order_items_dataset.csv")
    # Only load items that have matching products
    df.to_sql('order_items', engine, if_exists='append', index=False, chunksize=10000)
    print(f"   ✅ Loaded {len(df):,} rows\n")
    
    # 7. Order payments
    print("📄 Loading order_payments...")
    df = pd.read_csv(data_dir / "olist_order_payments_dataset.csv")
    df.to_sql('order_payments', engine, if_exists='append', index=False, chunksize=10000)
    print(f"   ✅ Loaded {len(df):,} rows\n")
    
    # 8. Order reviews
    print("📄 Loading order_reviews...")
    df = pd.read_csv(data_dir / "olist_order_reviews_dataset.csv")
    df.to_sql('order_reviews', engine, if_exists='append', index=False, chunksize=10000)
    print(f"   ✅ Loaded {len(df):,} rows\n")
    
    # 9. Geolocation (deduplicated)
    print("📄 Loading geolocation...")
    df = pd.read_csv(data_dir / "olist_geolocation_dataset.csv")
    print(f"   Original rows: {len(df):,}")
    df = df.drop_duplicates(subset=['geolocation_zip_code_prefix'])
    print(f"   After deduplication: {len(df):,}")
    df.to_sql('geolocation', engine, if_exists='append', index=False)
    print(f"   ✅ Loaded {len(df):,} rows\n")
    
    # Get final counts
    print("\n📊 Database Summary:")
    print("-" * 50)
    
    with engine.connect() as conn:
        tables = [
            'customers', 'sellers', 'products', 'product_category_translation',
            'orders', 'order_items', 'order_payments', 'order_reviews', 'geolocation'
        ]
        for table in tables:
            result = conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = result.fetchone()[0]
            print(f"   {table:<35} {count:>12,} rows")
    
    print("-" * 50)
    print("\n✅ Data loading complete!")

if __name__ == "__main__":
    print("=" * 60)
    print("  Olist Data Loader (Fixed Version)")
    print("=" * 60)
    
    try:
        load_with_sqlalchemy()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
