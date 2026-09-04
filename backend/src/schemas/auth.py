from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserOut(BaseModel):
    id: UUID
    phone_number: str
    full_name: str
    email: Optional[str] = None
    national_id: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


class RegisterRequest(BaseModel):
    phone_number: str = Field(..., examples=["+989121234567"])
    full_name: str
    password: str = Field(..., min_length=8)


class RegisterResponse(BaseModel):
    user_id: UUID
    message: str


class VerifyOtpRequest(BaseModel):
    phone_number: str
    otp: str = Field(..., min_length=6, max_length=6)


class LoginRequest(BaseModel):
    phone_number: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserOut


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
