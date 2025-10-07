# Contact Extractor — Gemini + LangChain + Pydantic

Extract contact info (name, age, email, phone) from messages using:
- Google Gemini 2.5 (`google.generativeai`)
- LangChain + Pydantic structured output
- FastAPI & Streamlit UI
- Docker container

## Run Locally

```bash
cp .env.example .env
streamlit run src/app_streamlit.py
# or:
uvicorn src.app_fastapi:app --reload --port 8000
```

## Docker

```bash
docker build -t contact-bot .
docker run --env-file .env -p 8000:8000 -p 8501:8501 contact-bot
```