"use client";

import { useEffect, useState } from "react";
import { Activity, LogOut } from "lucide-react";
import { getHealth } from "@/lib/api";
import type { AuthSession } from "@/types/auth";
import { WorkspaceSwitcher } from "@/components/workspace/WorkspaceSwitcher";

type HeaderProps = {
  onLogout: () => void;
  onWorkspaceChange: (workspaceId: string) => void;
  session: AuthSession;
};

export function Header({ onLogout, onWorkspaceChange, session }: HeaderProps) {
  const [apiStatus, setApiStatus] = useState<"checking" | "online" | "offline">(
    "checking",
  );

  useEffect(() => {
    let active = true;
    getHealth()
      .then(() => {
        if (active) setApiStatus("online");
      })
      .catch(() => {
        if (active) setApiStatus("offline");
      });
    return () => {
      active = false;
    };
  }, []);

  const statusLabel =
    apiStatus === "checking"
      ? "Checking API"
      : apiStatus === "online"
        ? "API online"
        : "API offline";

  return (
    <header className="sticky top-0 z-20 border-b border-white/10 bg-[#070b14]/90 px-4 py-4 backdrop-blur sm:px-6 lg:px-8">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.2em] text-cyan-300">
            Current section
          </p>
          <h1 className="mt-1 text-xl font-semibold text-white">
            AI Content Studio
          </h1>
        </div>
        <div className="flex flex-wrap items-center justify-end gap-2">
          <WorkspaceSwitcher
            onWorkspaceChange={onWorkspaceChange}
            session={session}
          />
          <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-2 text-sm text-slate-300">
            <Activity
              className={
                apiStatus === "online"
                  ? "h-4 w-4 text-emerald-300"
                  : apiStatus === "offline"
                    ? "h-4 w-4 text-red-300"
                    : "h-4 w-4 text-cyan-300"
              }
              aria-hidden="true"
            />
            {statusLabel}
          </div>
          <button
            className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.08] focus:outline-none focus:ring-2 focus:ring-cyan-300"
            onClick={onLogout}
            type="button"
          >
            <LogOut className="h-4 w-4" aria-hidden="true" />
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
