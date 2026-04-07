#!/bin/bash

# Ensure PORT is set, default to 8000 if not
PORT=${PORT:-8000}

echo "Starting DataLens on port $PORT..."

# Run Streamlit with explicit port binding
streamlit run streamlit_app.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --logger.level=error \
  --client.showErrorDetails=false
