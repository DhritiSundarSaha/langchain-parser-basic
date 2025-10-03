import re
import phonenumbers
import google.generativeai as genai
from typing import Dict, Any, Tuple, Optional
from pydantic import ValidationError
from models import Person
def normalize_phone(number_raw: str, default_region: str = "IN") -> str:
    """
    Cleans and normalizes a phone number string to the E.164 format.
    Raises ValueError if the number is invalid.
    """
    if not number_raw or not isinstance(number_raw, str):
        raise ValueError("Phone must be a non-empty string")
    cleaned = re.sub(r"[^\d+]", "", number_raw)
    try:
        if cleaned.startswith("+"):
            parsed = phonenumbers.parse(cleaned, None)
        else:
            parsed = phonenumbers.parse(cleaned, default_region)
    except phonenumbers.NumberParseException as e:
        raise ValueError(f"Invalid phone format: {e}")

    if not phonenumbers.is_valid_number(parsed):
        raise ValueError("Phone number is not valid")

    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
COMMON_DOMAIN_FIXES = {
    "gamil.com": "gmail.com", "gmial.com": "gmail.com",
    "gmail.con": "gmail.com", "gnail.com": "gmail.com",
    "yaho.com": "yahoo.com", "yhoo.com": "yahoo.com",
    "outlok.com": "outlook.com", "hotmal.com": "hotmail.com",
    "icloud,com": "icloud.com",
}

def regex_autocorrect_email(raw: str) -> str:
    """Applies a series of common-sense regex and string replacements to fix emails."""
    if not raw: return raw
    s = raw.strip().replace(" ", "")
    s = s.replace("(at)", "@").replace("[at]", "@") if "@" not in s else s
    s = s.replace("(dot)", ".").replace("[dot]", ".")
    s = s.replace(",", ".")
    if "@" in s:
        local, domain = s.split("@", 1)
        domain = COMMON_DOMAIN_FIXES.get(domain.lower(), domain)
        s = f"{local}@{domain}"
    return re.sub(r"[;,\.\s]+$", "", s)

def llm_suggest_email(raw: str, model_id: str) -> str:
    """Asks the Gemini model to suggest a corrected email address."""
    model = genai.GenerativeModel(model_id)
    prompt = f"""
You are an email-correction function.
Given a possibly mistyped email, return ONLY the corrected email.
If you cannot confidently correct it, return EXACTLY: UNKNOWN

Input: "raj_22 at gmail,com"
Output: raj_22@gmail.com

Input: "foo at bar"
Output: UNKNOWN

Input: "{raw}"
Output:
"""
    try:
        resp = model.generate_content(prompt)
        suggestion = (getattr(resp, "text", "") or "").strip()
        return suggestion if "UNKNOWN" not in suggestion.upper() else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def validate_with_autocorrect(payload: Dict[str, Any], model_id: str) -> Tuple[Optional[Person], Dict[str, Any]]:
    """
    Tries to validate a payload into a Person model. If email validation fails,
    it attempts a two-pass auto-correction (regex, then LLM).
    Returns the validated Person object and a dictionary with info about the process.
    """
    info = {"email_correction": None, "llm_email_correction": None, "errors": None}
    try:
        return Person.model_validate(payload), info
    except ValidationError as e:
        info["errors"] = str(e)

    data = dict(payload)
    raw_email = data.get("email")

    if raw_email:
        # 1. Regex Pass
        corrected_email = regex_autocorrect_email(raw_email)
        if corrected_email != raw_email:
            data["email"] = corrected_email
            info["email_correction"] = {"from": raw_email, "to": corrected_email}
            try:
                person = Person.model_validate(data)
                info["errors"] = None
                return person, info
            except ValidationError as e:
                info["errors"] = str(e) # Update error with new attempt

        # 2. LLM Pass
        llm_suggestion = llm_suggest_email(raw_email, model_id)
        if llm_suggestion not in ["UNKNOWN", raw_email]:
            data["email"] = llm_suggestion
            info["llm_email_correction"] = {"from": raw_email, "to": llm_suggestion}
            try:
                person = Person.model_validate(data)
                info["errors"] = None
                return person, info
            except ValidationError as e:
                info["errors"] = str(e) # Update error with final attempt

    return None, info