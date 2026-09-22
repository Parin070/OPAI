import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    body_type: Optional[str] = None

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    body_type: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ClothingItemResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    image_url: str
    category: Optional[str] = None
    color: Optional[str] = None
    pattern: Optional[str] = None
    formality_score: Optional[float] = None
    season: Optional[str] = None
    
    class Config:
        from_attributes = True
