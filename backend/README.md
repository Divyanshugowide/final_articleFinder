# NRRC Arabic PoV - Backend

This is the FastAPI backend server for the NRRC Arabic Document Retrieval System.

## Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── api.py              # Main API with CORS (for frontend communication)
│   ├── run_api.py          # Original API with embedded frontend
│   ├── auth.py             # Authentication & RBAC
│   ├── retrieval.py        # Search engine
│   ├── chunking.py         # Document processing
│   ├── normalize.py        # Arabic normalization
│   ├── bge_reranker.py     # Reranking
│   ├── arabert_integration.py # AraBERT embeddings
│   ├── synonym_expander.py # Synonym expansion
│   └── enhanced_retrieval.py # Quality boosters
├── data/
│   ├── idx/                # Search indices (BM25, FAISS, etc.)
│   ├── processed/          # Processed chunks
│   └── raw_pdfs/           # Original PDF documents
├── conf/
│   └── glossary_ar.json    # Arabic synonym glossary
├── scripts/
│   └── ...                 # Processing and test scripts
├── requirements.txt        # Python dependencies
├── start.sh               # Startup script for Render
└── Dockerfile             # Docker configuration
```

## API Endpoints

- `POST /login` - User authentication
- `GET /me` - Get current user info
- `GET /users` - List users (admin only)
- `POST /ask` - Search documents (requires auth)
- `GET /health` - Health check

## Deployment on Render

1. Push code to GitHub
2. Connect repository in Render dashboard
3. Set Root Directory to `backend`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `bash start.sh`
6. Add environment variables:
   - `SECRET_KEY`: Your JWT secret
   - `PYTHONIOENCODING`: utf-8

See `../deploy.txt` for detailed deployment instructions.

## Local Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
```

Access at: http://localhost:8000

