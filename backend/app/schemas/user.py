from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LearnerProfileBase(BaseModel):
    headline: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    target_role: Optional[str] = None
    years_of_experience: float = 0.0
    education_level: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None

class LearnerProfileCreate(LearnerProfileBase):
    user_id: str

class LearnerProfileUpdate(LearnerProfileBase):
    pass

class LearnerResponse(LearnerProfileBase):
    id: str
    user_id: str
    user: Optional[UserResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
