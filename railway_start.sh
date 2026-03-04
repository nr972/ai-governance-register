#!/usr/bin/env bash
set -e

# Railway startup — runs both API and Streamlit in a single container

mkdir -p data

# Start API in background
uvicorn api.main:app --host 0.0.0.0 --port 8000 &

# Wait for API
sleep 2

# Start Streamlit (foreground)
streamlit run agr_frontend/app.py \
    --server.port 8501 \
    --server.headless true \
    --server.address 0.0.0.0
