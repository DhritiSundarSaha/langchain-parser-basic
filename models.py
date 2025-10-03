from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from validation_utils import normalize_phone

class Person(BaseModel):
    name: str = Field(..., min_length=1, description="The person's name.")
    age: int = Field(..., ge=0, le=120, description="The person's age.")
    email: Optional[EmailStr] = Field(default=None, description="The person's email address.")
    phone: Optional[str] = Field(default=None, description="E.164 formatted phone number (e.g., +919876543210).")

    @field_validator("phone")
    @classmethod
    def _validate_phone(cls, v: str) -> Optional[str]:

        if v is None or v == "":
            return None
        try:
            return normalize_phone(v, default_region="IN")
        except ValueError as e:
            
            raise ValueError(f"Invalid phone number: {e}")