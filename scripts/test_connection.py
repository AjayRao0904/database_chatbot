"""
Test database connectivity and show basic stats
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))
load_dotenv()

def test_connection():
    """Test PostgreSQL connection"""
    
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'olist_ecommerce'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', '')
    }
    
    print("=" * 60)
    print("  Database Connection Test")
    print("=" * 60)
    
    print(f"\n📍 Connection Details:")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   Port: {DB_CONFIG['port']}")
    print(f"   Database: {DB_CONFIG['database']}")
    print(f"   User: {DB_CONFIG['user']}")
    
    try:
        import psycopg2
        
        print("\n🔌 Attempting to connect...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Connection successful!\n")
        
        # Get PostgreSQL version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"🐘 PostgreSQL Version:")
        print(f"   {version.split(',')[0]}\n")
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"📊 Found {len(tables)} tables:")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   ✓ {table[0]:<35} {count:>12,} rows")
            
            print("\n✨ Database is ready!")
            print("\n📝 Try running some queries:")
            print("   psql -U postgres -d olist_ecommerce")
            print("   SELECT * FROM order_summary LIMIT 5;")
            
        else:
            print("⚠️  No tables found. Database schema not created yet.")
            print("\n📝 Next step: python scripts/setup_database.py")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed. Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure PostgreSQL is running")
        print("   2. Check your credentials in .env file")
        print("   3. Verify database exists")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
