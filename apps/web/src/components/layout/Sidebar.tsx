import {
  BarChart3,
  Brain,
  FileText,
  Home,
  PenLine,
  Search,
  Send,
  Settings,
} from "lucide-react";
import { NAVIGATION_ITEMS } from "@/lib/constants";

const icons = {
  Dashboard: Home,
  "AI Content Studio": PenLine,
  "Brand Brain": Brain,
  "Research Hub": Search,
  Publishing: Send,
  Drafts: FileText,
  Analytics: BarChart3,
  Settings,
};

export function Sidebar() {
  return (
    <aside className="hidden w-72 shrink-0 border-r border-white/10 bg-[#050812] p-6 lg:block">
      <div>
        <p className="text-xl font-semibold text-white">GrowthOS</p>
        <p className="mt-1 text-sm text-slate-500">Nexalyze AI Platform</p>
      </div>

      <nav className="mt-10 space-y-1" aria-label="Primary navigation">
        {NAVIGATION_ITEMS.map((item) => {
          const Icon = icons[item.label as keyof typeof icons];
          const active = item.label === "AI Content Studio";
          return (
            <button
              key={item.label}
              aria-current={active ? "page" : undefined}
              className={
                active
                  ? "flex w-full items-center gap-3 rounded-lg bg-cyan-400 px-3 py-3 text-left text-sm font-semibold text-slate-950"
                  : "flex w-full cursor-not-allowed items-center gap-3 rounded-lg px-3 py-3 text-left text-sm text-slate-500"
              }
              disabled={!active}
              type="button"
            >
              <Icon className="h-4 w-4" aria-hidden="true" />
              <span className="flex-1">{item.label}</span>
              {!active ? <span className="text-xs">Soon</span> : null}
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
