# ⚡ Quick Deployment Guide

## 🎯 Before You Start

1. **Backend URL** will be: `https://your-project-name.onrender.com`
2. **Frontend URL** will be: `https://your-project-name.vercel.app`
3. You need to **update one line** in `frontend/index.html` after backend deployment

---

## 📦 Backend on Render (5 minutes)

1. Go to https://dashboard.render.com → **"New +"** → **"Web Service"**
2. Connect GitHub repo
3. Settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `bash start.sh`
4. Environment Variables:
   ```
   PYTHONIOENCODING=utf-8
   CORS_ORIGINS=*
   ```
5. Click **"Create Web Service"**
6. Wait ~5 minutes, then copy your backend URL

---

## 🌐 Frontend on Vercel (2 minutes)

1. Go to https://vercel.com/dashboard → **"Add New"** → **"Project"**
2. Import GitHub repo
3. Settings:
   - **Root Directory**: `frontend`
   - **Framework**: Other
   - **Build Command**: (leave empty)
4. **IMPORTANT**: Before deploying, update `frontend/index.html` line ~865:
   ```javascript
   // Change this:
   'https://your-render-backend-url.onrender.com'
   
   // To your actual Render URL:
   'https://your-project-name.onrender.com'
   ```
5. Commit and push, then click **"Deploy"**
6. Copy your frontend URL

---

## ✅ Done!

Your app is live! Open your Vercel URL to test.

For detailed steps, see `DEPLOYMENT_CHECKLIST.md`
