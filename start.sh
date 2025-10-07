#!/bin/bash
export $(grep -v '^#' .env | xargs) 2>/dev/null
uvicorn src.app_fastapi:app --host 0.0.0.0 --port ${FASTAPI_PORT:-8000} &
streamlit run src/app_streamlit.py --server.port ${STREAMLIT_PORT:-8501} --server.address 0.0.0.0