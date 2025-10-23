# NRRC Arabic PoV - Advanced Arabic Document Retrieval System

🔍 **Enterprise-Grade Arabic Legal Document Search with AI-Powered Quality Boosters**

A comprehensive offline Arabic document retrieval system with advanced RBAC (Role-Based Access Control) for nuclear regulatory documents. Features semantic search, keyword matching, AI-powered reranking, Arabic-native embeddings, and secure role-based document access.

## 🚀 **NEW: Week-2 Quality Boosters**

### ✅ **BAAI/bge-reranker-v2-m3**
- **Multilingual Reranking**: Cross-encoder for top-50 candidate reranking
- **Precision Lift**: 10-20% improvement in search accuracy
- **Score Fusion**: Combines rerank scores with original relevance

### ✅ **AraBERT-v3 Integration**
- **Arabic-Native Embeddings**: Second embedding index for better Arabic understanding
- **Weighted Fusion**: 0.7 mE5 / 0.3 AraBERT optimal combination
- **RRF Support**: Reciprocal Rank Fusion for advanced result merging

### ✅ **Synonym Expansion**
- **Query Enhancement**: Up to 2 synonyms from Arabic legal glossary
- **Semantic Drift Prevention**: Avoids missing relevant documents
- **Arabic Legal Terms**: Specialized nuclear/legal terminology

### ✅ **Enhanced Retrieval Pipeline**
- **End-to-End Integration**: All quality boosters working together
- **Configurable Weights**: Adjustable fusion parameters
- **Production Ready**: Comprehensive logging and monitoring





# 🚀 Quick Start for Smart NRRC AI

### Prerequisites
- Python 3.11+
- No Internet required after first setup
- Windows 10/11 (PowerShell 7+)

### Steps
1. Clone or unzip project
2. Open PowerShell → Run:
   ```powershell
   .\run_native.bat


### Prerequisites
- Python 3.10/3.11
- Windows PowerShell 7+ (recommended)
- Internet connection (first run only)





### 1. Setup Environment
```powershell
# Create project directory
cd %HOMEPATH%\Desktop
mkdir nrrc_arabic_pov && cd nrrc_arabic_pov

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 2. Add Your Documents
Place your Arabic PDFs in: `data\raw_pdfs\`

### 3. Run the Complete Pipeline
```powershell
# Extract and chunk documents
python scripts\02_extract_and_chunk.py

# Build keyword index (BM25)
python scripts\03_build_bm25.py

# Build semantic index (FAISS)
python scripts\04_build_faiss.py

# Add test restricted documents (optional)
python scripts\add_restricted_docs.py
```

### 4. Test the System
```powershell
# CLI Testing
python scripts\05_query_cli.py --query "ما هو حد مسؤولية المشغل؟" --roles staff
python scripts\05_query_cli.py --query "الطاقة النووية" --roles legal --show-restricted

# Start Web API
uvicorn app.run_api:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Access Web Interface
Open `http://localhost:8000` and login with:
- **Admin**: `admin` / `admin123` (Full access)
- **Legal**: `legal` / `legal123` (Legal + Restricted access)  
- **Staff**: `staff` / `staff123` (General access only)

## 📋 Complete Phase-by-Phase Implementation

### Phase 1: Data Preparation
```powershell
# Extract and chunk PDF documents
python scripts\02_extract_and_chunk.py
```
**Evidence**: `evidence_phase1.txt`

### Phase 2: Keyword Indexing (BM25)
```powershell
# Build BM25 keyword search index
python scripts\03_build_bm25.py
```
**Evidence**: `evidence_phase2.txt`

### Phase 3: Semantic Indexing (FAISS)
```powershell
# Build FAISS semantic search index
python scripts\04_build_faiss.py
```
**Evidence**: `evidence_phase3.txt`

### Phase 4: Hybrid Search Implementation
```powershell
# Test hybrid search functionality
python scripts\05_query_cli.py --query "test query" --roles admin
```
**Evidence**: `evidence_phase4.txt`

### Phase 5: RBAC System Implementation
```powershell
# Test RBAC with different roles
python scripts\test_rbac.py
```
**Evidence**: `evidence_phase5.txt`

### Phase 6: Web Interface Development
```powershell
# Start web interface
uvicorn app.run_api:app --host 0.0.0.0 --port 8000 --reload
```
**Evidence**: `evidence_phase6.txt`

