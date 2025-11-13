"""
Explore the Olist dataset before loading into database
Shows sample data, column info, and basic statistics
"""

import sys
from pathlib import Path
import pandas as pd

def explore_csv(file_path):
    """Explore a single CSV file"""
    print(f"\n{'='*80}")
    print(f"📄 {file_path.name}")
    print(f"{'='*80}\n")
    
    try:
        # Read CSV with sample
        df = pd.read_csv(file_path, nrows=100000)  # Limit for large files
        
        # Basic info
        print(f"📊 Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
        print(f"💾 Memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n")
        
        # Column info
        print("📋 Columns:")
        print("-" * 80)
        for i, col in enumerate(df.columns, 1):
            dtype = df[col].dtype
            nulls = df[col].isna().sum()
            null_pct = (nulls / len(df)) * 100
            unique = df[col].nunique()
            
            print(f"{i:2}. {col:<40} {str(dtype):<15} "
                  f"Nulls: {null_pct:5.1f}% | Unique: {unique:,}")
        
        # Sample data
        print(f"\n🔍 First 3 rows:")
        print("-" * 80)
        print(df.head(3).to_string())
        
        # Statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            print(f"\n📈 Numeric Statistics:")
            print("-" * 80)
            print(df[numeric_cols].describe().to_string())
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def main():
    print("=" * 80)
    print(" " * 25 + "OLIST DATASET EXPLORER")
    print("=" * 80)
    
    data_dir = Path(__file__).parent.parent / "data"
    
    if not data_dir.exists():
        print(f"\n❌ Data directory not found: {data_dir}")
        print("\n📝 Please run: python scripts/download_dataset.py first")
        sys.exit(1)
    
    csv_files = sorted(data_dir.glob("*.csv"))
    
    if len(csv_files) == 0:
        print(f"\n❌ No CSV files found in: {data_dir}")
        print("\n📝 Please run: python scripts/download_dataset.py first")
        sys.exit(1)
    
    print(f"\n📁 Data directory: {data_dir}")
    print(f"📄 Found {len(csv_files)} CSV files\n")
    
    # Explore each file
    for csv_file in csv_files:
        explore_csv(csv_file)
    
    print("\n" + "=" * 80)
    print("✨ Exploration complete!")
    print("\n📝 Next step: python scripts/setup_database.py")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
