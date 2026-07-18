import { WandSparkles } from "lucide-react";

export function DashboardHero() {
  return (
    <section className="rounded-lg border border-white/10 bg-slate-900/60 p-6 shadow-2xl shadow-black/20 sm:p-8">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div className="max-w-3xl">
          <div className="flex items-center gap-2 text-sm font-medium text-cyan-300">
            <WandSparkles className="h-4 w-4" aria-hidden="true" />
            Nexalyze GrowthOS
          </div>
          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            AI growth workflows from idea to publish-ready draft.
          </h1>
          <p className="mt-4 text-sm leading-6 text-slate-400 sm:text-base">
            Use the working AI Content Studio to brief, generate, copy, and
            regenerate structured social content from the local FastAPI backend.
          </p>
        </div>
        <div className="rounded-lg border border-cyan-400/20 bg-cyan-400/10 px-4 py-3 text-sm text-cyan-100">
          Mock provider release
        </div>
      </div>
    </section>
  );
}
