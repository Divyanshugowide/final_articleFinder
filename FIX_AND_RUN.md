# 🔧 Fix and Run Guide

## ✅ Good News: All Code is Working!

All imports are successful. The issue is likely configuration or startup steps.

## 🚀 Quick Fix & Run

### Step 1: Start Backend

**Option A: Using Batch File (Easiest)**
```bash
cd backend
start_backend.bat
```

**Option B: Using Python Script**
```bash
cd backend
python run.py
```

**Option C: Direct Uvicorn**
```bash
cd backend
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
[Loading BM25 + FAISS + model...]
[OK] System ready
```

### Step 2: Start Frontend

**Open a NEW terminal:**
```bash
cd frontend
python -m http.server 3000
```

**Or use:**
```bash
cd frontend
python -m http.server 8080
```

### Step 3: Access Application

- **Frontend**: http://localhost:3000 (or 8080)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔍 Common Issues & Fixes

### Issue 1: "Module not found"
**Fix:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue 2: "Port already in use"
**Fix:** 
- Close other programs using port 8000
- Or change port: `uvicorn app.api:app --port 8001`

### Issue 3: "Data files not found"
**Fix:**
```bash
# Check if indices exist
cd backend
dir data\idx\

# If missing, run indexing scripts
python scripts\02_extract_and_chunk.py
python scripts\03_build_bm25.py
python scripts\04_build_faiss.py
```

### Issue 4: "Frontend can't connect"
**Fix:**
1. Check backend is running: http://localhost:8000/health
2. Update API_URL in `frontend/index.html` (line ~808)
3. Make sure both are running

### Issue 5: "CORS errors"
**Fix:**
- Already configured in `backend/app/api.py`
- Make sure backend allows your frontend origin

## 🧪 Test if Backend is Running

```bash
# Test health endpoint
curl http://localhost:8000/health

# Or in browser:
# http://localhost:8000/health
```

Should return:
```json
{"status": "healthy", "message": "System is ready"}
```

## 📋 Verification Checklist

- [ ] Backend starts without errors
- [ ] Health endpoint responds
- [ ] Frontend starts on different port
- [ ] Frontend can access backend API
- [ ] Login works
- [ ] Search works
- [ ] Admin can upload PDFs

## 🎯 Quick Test Commands

```bash
# Test backend
cd backend
python test_imports.py

# Start backend
python run.py

# In another terminal, start frontend
cd frontend
python -m http.server 3000
```

## 💡 Pro Tips

1. **Always run backend first** - It needs to load indices
2. **Check terminal output** - Look for error messages
3. **Use two terminals** - One for backend, one for frontend
4. **Check ports** - Make sure 8000 and 3000 are free

## 🔗 Quick Links

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Frontend: http://localhost:3000

If still having issues, share the exact error message!

