"""
PDF Processing Service for Admin Uploads
Handles PDF upload, chunking, and index rebuilding
"""
import os
import json
import pickle
import numpy as np
import faiss
from typing import List
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from .chunking import build_chunks_from_pdf, run_for_folder
from .normalize import tokenize_ar

CHUNKS_PATH = "data/processed/chunks.jsonl"
BM25_PATH = "data/idx/bm25.pkl"
FAISS_PATH = "data/idx/mE5.faiss"
META_PATH = "data/idx/meta.json"
RAW_PDFS_DIR = "data/raw_pdfs"
MODEL_NAME = "intfloat/multilingual-e5-base"


def process_uploaded_pdf(pdf_path: str, doc_id: str, roles: List[str] = None) -> dict:
    """
    Process a single uploaded PDF and rebuild indices.
    
    Args:
        pdf_path: Path to the uploaded PDF file
        doc_id: Document ID (filename without extension)
        roles: List of roles that can access this document
        
    Returns:
        dict with processing results
    """
    if roles is None:
        roles = ["staff", "legal", "admin"]
    
    # Check if PDF is restricted
    if "restricted" in doc_id.lower():
        roles = ["legal", "admin"]
    
    print(f"[PDF Processor] Processing {doc_id}...")
    
    # 1. Build chunks from PDF
    new_chunks = build_chunks_from_pdf(pdf_path, doc_id, roles)
    print(f"[PDF Processor] Created {len(new_chunks)} chunks from {doc_id}")
    
    # 2. Load existing chunks
    existing_chunks = []
    if os.path.exists(CHUNKS_PATH):
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            existing_chunks = [json.loads(line) for line in f if line.strip()]
    
    # 3. Remove old chunks from same document and add new ones
    existing_chunks = [ch for ch in existing_chunks if ch.get("doc_id") != doc_id]
    all_chunks = existing_chunks + new_chunks
    
    # 4. Save updated chunks
    os.makedirs(os.path.dirname(CHUNKS_PATH), exist_ok=True)
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        for ch in all_chunks:
            f.write(json.dumps(ch, ensure_ascii=False) + "\n")
    
    print(f"[PDF Processor] Total chunks: {len(all_chunks)}")
    
    # 5. Rebuild BM25 index
    print("[PDF Processor] Rebuilding BM25 index...")
    docs_tokens = [tokenize_ar(ch["text"]) for ch in all_chunks]
    bm25 = BM25Okapi(docs_tokens)
    os.makedirs(os.path.dirname(BM25_PATH), exist_ok=True)
    with open(BM25_PATH, "wb") as f:
        pickle.dump(bm25, f)
    
    # 6. Rebuild FAISS index
    print("[PDF Processor] Rebuilding FAISS index...")
    model = SentenceTransformer(MODEL_NAME)
    texts = [c["norm_text"] for c in all_chunks]
    embs = model.encode(texts, normalize_embeddings=True, batch_size=64, show_progress_bar=False)
    embs = np.asarray(embs, dtype="float32")
    index = faiss.IndexFlatIP(embs.shape[1])
    index.add(embs)
    
    os.makedirs(os.path.dirname(FAISS_PATH), exist_ok=True)
    faiss.write_index(index, FAISS_PATH)
    
    # 7. Save metadata
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    
    print(f"[PDF Processor] ✓ Successfully processed {doc_id}")
    
    return {
        "success": True,
        "doc_id": doc_id,
        "chunks_created": len(new_chunks),
        "total_chunks": len(all_chunks),
        "message": f"Successfully processed {doc_id} with {len(new_chunks)} chunks"
    }


def rebuild_all_indices() -> dict:
    """
    Rebuild all indices from all PDFs in raw_pdfs folder.
    """
    print("[PDF Processor] Rebuilding all indices...")
    
    if not os.path.exists(RAW_PDFS_DIR):
        os.makedirs(RAW_PDFS_DIR, exist_ok=True)
        return {"success": False, "message": "No PDFs directory found"}
    
    # Process all PDFs
    run_for_folder(RAW_PDFS_DIR, CHUNKS_PATH)
    
    # Load chunks
    if not os.path.exists(CHUNKS_PATH):
        return {"success": False, "message": "No chunks found"}
    
    chunks = []
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = [json.loads(line) for line in f if line.strip()]
    
    # Rebuild BM25
    print("[PDF Processor] Rebuilding BM25...")
    docs_tokens = [tokenize_ar(ch["text"]) for ch in chunks]
    bm25 = BM25Okapi(docs_tokens)
    os.makedirs(os.path.dirname(BM25_PATH), exist_ok=True)
    with open(BM25_PATH, "wb") as f:
        pickle.dump(bm25, f)
    
    # Rebuild FAISS
    print("[PDF Processor] Rebuilding FAISS...")
    model = SentenceTransformer(MODEL_NAME)
    texts = [c["norm_text"] for c in chunks]
    embs = model.encode(texts, normalize_embeddings=True, batch_size=64, show_progress_bar=True)
    embs = np.asarray(embs, dtype="float32")
    index = faiss.IndexFlatIP(embs.shape[1])
    index.add(embs)
    
    os.makedirs(os.path.dirname(FAISS_PATH), exist_ok=True)
    faiss.write_index(index, FAISS_PATH)
    
    # Save metadata
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    
    return {
        "success": True,
        "total_chunks": len(chunks),
        "message": f"Successfully rebuilt indices with {len(chunks)} chunks"
    }

