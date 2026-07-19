"use client";

import type { AuthSession } from "@/types/auth";

type WorkspaceSwitcherProps = {
  session: AuthSession;
  onWorkspaceChange: (workspaceId: string) => void;
};

export function WorkspaceSwitcher({
  session,
  onWorkspaceChange,
}: WorkspaceSwitcherProps) {
  return (
    <label className="flex items-center gap-2 text-sm text-slate-300">
      <span className="hidden sm:inline">Workspace</span>
      <select
        className="max-w-[220px] rounded-lg border border-white/10 bg-slate-950/80 px-3 py-2 text-sm text-white outline-none focus:border-cyan-300 focus:ring-2 focus:ring-cyan-300/30"
        onChange={(event) => onWorkspaceChange(event.target.value)}
        value={session.active_workspace_id}
      >
        {session.workspaces.map((workspace) => (
          <option key={workspace.id} value={workspace.id}>
            {workspace.name} ({workspace.role})
          </option>
        ))}
      </select>
    </label>
  );
}