### Phase 7: Testing and Validation
```powershell
# Run comprehensive tests
python scripts\test_rbac.py
python scripts\05_query_cli.py --query "test" --roles admin
```
**Evidence**: `evidence_phase7.txt`

### Phase 8: Evaluation Framework
```powershell
# Run evaluation on gold standard dataset
$env:PYTHONIOENCODING="utf-8"; python eval\evaluate.py
```
**Evidence**: `evidence_phase8.txt`

### Phase 9: Handover Pack
```powershell
# Package system for distribution
# (See Docker section below)
```
**Evidence**: This README and evidence files

### Phase 10: Quality Boosters Implementation ✅
```powershell
# Implement Week-2 quality boosters
python scripts\quality_boosters_implementation.py

# Test BGE reranker
python test_bge_reranker.py

# Test AraBERT integration
python create_arabert_index.py

# Test synonym expansion
python test_synonym_expansion.py

# Test enhanced retrieval system
python test_enhanced_retrieval.py
```
**Evidence**: `evidence_quality_boosters.txt`

## 🔐 RBAC System Features

### Role Hierarchy
- **Admin**: Full access to all documents including restricted ones
- **Legal**: Access to general documents and restricted documents
- **Staff**: Access to general documents only

### File Restrictions
- **Automatic Detection**: Any document with "restricted" in its name is automatically restricted
- **Access Control**: Only `legal` and `admin` roles can access restricted documents
- **Transparent Filtering**: Users are informed about their access level and hidden results

### Security Features
- JWT-based authentication with secure token management
- Password hashing using bcrypt
- Session management with automatic logout
- Role-based API endpoint protection

## 📁 Project Structure

```
nrrc_arabic_pov/
├── app/
│   ├── auth.py                    # Authentication & RBAC system
│   ├── run_api.py                 # Main API with web interface
│   ├── retrieval.py               # Search engine with RBAC
│   ├── chunking.py                # Document processing
│   ├── normalize.py               # Arabic text normalization
│   ├── bge_reranker.py           # BAAI/bge-reranker-v2-m3 integration
│   ├── arabert_integration.py    # AraBERT-v3 second embedding index
│   ├── synonym_expander.py        # Query-time synonym expansion
│   └── enhanced_retrieval.py     # Integrated quality boosters
├── scripts/
│   ├── 02_extract_and_chunk.py    # PDF processing
│   ├── 03_build_bm25.py           # Keyword index
│   ├── 04_build_faiss.py          # Semantic index
│   ├── 05_query_cli.py            # CLI interface
│   ├── add_restricted_docs.py     # Add test documents
│   ├── test_rbac.py               # RBAC testing
│   └── quality_boosters_implementation.py  # Quality boosters setup
├── data/
│   ├── raw_pdfs/            # Input PDF files
│   ├── processed/           # Chunked documents
│   ├── idx/                 # Search indices (BM25, mE5, AraBERT)
│   └── finetuning_dataset.csv  # Fine-tuning dataset
├── conf/
│   └── glossary_ar.json     # Arabic synonyms (20+ groups)
├── eval/
│   ├── gold.csv             # Gold standard evaluation dataset
│   └── evaluate.py          # Evaluation framework
├── test_*.py                # Quality booster test scripts
├── create_arabert_index.py  # AraBERT index creation
└── requirements.txt         # Dependencies
```

## 🔧 API Endpoints

### Authentication
- `POST /login` - User authentication
- `GET /me` - Get current user info
- `GET /users` - List users (admin only)

### Search
- `POST /ask` - Search documents (requires authentication)

### Example API Usage
```bash
# Login
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "staff", "password": "staff123"}'

# Search (with token)
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "الطاقة النووية", "topk": 5}'
```

## 🧪 Testing

### CLI Testing
```powershell
# Test different roles
python scripts\05_query_cli.py --query "restricted" --roles staff --show-restricted
python scripts\05_query_cli.py --query "restricted" --roles legal --show-restricted
python scripts\05_query_cli.py --query "restricted" --roles admin --show-restricted
```

### Automated Testing
```powershell
# Run comprehensive RBAC tests
python scripts\test_rbac.py
```

## 📊 Search Features

