import { Brain, CalendarClock, Search, Settings } from "lucide-react";
import { Card } from "@/components/ui/Card";

const actions = [
  {
    icon: Brain,
    label: "Brand Brain",
    text: "Voice rules and knowledge base are planned.",
  },
  {
    icon: Search,
    label: "Research Hub",
    text: "Insight gathering remains on the roadmap.",
  },
  {
    icon: CalendarClock,
    label: "Publishing",
    text: "Scheduling connectors are coming later.",
  },
  {
    icon: Settings,
    label: "Settings",
    text: "Workspace controls are not active yet.",
  },
];

export function QuickActions() {
  return (
    <section aria-labelledby="quick-actions-title">
      <h2 id="quick-actions-title" className="mb-3 text-lg font-semibold text-white">
        Quick actions
      </h2>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {actions.map(({ icon: Icon, label, text }) => (
          <Card key={label} className="p-5 opacity-80">
            <div className="flex items-center justify-between gap-3">
              <Icon className="h-5 w-5 text-slate-300" aria-hidden="true" />
              <span className="rounded-full border border-white/10 px-2.5 py-1 text-xs text-slate-400">
                Coming soon
              </span>
            </div>
            <h3 className="mt-4 font-semibold text-white">{label}</h3>
            <p className="mt-2 text-sm leading-6 text-slate-400">{text}</p>
          </Card>
        ))}
      </div>
    </section>
  );
}
