from pydantic import BaseModel, EmailStr 
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr # ใช้ EmailStr
    password: Optional[str] = None
    display_name: str
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None
    avatar_url: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    display_name: str
    oauth_provider: Optional[str] = None # เพิ่ม field นี้ให้ตรงกับ Model
    oauth_id: Optional[str] = None       # เพิ่ม field นี้ให้ตรงกับ Model
    avatar_url: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class OAuthUserCreate(BaseModel):
    email: EmailStr
    display_name: str
    avatar_url: Optional[str] = None
    oauth_provider: str
    oauth_id: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str