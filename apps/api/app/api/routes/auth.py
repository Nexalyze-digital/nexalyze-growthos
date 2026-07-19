from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from app.api.dependencies import RequestContext, get_request_context
from app.db import get_db
from app.schemas.auth import (
    AuthTokens,
    CurrentUserResponse,
    RefreshRequest,
    UserLogin,
    UserRegister,
    WorkspaceCreate,
    WorkspaceList,
    WorkspaceSummary,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthTokens, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> AuthTokens:
    return AuthService(db).register(payload)


@router.post("/login", response_model=AuthTokens)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> AuthTokens:
    return AuthService(db).login(payload)


@router.post("/refresh", response_model=AuthTokens)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> AuthTokens:
    return AuthService(db).refresh(payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: RefreshRequest | None = None,
    context: RequestContext = Depends(get_request_context),
) -> None:
    AuthService(context.db).logout(payload.refresh_token if payload else None, context.user.id)


@router.get("/me", response_model=CurrentUserResponse)
def current_user(context: RequestContext = Depends(get_request_context)) -> CurrentUserResponse:
    return AuthService(context.db).current_user(context.user, context.workspace_id)


@router.get("/workspaces", response_model=WorkspaceList)
def list_workspaces(context: RequestContext = Depends(get_request_context)) -> WorkspaceList:
    return AuthService(context.db).list_workspaces(context.user.id)


@router.post("/workspaces", response_model=WorkspaceSummary, status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: WorkspaceCreate,
    context: RequestContext = Depends(get_request_context),
) -> WorkspaceSummary:
    return AuthService(context.db).create_workspace(context.user.id, payload)
