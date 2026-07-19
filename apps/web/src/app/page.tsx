"use client";

import { useState } from "react";
import { AuthGate } from "@/components/auth/AuthGate";
import { BrandBrain } from "@/components/brand-brain/BrandBrain";
import { ContentStudio } from "@/components/content-studio/ContentStudio";
import { DashboardHero } from "@/components/dashboard/DashboardHero";
import { DashboardStats } from "@/components/dashboard/DashboardStats";
import { QuickActions } from "@/components/dashboard/QuickActions";
import { AppShell } from "@/components/layout/AppShell";
import { ResearchHub } from "@/components/research-hub/ResearchHub";
import {
  clearStoredSession,
  getStoredSession,
  logout,
  switchWorkspace,
} from "@/lib/api";
import { activeWorkspaceRole, canEditWorkspace } from "@/lib/permissions";
import type { AuthSession } from "@/types/auth";

export default function HomePage() {
  return (
    <AuthGate>
      {(initialSession, onSessionChange) => (
        <AuthenticatedHome
          initialSession={initialSession}
          onSessionChange={onSessionChange}
        />
      )}
    </AuthGate>
  );
}

function AuthenticatedHome({
  initialSession,
  onSessionChange,
}: {
  initialSession: AuthSession;
  onSessionChange: (session: AuthSession) => void;
}) {
  const [session, setSession] = useState(initialSession);
  const role = activeWorkspaceRole(session);
  const canEdit = canEditWorkspace(role);

  function handleWorkspaceChange(workspaceId: string) {
    switchWorkspace(workspaceId);
    const nextSession = getStoredSession();
    if (nextSession) {
      setSession(nextSession);
      onSessionChange(nextSession);
    }
  }

  async function handleLogout() {
    await logout();
    clearStoredSession();
    window.location.reload();
  }

  return (
    <AppShell
      onLogout={handleLogout}
      onWorkspaceChange={handleWorkspaceChange}
      session={session}
    >
      <div className="space-y-8" id="top" key={session.active_workspace_id}>
        <DashboardHero />
        <DashboardStats />
        <QuickActions />
        <BrandBrain canEdit={canEdit} />
        <ResearchHub canEdit={canEdit} />
        <ContentStudio canEdit={canEdit} />
      </div>
    </AppShell>
  );
}
