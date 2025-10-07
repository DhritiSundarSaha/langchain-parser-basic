import os, re, json
import google.generativeai as genai
from schemas import Person
from validators import normalize_phone, regex_autocorrect_email
from extractor import extract_person
from pydantic import ValidationError

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_ID = os.getenv("MODEL_ID", "gemini-2.5-flash")

def llm_suggest_email(raw: str) -> str:
    model = genai.GenerativeModel(MODEL_ID)
    prompt = f"Correct this email: {raw}"
    resp = model.generate_content(prompt)
    text = getattr(resp, "text", "") or ""
    match = re.search(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", text)
    return match.group(0) if match else "UNKNOWN"

def validate_with_autocorrect(p: Person, default_region="IN") -> Person:
    data = p.model_dump()
    if data.get("phone"):
        data["phone"] = normalize_phone(data["phone"], default_region)
    if data.get("email"):
        corrected = regex_autocorrect_email(data["email"])
        try:
            data["email"] = corrected
            Person.model_validate(data)
        except ValidationError:
            suggestion = llm_suggest_email(data["email"])
            if suggestion and suggestion != "UNKNOWN":
                data["email"] = suggestion
    return Person.model_validate(data)

def respond(msg: str) -> str:
    try:
        p = extract_person(msg)
        validated = validate_with_autocorrect(p)
        return json.dumps(validated.model_dump(), indent=2)
    except Exception:
        fallback = genai.GenerativeModel(MODEL_ID).generate_content(msg)
        return getattr(fallback, "text", "Sorry, something went wrong.")