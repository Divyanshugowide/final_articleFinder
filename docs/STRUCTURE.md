# Project Structure

## 📁 Current Organization

```
nrrc_arabic_pov_windows/
│
├── 📂 backend/                     # Main Backend (For Render Deployment)
│   ├── app/
│   │   ├── api.py                 # FastAPI with CORS
│   │   ├── auth.py                # Authentication
│   │   ├── retrieval.py           # Search engine
│   │   └── ... (all modules)
│   ├── data/                      # Indices & documents
│   ├── conf/                      # Config files
│   ├── scripts/                   # Processing scripts
│   ├── eval/                      # Evaluation data
│   ├── requirements.txt
│   ├── start.sh                   # Render startup
│   └── README.md
│
├── 📂 frontend/                    # Main Frontend (For Vercel)
│   ├── index.html                 # Web application
│   ├── vercel.json                # Vercel config
│   └── README.md
│
├── 📂 docs/                        # All Documentation
│   ├── deploy.txt                 # Deployment guide
│   ├── QUICK_START.md             # Quick steps
│   ├── DEPLOYMENT_STRUCTURE.md    # Structure details
│   ├── AWS_DEPLOYMENT_GUIDE.md    # AWS guide
│   └── ... (all docs)
│
├── 📂 archive/                     # Legacy Files (Old Structure)
│   ├── app/                       # Old monolithic structure
│   ├── data/                      # Old data files
│   ├── scripts/                   # Old scripts
│   ├── *.bat, *.ps1              # Old batch files
│   └── requirements.txt           # Old requirements
│
├── README.md                       # Main README
├── LICENSE                         # License file
└── .gitignore                     # Git ignore rules
```

## 🎯 Key Differences

| Item | New Location | Old Location | Purpose |
|------|--------------|--------------|---------|
| Backend Code | `backend/app/` | `archive/app/` | Deploy to Render |
| Frontend | `frontend/` | Embedded in backend | Deploy to Vercel |
| Documentation | `docs/` | Root scattered | All in one place |
| Legacy Files | `archive/` | Root | Preserved for reference |
| Requirements | `backend/requirements.txt` | `archive/requirements.txt` | Backend deps |

## 🚀 What's Active

✅ **Use These:**
- `backend/` - For deployment
- `frontend/` - For deployment
- `docs/` - For documentation

📦 **Archive:**
- `archive/` - Old structure (kept for reference)

## 📚 Documentation Map

| Need | File |
|------|------|
| Quick deployment | `docs/QUICK_START.md` |
| Full deployment guide | `docs/deploy.txt` |
| Structure details | `docs/DEPLOYMENT_STRUCTURE.md` |
| Setup complete | `docs/SETUP_COMPLETE.md` |
| AWS deployment | `docs/AWS_DEPLOYMENT_GUIDE.md` |
| Docker solution | `docs/COMPLETE_DOCKER_SOLUTION.md` |
| RBAC guide | `docs/RBAC_README.md` |
| Backend info | `backend/README.md` |
| Frontend info | `frontend/README.md` |

## 🎨 Best Practices

1. **New Development**: Use `backend/` and `frontend/`
2. **Deployment**: Follow `docs/deploy.txt`
3. **Documentation**: Add to `docs/`
4. **Legacy**: Refer to `archive/` if needed

## 🔄 Migration Notes

### From Old Structure

If you need to work with the old structure:

```bash
cd archive
pip install -r requirements.txt
uvicorn app.run_api:app --reload
```

### To New Structure

```bash
cd backend
pip install -r requirements.txt
uvicorn app.api:app --reload
```

## 📊 Clean Organization Benefits

✅ **Separated Concerns**
- Frontend and backend independent
- Clear deployment paths

✅ **Organized Documentation**
- All docs in one place
- Easy to find references

✅ **Preserved Legacy**
- Old structure archived
- Can reference if needed

✅ **Clean Root**
- Only essential files
- Clear structure

## 🎯 What Each Folder Does

| Folder | Purpose | Deploy To |
|--------|---------|-----------|
| `backend/` | FastAPI backend | Render |
| `frontend/` | Web interface | Vercel |
| `docs/` | Documentation | N/A |
| `archive/` | Legacy files | N/A |

## 📝 File Naming

- `.md` files → Documentation in `docs/`
- `.txt` files → Documentation in `docs/`
- `.py` files → Code in respective folders
- `.json` → Config/data files
- `.bat/.ps1` → Old scripts in `archive/`

---

**Clean, organized, and ready for deployment!** 🚀


