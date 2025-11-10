from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import Response, JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os, json, shutil
from .retrieval import load_bm25, load_faiss, load_meta, load_model, Indices, search
from .auth import (
    User, UserCreate, UserLogin, Token, authenticate_user, create_access_token,
    get_current_user, require_roles, check_file_access, filter_documents_by_access,
    get_effective_roles, ACCESS_TOKEN_EXPIRE_MINUTES
)
from .pdf_processor import process_uploaded_pdf, rebuild_all_indices
from datetime import timedelta

# ---- Paths ----
BM25_PATH = "data/idx/bm25.pkl"
FAISS_PATH = "data/idx/mE5.faiss"
META_PATH = "data/idx/meta.json"
MODEL_NAME = "intfloat/multilingual-e5-base"

indices: Indices | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global indices
    try:
        print("[Loading BM25 + FAISS + model...]")
        bm25 = load_bm25(BM25_PATH)
        faiss_index = load_faiss(FAISS_PATH)
        meta = load_meta(META_PATH)
        model = load_model(MODEL_NAME)
        indices = Indices(bm25=bm25, faiss_index=faiss_index, meta=meta, model=model)
        print("[OK] System ready")
    except Exception as e:
        print(f"[ERROR] Failed to load indices: {e}")
        print("[WARNING] System may not function correctly")
        indices = None
    
    yield
    
    # Shutdown
    print("[Shutting down...]")


app = FastAPI(title="Arabic Legal Q&A API", lifespan=lifespan)

# Add CORS middleware
# Allow origins from environment variable or use wildcard for development
allowed_origins = os.getenv("CORS_ORIGINS", "*")
if allowed_origins == "*":
    cors_origins = ["*"]
else:
    # Support comma-separated list of origins
    cors_origins = [origin.strip() for origin in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # WARNING: In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    allow_origin_regex="https://.*\\.ngrok-free\\.app"
)


class AskPayload(BaseModel):
    query: str
    topk: int = 5

class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/", response_class=HTMLResponse)
def root():
    """Root endpoint - Serve frontend HTML"""
    # Try multiple possible paths for frontend/index.html
    # __file__ is at backend/app/api.py
    # We want to find frontend/index.html at project root
    app_dir = os.path.dirname(__file__)  # backend/app/
    backend_dir = os.path.dirname(app_dir)  # backend/
    project_root = os.path.dirname(backend_dir)  # project root
    
    possible_paths = [
        os.path.join(project_root, "frontend", "index.html"),  # project_root/frontend/index.html
        os.path.join(backend_dir, "..", "frontend", "index.html"),  # Fallback
    ]
    # Also check nginx default html directory (when running in Docker)
    possible_paths.insert(0, "/usr/share/nginx/html/index.html")
    
    frontend_path = None
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            frontend_path = abs_path
            break
    
    if frontend_path:
        with open(frontend_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        # Fallback if file not found
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head><title>NRRC Arabic PoV</title></head>
        <body style="font-family: Arial; padding: 40px; text-align: center;">
            <h1>NRRC Arabic PoV API</h1>
            <p>Frontend file not found. Please ensure frontend/index.html exists.</p>
            <p><a href="/docs">API Documentation</a></p>
            <p><a href="/health">Health Check</a></p>
        </body>
        </html>
        """)

@app.get("/api/info")
def api_info():
    """API information endpoint"""
    return {
        "message": "NRRC Arabic PoV API",
        "status": "running",
        "version": "2.0",
        "endpoints": {
            "health": "/health",
            "login": "/login",
            "search": "/ask",
            "upload_pdf": "/upload-pdf (admin only)",
            "rebuild_indices": "/rebuild-indices (admin only)"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint for Docker"""
    if indices is None:
        return {"status": "loading", "message": "System is still loading"}
    return {"status": "healthy", "message": "System is ready"}


# Authentication endpoints
@app.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Login endpoint to get access token"""
    print(f"[DEBUG] Login attempt for user: {login_data.username}")
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        print(f"[DEBUG] Authentication failed for user: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print(f"[DEBUG] Authentication successful for user: {login_data.username}")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.get("/users", response_model=list[User])
async def list_users(current_user: User = Depends(require_roles(["admin"]))):
    """List all users (admin only)"""
    from .auth import USERS_DB
    users = []
    for user_data in USERS_DB.values():
        users.append(User(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            roles=user_data["roles"],
            is_active=user_data["is_active"]
        ))
    return users

@app.post("/ask", response_class=Response)
async def ask(payload: AskPayload, current_user: User = Depends(get_current_user)):
    """
    Search endpoint with RBAC - Return manual JSON string (NOT auto-escaped).
    """
    # Get effective roles for the user
    effective_roles = get_effective_roles(current_user.roles)
    
    # Perform search with user's roles
    out = search(indices, payload.query, effective_roles, topk=payload.topk)
    
    # Filter results based on file access restrictions
    filtered_results = filter_documents_by_access(current_user.roles, out["results"])
    
    # Update the answer if no results remain after filtering
    if not filtered_results and out["results"]:
        answer_html = "لم يتم العثور على نتائج متاحة بناءً على صلاحياتك الحالية."
    else:
        answer_html = out["answer"]
    
    raw_json = json.dumps({
        "answer": answer_html, 
        "citations": filtered_results,
        "user_roles": current_user.roles,
        "total_found": len(out["results"]),
        "accessible_results": len(filtered_results)
    }, ensure_ascii=False)
    
    # ✅ return as plain response so <mark> isn't escaped
    return Response(content=raw_json, media_type="application/json")


def reload_indices():
    """Reload indices after PDF processing"""
    global indices
    try:
        print("[Reloading indices...]")
        bm25 = load_bm25(BM25_PATH)
        faiss_index = load_faiss(FAISS_PATH)
        meta = load_meta(META_PATH)
        model = load_model(MODEL_NAME)
        indices = Indices(bm25=bm25, faiss_index=faiss_index, meta=meta, model=model)
        print("[OK] Indices reloaded successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to reload indices: {e}")
        return False


@app.post("/upload-pdf", response_model=dict)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(["admin"]))
):
    """
    Upload and process a PDF file (Admin only).
    Automatically chunks, indexes, and makes it searchable.
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = "data/raw_pdfs"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate file path
    doc_id = os.path.splitext(file.filename)[0]
    file_path = os.path.join(upload_dir, file.filename)
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"[Upload] Saved PDF: {file.filename}")
        
        # Process PDF: chunk, index BM25 and FAISS
        result = process_uploaded_pdf(file_path, doc_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("message", "Failed to process PDF")
            )
        
        # Reload indices in memory
        if not reload_indices():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reload indices after processing"
            )
        
        return {
            "success": True,
            "message": f"PDF '{file.filename}' processed successfully and is now searchable",
            "doc_id": doc_id,
            "chunks_created": result["chunks_created"],
            "total_chunks": result["total_chunks"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        # Clean up file if processing failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process PDF: {str(e)}"
        )


@app.post("/rebuild-indices", response_model=dict)
async def rebuild_indices_endpoint(
    current_user: User = Depends(require_roles(["admin"]))
):
    """
    Rebuild all indices from all PDFs (Admin only).
    Useful if indices get corrupted or need to be refreshed.
    """
    try:
        result = rebuild_all_indices()
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("message", "Failed to rebuild indices")
            )
        
        # Reload indices in memory
        if not reload_indices():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reload indices after rebuilding"
            )
        
        return {
            "success": True,
            "message": "Indices rebuilt successfully",
            "total_chunks": result["total_chunks"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Rebuild failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rebuild indices: {str(e)}"
        )

from fastapi.middleware.cors import CORSMiddleware

