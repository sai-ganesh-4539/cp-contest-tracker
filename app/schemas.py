from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ContestResponse(BaseModel):
    id: UUID
    platform: str
    name: str
    start_time: datetime
    duration_minutes: Optional[int]
    url: Optional[str]

    class Config:
        from_attributes = True

class BookmarkResponse(BaseModel):
    id: UUID
    contest: ContestResponse
    created_at: datetime

    class Config:
        from_attributes = True