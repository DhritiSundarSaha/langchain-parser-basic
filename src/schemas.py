from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Person(BaseModel):
    name: str = Field(..., min_length=1)
    age: int = Field(..., ge=0, le=120)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None