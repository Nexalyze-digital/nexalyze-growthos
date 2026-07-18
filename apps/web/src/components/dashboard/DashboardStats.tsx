import { BarChart3, FileText, Gauge, Send } from "lucide-react";
import { Card } from "@/components/ui/Card";

const stats = [
  { icon: FileText, label: "Drafts generated", value: "12" },
  { icon: Send, label: "Ready for review", value: "5" },
  { icon: BarChart3, label: "Demo engagement", value: "82%" },
  { icon: Gauge, label: "Workflow health", value: "Good" },
];

export function DashboardStats() {
  return (
    <section aria-labelledby="demo-stats-title">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h2 id="demo-stats-title" className="text-lg font-semibold text-white">
          Workspace summary
        </h2>
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">
          Demonstration data
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {stats.map(({ icon: Icon, label, value }) => (
          <Card key={label} className="p-5">
            <Icon className="h-5 w-5 text-cyan-300" aria-hidden="true" />
            <p className="mt-4 text-2xl font-semibold text-white">{value}</p>
            <p className="mt-1 text-sm text-slate-400">{label}</p>
          </Card>
        ))}
      </div>
    </section>
  );
}
