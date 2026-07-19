export type WorkspaceRole = "owner" | "admin" | "editor" | "viewer";

export type UserSummary = {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
};

export type WorkspaceSummary = {
  id: string;
  organization_id: string;
  organization_name: string;
  name: string;
  role: WorkspaceRole;
};

export type AuthSession = {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_at: string;
  user: UserSummary;
  workspaces: WorkspaceSummary[];
  active_workspace_id: string;
};

export type RegisterValues = {
  email: string;
  password: string;
  name: string;
  organization_name: string;
  workspace_name: string;
};

export type LoginValues = {
  email: string;
  password: string;
};
