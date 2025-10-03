# Contact Extractor Chatbot — Google Gemini + LangChain + Pydantic

A beginner-friendly **chatbot** that extracts clean **contact JSON** (name, age, email, phone) from messy text using:
- **Google Gemini 2.5** (`google.generativeai`)
- **LangChain** (prompt orchestration + structured output)
- **Pydantic** (JSON validation)
- **phonenumbers** (E.164 phone normalization)
- **Email autocorrect** (regex → LLM fallback)
## 🏛️ Project Structure

The project is organized into logical modules for clarity and maintainability:

```
/gemini-contact-extractor
|
├── app.py                  # Main application: Gradio UI and core logic
├── models.py               # Pydantic data model for a 'Person'
├── extraction.py           # LangChain logic for extracting information
├── validation_utils.py     # Helper functions for phone/email validation & correction
|
├── requirements.txt        # List of all Python dependencies
├── .env.example            # Example environment file for the API key
├── README.md               # You are here!
└── .gitignore              # To exclude unnecessary files from Git
```
