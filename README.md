# NRRC Arabic PoV - Arabic Document Retrieval System

🔍 **Enterprise-Grade Arabic Legal Document Search with AI-Powered Quality Boosters**

A comprehensive offline Arabic document retrieval system with advanced RBAC (Role-Based Access Control) for nuclear regulatory documents. Features semantic search, keyword matching, AI-powered reranking, Arabic-native embeddings, and secure role-based document access.

## 🚀 Project Structure

```
nrrc_arabic_pov_windows/
├── backend/              # FastAPI Backend (Deploy to Render)
│   ├── app/             # Application code
│   ├── data/            # Indices and documents
│   ├── conf/            # Configuration files
│   ├── scripts/         # Processing scripts
│   ├── requirements.txt
│   └── start.sh         # Render startup script
│
├── frontend/            # Web Frontend (Deploy to Vercel)
│   ├── index.html       # Single-page application
│   ├── vercel.json      # Vercel configuration
│   └── README.md
│
├── docs/                # Documentation
│   ├── deploy.txt       # Full deployment guide
│   ├── QUICK_START.md   # Quick deployment steps
│   ├── DEPLOYMENT_STRUCTURE.md
│   └── ... (all other docs)
│
├── archive/             # Legacy files (old structure)
│   └── ... (preserved for reference)
│
└── LICENSE              # Project license
```

## ⚡ Quick Start

### Local Development

**Option 1: Monolithic (from archive)**
```bash
cd archive
pip install -r requirements.txt
uvicorn app.run_api:app --host 0.0.0.0 --port 8000 --reload
```

**Option 2: Separated (recommended)**
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.api:app --reload

# Frontend (separate terminal)
cd frontend
python -m http.server 3000
```

### Deployment

1. **Quick**: Read `docs/QUICK_START.md`
2. **Detailed**: Follow `docs/deploy.txt`
3. **Structure**: Check `docs/DEPLOYMENT_STRUCTURE.md`

## 🎯 Features

### Advanced Search
- **Keyword Search**: BM25-based exact term matching
- **Semantic Search**: Multilingual-E5 embeddings
- **Arabic-Native**: AraBERT-v3 for Arabic-specific understanding
- **AI Reranking**: BGE reranker for precision optimization
- **Hybrid Fusion**: Combines all approaches

### Security
- JWT-based authentication
- Role-Based Access Control (RBAC)
- Document-level restrictions
- Secure password hashing

### Quality Boosters
- BAAI/bge-reranker-v2-m3
- AraBERT-v3 integration
- Synonym expansion
- Enhanced retrieval pipeline

## 📋 Test Accounts

| Username | Password | Access Level |
|----------|----------|--------------|
| admin | admin123 | Full access (including restricted docs) |
| legal | legal123 | General + Restricted documents |
| staff | staff123 | General documents only |

## 🔗 API Endpoints

- `POST /login` - User authentication
- `GET /me` - Get current user info
- `GET /users` - List users (admin only)
- `POST /ask` - Search documents (requires authentication)
- `GET /health` - Health check

## 📚 Documentation

All documentation is in the `docs/` folder:

| File | Purpose |
|------|---------|
| `deploy.txt` | Complete deployment walkthrough |
| `QUICK_START.md` | Quick deployment steps |
| `DEPLOYMENT_STRUCTURE.md` | Project structure details |
| `SETUP_COMPLETE.md` | Setup completion summary |
| `backend/README.md` | Backend-specific info |
| `frontend/README.md` | Frontend-specific info |

## 🚀 Deployment

### Backend (Render)
```bash
# Push to GitHub
# Connect in Render dashboard
# Set root directory: backend
# Deploy
```

### Frontend (Vercel)
```bash
# Update API_URL in frontend/index.html
# Push to GitHub
# Connect in Vercel dashboard
# Set root directory: frontend
# Deploy
```

See `docs/deploy.txt` for detailed instructions.

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **Search**: FAISS, BM25, Sentence-Transformers
- **Models**: mE5-base, AraBERT-v3, BGE Reranker
- **Auth**: JWT, bcrypt
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Render + Vercel

## 📊 Project Status

✅ **Complete**
- Phase 1-10: All phases implemented
- Quality Boosters: Week 2 features deployed
- RBAC: Full role-based access control
- Deployment: Ready for production

## 🔧 Environment Variables

### Backend
- `SECRET_KEY`: JWT secret key
- `PYTHONIOENCODING`: utf-8

### Frontend
- `REACT_APP_API_URL`: Backend API URL

## 🤝 Support

- **Issues**: Check troubleshooting in `docs/deploy.txt`
- **Platforms**: 
  - Render: https://render.com/docs
  - Vercel: https://vercel.com/docs
- **Project**: See documentation in `docs/` folder

## 📝 License

See LICENSE file for details.

---

**Built with** ❤️ for NRRC - Nuclear and Radiation Control Authority

For deployment instructions, see `docs/QUICK_START.md` or `docs/deploy.txt`


