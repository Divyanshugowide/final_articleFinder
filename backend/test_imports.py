"""
Test script to check if all imports work correctly
"""
import sys

print("Testing imports...")
errors = []

try:
    print("1. Testing FastAPI...")
    from fastapi import FastAPI
    print("   ✓ FastAPI OK")
except Exception as e:
    print(f"   ✗ FastAPI ERROR: {e}")
    errors.append(f"FastAPI: {e}")

try:
    print("2. Testing app modules...")
    from app.api import app
    print("   ✓ API module OK")
except Exception as e:
    print(f"   ✗ API module ERROR: {e}")
    errors.append(f"API: {e}")

try:
    print("3. Testing PDF processor...")
    from app.pdf_processor import process_uploaded_pdf
    print("   ✓ PDF processor OK")
except Exception as e:
    print(f"   ✗ PDF processor ERROR: {e}")
    errors.append(f"PDF processor: {e}")

try:
    print("4. Testing retrieval...")
    from app.retrieval import load_bm25, load_faiss, load_meta
    print("   ✓ Retrieval module OK")
except Exception as e:
    print(f"   ✗ Retrieval module ERROR: {e}")
    errors.append(f"Retrieval: {e}")

try:
    print("5. Testing chunking...")
    from app.chunking import build_chunks_from_pdf
    print("   ✓ Chunking module OK")
except Exception as e:
    print(f"   ✗ Chunking module ERROR: {e}")
    errors.append(f"Chunking: {e}")

try:
    print("6. Testing auth...")
    from app.auth import authenticate_user
    print("   ✓ Auth module OK")
except Exception as e:
    print(f"   ✗ Auth module ERROR: {e}")
    errors.append(f"Auth: {e}")

print("\n" + "="*50)
if errors:
    print("❌ ERRORS FOUND:")
    for error in errors:
        print(f"   - {error}")
    sys.exit(1)
else:
    print("✅ All imports successful!")
    print("✅ Backend is ready to run!")
    sys.exit(0)

