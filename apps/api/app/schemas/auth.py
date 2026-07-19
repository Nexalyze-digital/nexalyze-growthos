from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class WorkspaceRole(str, Enum):
    owner = "owner"
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


class UserRegister(BaseModel):
    email: str = Field(..., min_length=5, max_length=320)
    password: str = Field(..., min_length=10, max_length=128)
    name: str = Field(..., min_length=2, max_length=160)
    organization_name: str = Field(default="My Organization", min_length=2, max_length=160)
    workspace_name: str = Field(default="Default Workspace", min_length=2, max_length=160)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if value.lower() == value or value.upper() == value:
            raise ValueError("Password must include uppercase and lowercase letters.")
        if not any(character.isdigit() for character in value):
            raise ValueError("Password must include at least one number.")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or "." not in normalized.rsplit("@", 1)[-1]:
            raise ValueError("Enter a valid email address.")
        return normalized


class UserLogin(BaseModel):
    email: str = Field(..., min_length=5, max_length=320)
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or "." not in normalized.rsplit("@", 1)[-1]:
            raise ValueError("Enter a valid email address.")
        return normalized


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20)


class UserSummary(BaseModel):
    id: str
    email: str
    name: str
    is_active: bool


class WorkspaceSummary(BaseModel):
    id: str
    organization_id: str
    organization_name: str
    name: str
    role: WorkspaceRole


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserSummary
    workspaces: list[WorkspaceSummary]
    active_workspace_id: str


class CurrentUserResponse(BaseModel):
    user: UserSummary
    workspaces: list[WorkspaceSummary]
    active_workspace_id: str


class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=160)
    organization_id: str | None = None


class WorkspaceList(BaseModel):
    workspaces: list[WorkspaceSummary]
