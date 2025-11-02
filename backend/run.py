#!/usr/bin/env python3
"""
Quick start script for the backend API
"""
import uvicorn
import os

if __name__ == "__main__":
    # Set environment variables
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("TRANSFORMERS_CACHE", ".cache/transformers")
    
    # Run the API server
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

