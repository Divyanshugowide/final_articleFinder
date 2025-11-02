# 🚀 Deployment Checklist for Render + Vercel

## ✅ Pre-Deployment Verification

### Backend (Render) - Ready ✅
- [x] `backend/start.sh` exists and is executable
- [x] `backend/requirements.txt` is complete
- [x] `backend/app/api.py` has CORS middleware configured
- [x] Environment variables can be set in Render dashboard
- [x] Health check endpoint (`/health`) is available
- [x] Data indices (`data/idx/`) are committed to Git

### Frontend (Vercel) - Needs Update ⚠️
- [x] `frontend/index.html` exists
- [x] `frontend/vercel.json` is configured
- [⚠️] **API_URL needs to be updated** with your Render backend URL
- [x] Static files structure is correct

---

## 📋 Step-by-Step Deployment

### PART 1: Backend Deployment on Render

#### Step 1: Prepare Repository
```bash
# Ensure all files are committed
git add .
git commit -m "Prepare for deployment"
git push origin main
```

#### Step 2: Create Render Web Service
1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `nrrc-backend` (or your preferred name)
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `bash start.sh`
   - **Plan**: Choose your plan (Free tier available)

#### Step 3: Set Environment Variables in Render
Go to **Environment** tab and add:
```
PYTHONIOENCODING=utf-8
TRANSFORMERS_CACHE=/opt/render/.cache/transformers
CORS_ORIGINS=https://your-frontend.vercel.app
SECRET_KEY=your-strong-secret-key-here-generate-random-string
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Step 4: Deploy
1. Click **"Create Web Service"**
2. Wait for deployment to complete (~5-10 minutes)
3. **Note your backend URL**: `https://nrrc-backend-xxxx.onrender.com`

#### Step 5: Verify Backend
1. Open: `https://your-backend-url.onrender.com/health`
2. Should return: `{"status": "ok"}`
3. Open: `https://your-backend-url.onrender.com/api/info`
4. Should return API information

---

### PART 2: Frontend Deployment on Vercel

#### Step 1: Update API URL in Frontend

**IMPORTANT:** Update `frontend/index.html` line ~853:
```javascript
// Change this:
API_URL = 'https://your-render-backend-url.onrender.com';

// To your actual Render URL:
API_URL = 'https://nrrc-backend-xxxx.onrender.com';
```

Or set environment variable in Vercel (see Step 3).

#### Step 2: Prepare for Vercel
```bash
# Ensure changes are committed
git add frontend/index.html
git commit -m "Update API URL for deployment"
git push origin main
```

#### Step 3: Create Vercel Project
1. Go to https://vercel.com/dashboard
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: `Other`
   - **Root Directory**: `frontend`
   - **Build Command**: (leave empty for static HTML)
   - **Output Directory**: `.` (or leave empty)
   - **Install Command**: (leave empty)

#### Step 4: Set Environment Variables (Optional)
If you want to use environment variables instead of hardcoding:

Go to **Settings** → **Environment Variables**:
```
API_URL=https://your-render-backend-url.onrender.com
```

Then update `frontend/index.html` to read from `window.API_URL` (already configured).

#### Step 5: Deploy
1. Click **"Deploy"**
2. Wait for deployment (~1-2 minutes)
3. **Note your frontend URL**: `https://your-project.vercel.app`

#### Step 6: Update CORS in Render
1. Go back to Render dashboard
2. Go to your backend service → **Environment**
3. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=https://your-project.vercel.app
   ```
4. Save and wait for redeployment

---

## 🔍 Post-Deployment Testing

### Test Backend
```bash
# Health check
curl https://your-backend.onrender.com/health

# API info
curl https://your-backend.onrender.com/api/info

# Test login (should return 422 without body)
curl -X POST https://your-backend.onrender.com/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Test Frontend
1. Open: `https://your-frontend.vercel.app`
2. Try logging in with test accounts:
   - `admin` / `admin123`
   - `legal` / `legal123`
   - `staff` / `staff123`
3. Perform a test search
4. Verify role-based UI themes appear
5. Test admin PDF upload (if admin user)

---

## ⚠️ Important Notes

### Render Free Tier Limitations
- Services may spin down after 15 minutes of inactivity
- First request after spin-down may be slow (~30 seconds)
- Consider upgrading for production use

### Vercel Free Tier
- Excellent for static frontends
- Auto-scaling
- Custom domains available

### Data/Indices
- Ensure `backend/data/idx/` folder is committed to Git
- Indices will be available after Render deployment
- For large indices, consider using Render Disk or external storage

### CORS Configuration
- Current setup allows all origins (`*`) - works but less secure
- Update `CORS_ORIGINS` in Render with specific Vercel URL for production
- Supports comma-separated list for multiple domains

### Environment Variables Summary

**Render (Backend):**
```
PYTHONIOENCODING=utf-8
TRANSFORMERS_CACHE=/opt/render/.cache/transformers
CORS_ORIGINS=https://your-frontend.vercel.app
SECRET_KEY=your-generated-secret-key
```

**Vercel (Frontend):**
```
API_URL=https://your-backend.onrender.com
```
(Optional - can also hardcode in index.html)

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: Backend fails to start
- Check Render logs for errors
- Verify `start.sh` is executable
- Ensure `requirements.txt` is correct
- Check Python version compatibility

**Problem**: Indices not found
- Verify `data/idx/` folder is in Git repository
- Check file paths in code (should be relative)
- Ensure indices are committed and pushed

**Problem**: CORS errors
- Verify `CORS_ORIGINS` includes your Vercel URL
- Check browser console for exact error
- Ensure credentials are properly handled

### Frontend Issues

**Problem**: Can't connect to backend
- Verify API_URL is correct in `index.html`
- Check if backend is running (might be spun down)
- Verify CORS is configured correctly
- Check browser console for errors

**Problem**: 401 Unauthorized errors
- Verify JWT token is being sent in headers
- Check if token expired (default: 30 minutes)
- Ensure login endpoint works

**Problem**: Static assets not loading
- Check `vercel.json` configuration
- Verify file paths are correct
- Clear browser cache

---

## ✅ Final Checklist

Before going live:
- [ ] Backend deployed and health check passes
- [ ] Frontend deployed and loads correctly
- [ ] Login works with test accounts
- [ ] Search functionality works
- [ ] Role-based UI themes display correctly
- [ ] Admin PDF upload works (if applicable)
- [ ] CORS properly configured
- [ ] Environment variables set correctly
- [ ] Indices are accessible
- [ ] SSL certificates working (HTTPS)
- [ ] Error handling works
- [ ] Mobile responsive design verified

---

## 📞 Support Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Project README**: See `README.md` for more info

---

## 🎉 You're Ready!

Once all steps are completed, your application should be live and accessible from anywhere!

**Backend URL**: `https://your-backend.onrender.com`
**Frontend URL**: `https://your-frontend.vercel.app`

Good luck with your deployment! 🚀
