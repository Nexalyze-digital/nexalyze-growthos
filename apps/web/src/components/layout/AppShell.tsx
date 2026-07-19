import type { ReactNode } from "react";
import type { AuthSession } from "@/types/auth";
import { Header } from "./Header";
import { MobileNavigation } from "./MobileNavigation";
import { Sidebar } from "./Sidebar";

type AppShellProps = {
  children: ReactNode;
  onLogout: () => void;
  onWorkspaceChange: (workspaceId: string) => void;
  session: AuthSession;
};

export function AppShell({
  children,
  onLogout,
  onWorkspaceChange,
  session,
}: AppShellProps) {
  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100">
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <Header
            onLogout={onLogout}
            onWorkspaceChange={onWorkspaceChange}
            session={session}
          />
          <main className="flex-1 px-4 py-5 sm:px-6 lg:px-8">{children}</main>
          <MobileNavigation />
        </div>
      </div>
    </div>
  );
}
