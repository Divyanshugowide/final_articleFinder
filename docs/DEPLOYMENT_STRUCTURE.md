# Deployment Structure Summary

## Project Reorganization

Your NRRC Arabic PoV project has been reorganized into separate frontend and backend directories to support deployment on different platforms.

## Folder Structure

```
nrrc_arabic_pov_windows/
├── backend/                   # Deploy to Render
│   ├── app/
│   │   ├── api.py            # API with CORS (NEW)
│   │   ├── run_api.py        # Original (with embedded frontend)
│   │   ├── auth.py
│   │   ├── retrieval.py
│   │   └── ... (all other modules)
│   ├── data/                 # Indices, processed data, PDFs
│   ├── conf/                 # Configuration files
│   ├── scripts/              # Processing scripts
│   ├── eval/                 # Evaluation data
│   ├── requirements.txt
│   ├── start.sh              # Render startup script
│   ├── Dockerfile
│   └── README.md
│
├── frontend/                  # Deploy to Vercel
│   ├── index.html            # Standalone web app
│   ├── vercel.json           # Vercel configuration
│   └── README.md
│
├── app/                      # Original (still works for local dev)
│   ├── run_api.py           # Monolithic version
│   └── ... (all modules)
│
├── data/                     # Original data folder
├── conf/                     # Original conf folder
├── scripts/                  # Original scripts
├── eval/                     # Original eval folder
│
├── deploy.txt               # Detailed deployment guide
├── QUICK_START.md           # Quick reference
├── DEPLOYMENT_STRUCTURE.md  # This file
├── .gitignore               # Git ignore rules
└── README.md               # Main project README
```

## Key Files

### Backend (Render)
- `backend/app/api.py` - FastAPI app with CORS middleware for frontend integration
- `backend/start.sh` - Startup script for Render deployment
- `backend/requirements.txt` - Python dependencies

### Frontend (Vercel)
- `frontend/index.html` - Complete single-page application
- `frontend/vercel.json` - Vercel configuration and routing

### Deployment Guides
- `deploy.txt` - Comprehensive step-by-step deployment instructions
- `QUICK_START.md` - Quick reference for fast deployment
- `DEPLOYMENT_STRUCTURE.md` - This file (structure overview)

## Deployment Options

### Option 1: Separate Deployment (Recommended)
- **Backend**: Render (https://render.com)
- **Frontend**: Vercel (https://vercel.com)
- **Benefits**: 
  - Best performance
  - Independent scaling
  - Cost-effective
  - Modern workflow

### Option 2: Monolithic Deployment
- **Platform**: Render, Railway, Fly.io, or AWS
- **Use**: `backend/app/run_api.py` or original `app/run_api.py`
- **Benefits**: 
  - Simpler deployment
  - Single service
  - Good for prototyping

### Option 3: Docker
- **Files**: `backend/Dockerfile` or root `Dockerfile`
- **Platform**: Any container platform
- **Benefits**: 
  - Consistent environment
  - Easy scaling
  - Portable

## Migration Notes

### What Changed
1. Created `backend/app/api.py` - Separate API without embedded HTML
2. Added CORS middleware for cross-origin requests
3. Created `frontend/index.html` - Standalone frontend app
4. Configured frontend to call backend API
5. Added deployment scripts and configs

### What Stayed the Same
1. All business logic unchanged
2. Original `app/` folder still works
3. Data structure compatible
4. Authentication unchanged
5. RBAC system intact

## Testing Checklist

Before deploying, verify:

- [ ] Backend starts locally: `cd backend && uvicorn app.api:app --reload`
- [ ] Frontend connects: Update API_URL in `frontend/index.html` to `http://localhost:8000`
- [ ] Login works: Test with admin/legal/staff accounts
- [ ] Search works: Perform a test query
- [ ] RBAC works: Try different roles
- [ ] Data loads: Check indices are present

## Configuration Required

### Before Deployment

1. **Backend** (`backend/app/api.py`):
   - Update CORS origins with your Vercel URL
   - Set SECRET_KEY environment variable

2. **Frontend** (`frontend/index.html`):
   - Update API_URL constant with your Render URL

3. **Both**:
   - Ensure environment variables are set in platforms
   - Verify file paths are correct

## Deployment Workflow

### Initial Setup
1. Push code to GitHub
2. Deploy backend to Render
3. Get backend URL
4. Deploy frontend to Vercel
5. Update CORS in backend
6. Test end-to-end

### Updates
1. Push changes to GitHub
2. Both platforms auto-deploy
3. Test in production

### Rollback
1. Vercel: Use deployment history to rollback
2. Render: Use manual deployment or previous release
3. Both: Keep multiple deployments for safety

## Environment Variables

### Backend (Render)
```
SECRET_KEY=your-secret-key
PYTHONIOENCODING=utf-8
TRANSFORMERS_CACHE=/app/.cache/transformers
```

### Frontend (Vercel)
```
REACT_APP_API_URL=https://your-backend.onrender.com
```

## Support & Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Project Docs**: `deploy.txt` for full instructions

## Next Steps

1. Read `QUICK_START.md` for fast deployment
2. Follow `deploy.txt` for detailed steps
3. Test locally before deploying
4. Monitor logs for issues
5. Optimize as needed

## Questions?

Check the deployment guides or project documentation for answers to common questions.

Good luck with your deployment! 🚀

