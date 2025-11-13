"""
Quick test to verify database is working with sample queries
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

sys.path.append(str(Path(__file__).parent.parent))
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'olist_ecommerce'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

def test_queries():
    """Run sample queries to verify database works"""
    
    conn_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    engine = create_engine(conn_string)
    
    print("=" * 70)
    print(" " * 20 + "DATABASE TEST QUERIES")
    print("=" * 70)
    
    with engine.connect() as conn:
        
        # Query 1: Top 5 Product Categories by Sales
        print("\n📊 Top 5 Product Categories by Sales:\n")
        query1 = text("""
            SELECT 
                COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown') as category,
                COUNT(DISTINCT oi.order_id) as total_orders,
                SUM(oi.price) as total_revenue,
                ROUND(AVG(oi.price), 2) as avg_price
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            LEFT JOIN product_category_translation t 
                ON p.product_category_name = t.product_category_name
            GROUP BY category
            ORDER BY total_revenue DESC
            LIMIT 5;
        """)
        
        result = conn.execute(query1)
        print(f"{'Category':<30} {'Orders':<10} {'Revenue':<15} {'Avg Price'}")
        print("-" * 70)
        for row in result:
            print(f"{row[0]:<30} {row[1]:<10} R${row[2]:>12,.2f}  R${row[3]:>6,.2f}")
        
        # Query 2: Orders by State
        print("\n\n🗺️  Top 5 States by Number of Orders:\n")
        query2 = text("""
            SELECT 
                c.customer_state,
                COUNT(DISTINCT o.order_id) as total_orders,
                COUNT(DISTINCT c.customer_id) as total_customers
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_state
            ORDER BY total_orders DESC
            LIMIT 5;
        """)
        
        result = conn.execute(query2)
        print(f"{'State':<10} {'Orders':<10} {'Customers'}")
        print("-" * 35)
        for row in result:
            print(f"{row[0]:<10} {row[1]:<10,} {row[2]:,}")
        
        # Query 3: Payment Methods
        print("\n\n💳 Payment Method Distribution:\n")
        query3 = text("""
            SELECT 
                payment_type,
                COUNT(*) as transactions,
                SUM(payment_value) as total_value,
                ROUND(AVG(payment_installments), 1) as avg_installments
            FROM order_payments
            GROUP BY payment_type
            ORDER BY transactions DESC;
        """)
        
        result = conn.execute(query3)
        print(f"{'Payment Type':<15} {'Transactions':<15} {'Total Value':<15} {'Avg Installments'}")
        print("-" * 70)
        for row in result:
            print(f"{row[0]:<15} {row[1]:<15,} R${row[2]:>12,.2f}  {row[3]:>6}")
        
        # Query 4: Monthly Sales Trend (last 6 months of data)
        print("\n\n📈 Monthly Sales Trend (Last 6 Months):\n")
        query4 = text("""
            SELECT 
                TO_CHAR(order_purchase_timestamp, 'YYYY-MM') as month,
                COUNT(DISTINCT o.order_id) as orders,
                SUM(oi.price) as revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY month
            ORDER BY month DESC
            LIMIT 6;
        """)
        
        result = conn.execute(query4)
        print(f"{'Month':<10} {'Orders':<10} {'Revenue'}")
        print("-" * 40)
        for row in result:
            print(f"{row[0]:<10} {row[1]:<10,} R${row[2]:>12,.2f}")
        
        # Query 5: Seller Performance
        print("\n\n🏪 Top 5 Sellers by Revenue:\n")
        query5 = text("""
            SELECT 
                s.seller_id,
                s.seller_city,
                s.seller_state,
                COUNT(DISTINCT oi.order_id) as orders,
                SUM(oi.price) as revenue
            FROM sellers s
            JOIN order_items oi ON s.seller_id = oi.seller_id
            GROUP BY s.seller_id, s.seller_city, s.seller_state
            ORDER BY revenue DESC
            LIMIT 5;
        """)
        
        result = conn.execute(query5)
        print(f"{'Seller ID':<35} {'City':<20} {'ST':<5} {'Orders':<8} {'Revenue'}")
        print("-" * 95)
        for row in result:
            seller_id_short = row[0][:30] + "..." if len(row[0]) > 30 else row[0]
            print(f"{seller_id_short:<35} {row[1]:<20} {row[2]:<5} {row[3]:<8,} R${row[4]:>12,.2f}")
    
    print("\n" + "=" * 70)
    print("✅ All queries executed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_queries()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
