# Installation Guide - Fixing Windows Dependency Issues

## ✅ Problem Solved!

The original `requirements.txt` had exact version pins that tried to build pandas from source, which requires Microsoft Visual Studio C++ Build Tools on Windows.

## 🔧 Solution Applied

We've split the dependencies into two files:

### 1. **requirements-minimal.txt** (✅ INSTALLED)
Core packages needed for database setup only:
- `python-dotenv` - Environment variables
- `pandas` - Data processing (pre-built wheel)
- `psycopg2-binary` - PostgreSQL driver
- `kaggle` - Dataset download
- `tqdm` - Progress bars

### 2. **requirements.txt** (For later)
Full agent system dependencies (install after database is working)

## 🚀 You're Ready to Go!

The minimal packages are now installed. You can proceed with:

### **Step 1: Download the Dataset**
```powershell
python scripts\download_dataset.py
```

### **Step 2: Setup PostgreSQL Database**
```powershell
python scripts\setup_database.py
```

### **Step 3: Load Data**
```powershell
python scripts\load_data.py
```

---

## 📝 Before You Start

Make sure you've configured your `.env` file with:

```env
# PostgreSQL credentials
DB_HOST=localhost
DB_PORT=5432
DB_NAME=olist_ecommerce
DB_USER=postgres
DB_PASSWORD=your_postgres_password

# Kaggle API credentials
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
```

### Getting Kaggle Credentials:
1. Go to https://www.kaggle.com/settings
2. Scroll to "API" section
3. Click "Create New Token"
4. Save the username and key to your `.env` file

---

## 🤖 Installing Agent Dependencies (Later)

Once your database is working, install the full agent system:

```powershell
pip install openai langchain langchain-openai langgraph
```

Or install specific packages as needed.

---

## 💡 Why This Works

- **Pre-built wheels**: We use flexible version ranges (`>=`) so pip can find pre-compiled Windows wheels
- **No compilation**: Avoids needing Visual Studio Build Tools
- **Minimal first**: Get the database working before adding AI dependencies

---

## 🐛 If You Still Have Issues

### Issue: "No module named 'X'"
**Solution:** Install the specific package:
```powershell
pip install package-name
```

### Issue: PostgreSQL connection fails
**Solution:** 
1. Make sure PostgreSQL is installed and running
2. Check your password in `.env`
3. Run: `python scripts\test_connection.py`

### Issue: Kaggle download fails
**Solution:**
1. Verify credentials in `.env`
2. Or use kaggle.json in `C:\Users\ajayr\.kaggle\`

---

## ✨ Next Steps

1. ✅ Packages installed
2. ⏭️ Configure `.env` file
3. ⏭️ Download dataset
4. ⏭️ Setup database
5. ⏭️ Start building agents!
