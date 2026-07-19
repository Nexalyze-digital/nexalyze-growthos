from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
    utc_now,
    verify_password,
)
from app.db.models import (
    AuditEvent,
    Organization,
    RefreshToken,
    User,
    Workspace,
    WorkspaceMembership,
)
from app.schemas.auth import (
    AuthTokens,
    CurrentUserResponse,
    UserLogin,
    UserRegister,
    UserSummary,
    WorkspaceCreate,
    WorkspaceList,
    WorkspaceRole,
    WorkspaceSummary,
)


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def register(self, payload: UserRegister) -> AuthTokens:
        existing = self.db.scalar(select(User).where(User.email == payload.email.lower()))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists.")

        user = User(
            email=payload.email.lower(),
            name=payload.name.strip(),
            password_hash=hash_password(payload.password),
            is_active=True,
        )
        self.db.add(user)
        self.db.flush()
        organization = Organization(name=payload.organization_name.strip(), owner_user_id=user.id)
        self.db.add(organization)
        self.db.flush()
        workspace = Workspace(organization_id=organization.id, name=payload.workspace_name.strip())
        self.db.add(workspace)
        self.db.flush()
        self.db.add(WorkspaceMembership(workspace_id=workspace.id, user_id=user.id, role=WorkspaceRole.owner.value))
        self._audit(user.id, workspace.id, "auth.register", "user", user.id)
        self.db.commit()
        return self._tokens_for(user, workspace.id)

    def login(self, payload: UserLogin) -> AuthTokens:
        user = self.db.scalar(select(User).where(User.email == payload.email.lower()))
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive.")
        workspace_id = self._default_workspace_id(user.id)
        self._audit(user.id, workspace_id, "auth.login", "user", user.id)
        self.db.commit()
        return self._tokens_for(user, workspace_id)

    def refresh(self, refresh_token: str) -> AuthTokens:
        token_hash = hash_token(refresh_token)
        record = self.db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        expires_at = record.expires_at if record else None
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=utc_now().tzinfo)
        if not record or record.revoked or not expires_at or expires_at < utc_now():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")
        user = self.db.get(User, record.user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")
        record.revoked = True
        workspace_id = self._default_workspace_id(user.id)
        self._audit(user.id, workspace_id, "auth.refresh", "user", user.id)
        self.db.commit()
        return self._tokens_for(user, workspace_id)

    def logout(self, refresh_token: str | None, user_id: str) -> None:
        if refresh_token:
            record = self.db.scalar(
                select(RefreshToken).where(RefreshToken.token_hash == hash_token(refresh_token))
            )
            if record:
                record.revoked = True
        self._audit(user_id, None, "auth.logout", "user", user_id)
        self.db.commit()

    def current_user(self, user: User, active_workspace_id: str) -> CurrentUserResponse:
        return CurrentUserResponse(
            user=self._user_summary(user),
            workspaces=self._workspace_summaries(user.id),
            active_workspace_id=active_workspace_id,
        )

    def list_workspaces(self, user_id: str) -> WorkspaceList:
        return WorkspaceList(workspaces=self._workspace_summaries(user_id))

    def create_workspace(self, user_id: str, payload: WorkspaceCreate) -> WorkspaceSummary:
        organization_id = payload.organization_id or self._default_organization_id(user_id)
        membership = self._membership_for_organization(user_id, organization_id)
        if membership.role not in {WorkspaceRole.owner.value, WorkspaceRole.admin.value}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient workspace permissions.")
        workspace = Workspace(organization_id=organization_id, name=payload.name.strip())
        self.db.add(workspace)
        self.db.flush()
        self.db.add(WorkspaceMembership(workspace_id=workspace.id, user_id=user_id, role=WorkspaceRole.owner.value))
        self._audit(user_id, workspace.id, "workspace.create", "workspace", workspace.id)
        self.db.commit()
        return self._workspace_summary(user_id, workspace.id)

    def ensure_membership(self, user_id: str, workspace_id: str, roles: set[str] | None = None) -> WorkspaceMembership:
        membership = self.db.scalar(
            select(WorkspaceMembership).where(
                WorkspaceMembership.user_id == user_id,
                WorkspaceMembership.workspace_id == workspace_id,
            )
        )
        if not membership:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Workspace access denied.")
        if roles and membership.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient workspace permissions.")
        return membership

    def audit(self, user_id: str | None, workspace_id: str | None, action: str, target_type: str = "", target_id: str = "") -> None:
        self._audit(user_id, workspace_id, action, target_type, target_id)
        self.db.commit()

    def _tokens_for(self, user: User, workspace_id: str) -> AuthTokens:
        access_token, expires_at = create_access_token(user.id, workspace_id)
        refresh_token = create_refresh_token()
        self.db.add(
            RefreshToken(
                user_id=user.id,
                token_hash=hash_token(refresh_token),
                expires_at=utc_now() + timedelta(days=settings.refresh_token_expire_days),
            )
        )
        self.db.commit()
        return AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            user=self._user_summary(user),
            workspaces=self._workspace_summaries(user.id),
            active_workspace_id=workspace_id,
        )

    def _workspace_summaries(self, user_id: str) -> list[WorkspaceSummary]:
        rows = self.db.execute(
            select(WorkspaceMembership, Workspace, Organization)
            .join(Workspace, Workspace.id == WorkspaceMembership.workspace_id)
            .join(Organization, Organization.id == Workspace.organization_id)
            .where(WorkspaceMembership.user_id == user_id)
        ).all()
        return [
            WorkspaceSummary(
                id=workspace.id,
                organization_id=organization.id,
                organization_name=organization.name,
                name=workspace.name,
                role=WorkspaceRole(membership.role),
            )
            for membership, workspace, organization in rows
        ]

    def _workspace_summary(self, user_id: str, workspace_id: str) -> WorkspaceSummary:
        return next(item for item in self._workspace_summaries(user_id) if item.id == workspace_id)

    def _user_summary(self, user: User) -> UserSummary:
        return UserSummary(id=user.id, email=user.email, name=user.name, is_active=user.is_active)

    def _default_workspace_id(self, user_id: str) -> str:
        membership = self.db.scalar(select(WorkspaceMembership).where(WorkspaceMembership.user_id == user_id))
        if not membership:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No workspace membership found.")
        return membership.workspace_id

    def _default_organization_id(self, user_id: str) -> str:
        membership = self.db.scalar(select(WorkspaceMembership).where(WorkspaceMembership.user_id == user_id))
        workspace = self.db.get(Workspace, membership.workspace_id) if membership else None
        if not workspace:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No organization found.")
        return workspace.organization_id

    def _membership_for_organization(self, user_id: str, organization_id: str) -> WorkspaceMembership:
        membership = self.db.execute(
            select(WorkspaceMembership)
            .join(Workspace, Workspace.id == WorkspaceMembership.workspace_id)
            .where(
                WorkspaceMembership.user_id == user_id,
                Workspace.organization_id == organization_id,
            )
        ).scalar_one_or_none()
        if not membership:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access denied.")
        return membership

    def _audit(self, user_id: str | None, workspace_id: str | None, action: str, target_type: str, target_id: str) -> None:
        self.db.add(
            AuditEvent(
                user_id=user_id,
                workspace_id=workspace_id,
                action=action,
                target_type=target_type,
                target_id=target_id,
            )
        )
