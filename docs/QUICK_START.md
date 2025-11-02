# Quick Start Guide - Separated Frontend/Backend

This project has been reorganized into separate frontend and backend folders for deployment on Vercel (frontend) and Render (backend).

## Project Structure

```
nrrc_arabic_pov_windows/
├── backend/              # FastAPI backend for Render
│   ├── app/
│   │   ├── api.py       # Main API with CORS
│   │   ├── auth.py      # Authentication
│   │   └── ...
│   ├── data/            # Indices and documents
│   ├── scripts/         # Processing scripts
│   ├── requirements.txt
│   ├── start.sh         # Render startup script
│   └── README.md
│
├── frontend/            # HTML/CSS/JS for Vercel
│   ├── index.html       # Single-page application
│   └── README.md
│
└── deploy.txt          # Full deployment instructions
```

## Quick Deployment Steps

### 1. Deploy Backend to Render

1. Push code to GitHub
2. Go to https://dashboard.render.com
3. Click "New +" > "Web Service"
4. Connect your GitHub repository
5. Configure:
   - Name: `nrrc-backend`
   - Root Directory: `backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `bash start.sh`
6. Add Environment Variables:
   - `SECRET_KEY`: (generate a random string)
   - `PYTHONIOENCODING`: `utf-8`
7. Click "Create Web Service"
8. Wait for deployment and note your URL: `https://your-backend.onrender.com`

### 2. Deploy Frontend to Vercel

1. Update `frontend/index.html` line with your backend URL:
   ```javascript
   const API_URL = 'https://your-backend.onrender.com';
   ```
2. Commit and push to GitHub
3. Go to https://vercel.com/dashboard
4. Click "Add New" > "Project"
5. Import your GitHub repository
6. Configure:
   - Framework Preset: `Other`
   - Root Directory: `frontend`
   - Build Command: (leave empty)
7. Click "Deploy"
8. Note your frontend URL: `https://your-project.vercel.app`

### 3. Update Backend CORS

1. Edit `backend/app/api.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-project.vercel.app"],
       # ... rest stays same
   )
   ```
2. Commit and push
3. Render will auto-redeploy

### 4. Test

1. Open your Vercel frontend URL
2. Login with: `admin` / `admin123`
3. Try a search query
4. Verify results appear

## Alternative: Keep Existing Structure

If you want to keep using the monolithic structure:

```bash
# Run from root directory as before
uvicorn app.run_api:app --host 0.0.0.0 --port 8000 --reload
```

The original `app/` folder in root still works for local development.

## Important Notes

1. **Two Deployments**: Frontend (Vercel) and Backend (Render) are separate
2. **CORS**: Backend must allow your frontend origin
3. **Environment Variables**: Set in platform dashboards
4. **Git**: Both folders are tracked separately
5. **Data**: `backend/data/` should be committed to Git for initial deployment

## Troubleshooting

- **CORS errors**: Check backend CORS settings match frontend URL
- **Connection refused**: Verify backend URL in frontend code
- **Auth fails**: Check SECRET_KEY is set in Render
- **Slow queries**: Upgrade Render plan or optimize models

For detailed instructions, see `deploy.txt`.

## Local Development

### Backend Only
```bash
cd backend
pip install -r requirements.txt
uvicorn app.api:app --reload
```

### Full Stack (Original)
```bash
# From root directory
uvicorn app.run_api:app --reload
```

### Frontend Only
```bash
cd frontend
python -m http.server 3000
# Update API_URL to http://localhost:8000
```

## Support

- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Full Deployment Guide: `deploy.txt`

