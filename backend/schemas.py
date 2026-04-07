"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


# Auth schemas
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    is_admin: bool

    class Config:
        from_attributes = True


# Run upload schemas
class RunUpload(BaseModel):
    run_data: Dict[str, Any]


class RunUploadResponse(BaseModel):
    id: int
    status: str
    duplicate: bool
    character: str
    ascension: int


# Analytics schemas
class AnalyticsComputeRequest(BaseModel):
    user_id: Optional[int] = None  # None for global stats


class AnalyticsComputeResponse(BaseModel):
    status: str
    combinations: int
    estimated_time: str


class AnalyticsResponse(BaseModel):
    metadata: Dict[str, Any]
    cards: Dict[str, Any]
