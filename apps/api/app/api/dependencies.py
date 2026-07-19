from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db import get_db
from app.db.models import User
from app.schemas.auth import WorkspaceRole
from app.services.auth_service import AuthService


@dataclass(frozen=True)
class RequestContext:
    user: User
    workspace_id: str
    role: WorkspaceRole
    db: Session


def _bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
    return authorization.split(" ", 1)[1].strip()


def get_request_context(
    authorization: str | None = Header(default=None),
    x_workspace_id: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> RequestContext:
    payload = decode_access_token(_bearer_token(authorization))
    user = db.get(User, payload.get("sub"))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    workspace_id = x_workspace_id or payload.get("workspace_id")
    if not workspace_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Workspace is required.")
    membership = AuthService(db).ensure_membership(user.id, workspace_id)
    return RequestContext(
        user=user,
        workspace_id=workspace_id,
        role=WorkspaceRole(membership.role),
        db=db,
    )


def require_editor(context: RequestContext = Depends(get_request_context)) -> RequestContext:
    AuthService(context.db).ensure_membership(
        context.user.id,
        context.workspace_id,
        {WorkspaceRole.owner.value, WorkspaceRole.admin.value, WorkspaceRole.editor.value},
    )
    return context


def require_admin(context: RequestContext = Depends(get_request_context)) -> RequestContext:
    AuthService(context.db).ensure_membership(
        context.user.id,
        context.workspace_id,
        {WorkspaceRole.owner.value, WorkspaceRole.admin.value},
    )
    return context