### Advanced Multi-Engine Search
- **Keyword Search**: BM25-based exact term matching
- **Semantic Search**: Multilingual-E5 embeddings for meaning-based search
- **Arabic-Native Search**: AraBERT-v3 for Arabic-specific understanding
- **AI Reranking**: BGE reranker for precision optimization
- **Hybrid Fusion**: Combines all approaches for optimal results

### Arabic Language Support
- **Text Normalization**: Handles Arabic diacritics and variations
- **Synonym Expansion**: Uses glossary for term expansion
- **RTL Support**: Full right-to-left text support in UI

### Result Highlighting
- **Yellow Highlights**: Direct term matches
- **Green Highlights**: Semantic/synonym matches
- **Citation Information**: Document, article, page references

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**
   ```powershell
   # Ensure virtual environment is activated
   .\.venv\Scripts\Activate.ps1
   ```

2. **Encoding Issues**
   ```powershell
   # Set UTF-8 encoding
   $env:PYTHONIOENCODING="utf-8"
   ```

3. **Model Download Issues**
   ```powershell
   # Set model cache directory
   $env:TRANSFORMERS_CACHE="C:\path\to\cache"
   ```

4. **Empty Search Results**
   - Check if PDFs are scanned images (need OCR)
   - Verify documents are in `data/raw_pdfs/`
   - Re-run the pipeline steps

### Performance Tuning
- Increase candidate pools: `bm25_k=100, vec_k=100`
- Adjust fusion weight: `alpha=0.7` for more semantic weight
- Add more synonyms to `conf/glossary_ar.json`

## 📚 Documentation

- **Complete Documentation**: See `documentation.txt`
- **RBAC Guide**: See `RBAC_README.md`
- **Implementation Summary**: See `IMPLEMENTATION_SUMMARY.md`

## 🔒 Security Notes

- Change default passwords in production
- Use strong SECRET_KEY for JWT signing
- Implement HTTPS in production
- Regular security audits recommended

## 📈 Performance

### Enhanced Performance with Quality Boosters
- **Indexing**: ~2-3 minutes for 5-6 PDFs (includes AraBERT index)
- **Search**: <200ms response time (with reranking)
- **Memory**: ~1.5GB for full system (mE5 + AraBERT + BGE reranker)
- **Storage**: ~150MB indices for 5-6 PDFs (includes all indices)
- **Precision Improvement**: 10-20% better accuracy with quality boosters

## 🐳 Docker Deployment

### Quick Start with Docker
```bash
# Clone repository
git clone <repository-url>
cd nrrc_arabic_pov_windows

# Add your PDFs to data/raw_pdfs/
# Then build and run
docker-compose up -d

# Access at http://localhost:8000
```

### Docker Commands
```bash
# Build image
docker build -t nrrc-arabic-pov .

# Run container
docker run -d -p 8000:8000 -v $(pwd)/data:/app/data nrrc-arabic-pov

# Check health
curl http://localhost:8000/health
```

For detailed Docker deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## 📦 Package Contents

### Core Files
- `app/` - Main application code
- `scripts/` - Processing and utility scripts
- `data/` - Document indices and processed data
- `conf/` - Configuration files
- `eval/` - Evaluation framework

### Evidence Files
- `evidence_phase1.txt` - Data preparation evidence
- `evidence_phase2.txt` - BM25 indexing evidence
- `evidence_phase3.txt` - FAISS indexing evidence
- `evidence_phase4.txt` - Hybrid search evidence
- `evidence_phase5.txt` - RBAC system evidence
- `evidence_phase6.txt` - Web interface evidence
- `evidence_phase7.txt` - Testing evidence
- `evidence_phase8.txt` - Evaluation evidence

### Docker Files
- `Dockerfile` - Container definition
- `docker-compose.yml` - Multi-container setup
- `.dockerignore` - Docker ignore patterns
- `DEPLOYMENT.md` - Deployment guide

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the documentation files
3. Test with different user roles
4. Verify file permissions and access
5. Check Docker logs: `docker logs nrrc-arabic-pov`

---

**Built with**: FastAPI, FAISS, BM25, Sentence-Transformers, PyMuPDF
**Language**: Arabic (RTL) with English support
**Security**: JWT Authentication + Role-Based Access Control
**Deployment**: Docker + Docker Compose ready