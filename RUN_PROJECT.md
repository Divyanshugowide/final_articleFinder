# 🚀 How to Run Your Project

## ✅ Everything is Fixed and Ready!

All code has been tested and is working. Follow these simple steps:

## Quick Start (3 Steps)

### 1️⃣ Start Backend (Terminal 1)

```bash
cd backend
python run.py
```

**Wait for this message:**
```
[OK] System ready
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2️⃣ Start Frontend (Terminal 2)

Open a **NEW terminal window**:

```bash
cd frontend
python -m http.server 3000
```

### 3️⃣ Open Browser

Go to: **http://localhost:3000**

## 🎯 Login Test

| Role | Username | Password | What You'll See |
|------|----------|----------|-----------------|
| Admin | admin | admin123 | 👑 Premium Purple UI + Upload Panel |
| Legal | legal | legal123 | ⚖️ Green Professional UI |
| Staff | staff | staff123 | 📄 Blue Standard UI |

## 🔧 If Something Goes Wrong

### Backend Not Starting?

1. **Check Python:**
   ```bash
   python --version  # Should be 3.11+
   ```

2. **Install Dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Check Data Files:**
   ```bash
   dir backend\data\idx\  # Should have bm25.pkl, mE5.faiss, meta.json
   ```

4. **Test Imports:**
   ```bash
   cd backend
   python test_imports.py
   ```

### Frontend Not Connecting?

1. **Check Backend is Running:**
   - Open: http://localhost:8000/health
   - Should see: `{"status":"healthy","message":"System is ready"}`

2. **Update API URL:**
   - Edit `frontend/index.html` line ~808
   - Make sure it says: `http://localhost:8000`

3. **Check Browser Console:**
   - Press F12 → Console tab
   - Look for errors

## 📊 Verify Everything Works

### Test Backend:
```bash
# In browser or curl:
http://localhost:8000/health
http://localhost:8000/
http://localhost:8000/docs
```

### Test Frontend:
- Open http://localhost:3000
- Should see login page
- Try logging in
- Should see themed interface based on role

## 🎨 What to Expect

### Admin (Premium):
- Purple/violet theme
- Crown icon 👑
- "Premium" badge
- Admin panel with PDF upload
- Enhanced animations

### Legal:
- Green professional theme
- Legal badge ⚖️
- Access to restricted docs

### Staff:
- Blue standard theme
- Staff badge 📄
- General access only

## 📝 Quick Commands Reference

```bash
# Backend
cd backend
python run.py

# Frontend (new terminal)
cd frontend  
python -m http.server 3000

# Test imports
cd backend
python test_imports.py

# Check health
curl http://localhost:8000/health
```

## ✨ That's It!

Your project is fully organized, themed, and ready to run. Just start backend and frontend in separate terminals!

Need help? Check `FIX_AND_RUN.md` for detailed troubleshooting.

