"""
Download Olist Brazilian E-Commerce dataset from Kaggle
Requires: kaggle.json API credentials in ~/.kaggle/ or %USERPROFILE%/.kaggle/
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

load_dotenv()

def download_dataset():
    """Download the Olist dataset from Kaggle"""
    
    # Create data directory if it doesn't exist
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    print("🔍 Checking Kaggle credentials...")
    
    # Check if Kaggle credentials are set
    kaggle_username = os.getenv("KAGGLE_USERNAME")
    kaggle_key = os.getenv("KAGGLE_KEY")
    
    if kaggle_username and kaggle_key:
        os.environ["KAGGLE_USERNAME"] = kaggle_username
        os.environ["KAGGLE_KEY"] = kaggle_key
        print("✅ Using Kaggle credentials from .env file")
    else:
        kaggle_config = Path.home() / ".kaggle" / "kaggle.json"
        if not kaggle_config.exists():
            print("\n❌ Kaggle credentials not found!")
            print("\nPlease do ONE of the following:")
            print("1. Add KAGGLE_USERNAME and KAGGLE_KEY to your .env file")
            print("2. Download kaggle.json from https://www.kaggle.com/settings")
            print(f"   and place it in: {kaggle_config.parent}")
            return False
        print("✅ Using Kaggle credentials from kaggle.json")
    
    try:
        import kaggle
        
        print(f"\n📥 Downloading dataset to {data_dir}...")
        print("This may take a few minutes (126 MB)...\n")
        
        # Download the dataset
        kaggle.api.dataset_download_files(
            'olistbr/brazilian-ecommerce',
            path=str(data_dir),
            unzip=True
        )
        
        print("\n✅ Dataset downloaded successfully!")
        
        # List downloaded files
        csv_files = list(data_dir.glob("*.csv"))
        print(f"\n📄 Found {len(csv_files)} CSV files:")
        for file in sorted(csv_files):
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"   - {file.name} ({size_mb:.2f} MB)")
        
        return True
        
    except ImportError:
        print("❌ Kaggle package not installed. Run: pip install kaggle")
        return False
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  Olist Dataset Downloader")
    print("=" * 60)
    
    success = download_dataset()
    
    if success:
        print("\n✨ Next steps:")
        print("   1. Review the CSV files in the 'data' folder")
        print("   2. Run: python scripts/setup_database.py")
        print("   3. Run: python scripts/load_data.py")
    
    sys.exit(0 if success else 1)
