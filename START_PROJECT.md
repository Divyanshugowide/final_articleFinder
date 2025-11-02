# 🚀 Quick Start Guide

## Start the Backend

### Option 1: Using Python Script (Recommended)
```bash
cd backend
python run.py
```

### Option 2: Using Uvicorn Directly
```bash
cd backend
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Using Start Script (Linux/Mac)
```bash
cd backend
bash start.sh
```

## Start the Frontend

### Option 1: Simple HTTP Server
```bash
cd frontend
python -m http.server 3000
```

### Option 2: Using Node.js (if installed)
```bash
cd frontend
npx serve .
```

## Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Test Accounts

| Role | Username | Password | UI Theme |
|------|----------|----------|----------|
| **Admin** | admin | admin123 | 👑 Premium Purple Theme |
| **Legal** | legal | legal123 | ⚖️ Professional Green Theme |
| **Staff** | staff | staff123 | 📄 Standard Blue Theme |

## Features by Role

### 👑 Admin (Premium)
- **Purple/Violet Premium Theme**
- Crown icon and "Premium" badge
- PDF Upload & Processing
- Index Rebuild
- Full access to all documents
- Enhanced UI animations
- Admin control panel

### ⚖️ Legal
- **Professional Green Theme**
- Access to general + restricted documents
- Standard search interface

### 📄 Staff
- **Standard Blue Theme**
- Access to general documents only
- Standard search interface

## Admin Features

### Upload PDF
1. Login as admin
2. Click "📄 اختر ملف PDF للرفع"
3. Select your PDF file
4. Wait for automatic processing:
   - PDF chunking
   - BM25 indexing
   - FAISS indexing
   - Index reload
5. PDF becomes searchable immediately!

### Rebuild Indices
- Click "🔄 إعادة بناء الفهارس"
- Rebuilds all indices from all PDFs
- Useful after bulk uploads or corruption

## Troubleshooting

### Backend Won't Start
1. Check if port 8000 is available
2. Ensure dependencies are installed: `pip install -r requirements.txt`
3. Check if data/idx/ files exist

### Frontend Can't Connect
1. Update API_URL in frontend/index.html (line ~647)
2. Ensure backend is running on port 8000
3. Check CORS settings in backend

### PDF Upload Fails
1. Ensure you're logged in as admin
2. Check file size (large PDFs may take time)
3. Check backend logs for errors

## Next Steps

1. **Upload PDFs**: Use admin panel to add documents
2. **Search**: Try different queries in Arabic or English
3. **Deploy**: Follow deployment guides in `docs/` folder

Happy searching! 🔍

