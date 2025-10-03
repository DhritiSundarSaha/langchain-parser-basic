# Contact Extractor Chatbot — Google Gemini + LangChain + Pydantic

A beginner-friendly **chatbot** that extracts clean **contact JSON** (name, age, email, phone) from messy text using:
- **Google Gemini 2.5** (`google.generativeai`)
- **LangChain** (prompt orchestration + structured output)
- **Pydantic** (JSON validation)
- **phonenumbers** (E.164 phone normalization)
- **Email autocorrect** (regex → LLM fallback)