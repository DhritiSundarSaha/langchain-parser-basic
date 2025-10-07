import re
import phonenumbers

COMMON_DOMAIN_FIXES = {
    "gamil.com": "gmail.com", "gmial.com": "gmail.com", "gmail.con": "gmail.com",
    "yaho.com": "yahoo.com", "outlok.com": "outlook.com", "hotmail.com": "hotmail.com",
    "icloud,com": "icloud.com"
}

def normalize_phone(number_raw: str, default_region: str = "IN") -> str:
    cleaned = re.sub(r"[^\d+]", "", number_raw or "")
    if cleaned.startswith("+"):
        parsed = phonenumbers.parse(cleaned, None)
    else:
        parsed = phonenumbers.parse(cleaned, default_region)
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError("Invalid phone number")
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

def regex_autocorrect_email(raw: str) -> str:
    if not raw: return raw
    s = raw.strip().replace(" ", "").replace("(at)", "@").replace("(dot)", ".").replace(",", ".")
    if "@" in s:
        local, domain = s.split("@", 1)
        domain = COMMON_DOMAIN_FIXES.get(domain.lower(), domain)
        s = f"{local}@{domain}"
    return s