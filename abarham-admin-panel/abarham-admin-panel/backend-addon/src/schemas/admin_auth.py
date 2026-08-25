from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AdminOut(BaseModel):
    id: UUID
    username: str
    full_name: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    admin: AdminOut


class AdminRefreshRequest(BaseModel):
    refresh_token: str


class AdminAccessTokenResponse(BaseModel):
    access_token: str


class AdminChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
