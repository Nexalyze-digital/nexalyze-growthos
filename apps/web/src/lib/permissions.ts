import type { AuthSession, WorkspaceRole } from "@/types/auth";

export function activeWorkspaceRole(session: AuthSession): WorkspaceRole {
  return (
    session.workspaces.find(
      (workspace) => workspace.id === session.active_workspace_id,
    )?.role || "viewer"
  );
}

export function canEditWorkspace(role: WorkspaceRole) {
  return role === "owner" || role === "admin" || role === "editor";
}

export function canAdminWorkspace(role: WorkspaceRole) {
  return role === "owner" || role === "admin";
}
