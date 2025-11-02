#!/bin/bash
# Script to start the FastAPI application on Render

# Set environment variables
export PYTHONIOENCODING=utf-8
export TRANSFORMERS_CACHE=/app/.cache/transformers

# Start the API server
exec uvicorn app.api:app --host 0.0.0.0 --port $PORT

