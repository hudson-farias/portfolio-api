from pydantic import BaseModel
from typing import List


class ContactMethod(BaseModel):
    type: str
    value: str


class ContactResponse(BaseModel):
    email: str
    others: List[ContactMethod] = []
