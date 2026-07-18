import { Home, PenLine, Settings } from "lucide-react";

const items = [
  { icon: Home, label: "Dashboard", disabled: true },
  { icon: PenLine, label: "Studio", disabled: false },
  { icon: Settings, label: "Settings", disabled: true },
];

export function MobileNavigation() {
  return (
    <nav
      aria-label="Mobile navigation"
      className="sticky bottom-0 z-30 border-t border-white/10 bg-[#050812]/95 px-4 py-2 backdrop-blur lg:hidden"
    >
      <div className="grid grid-cols-3 gap-2">
        {items.map(({ icon: Icon, label, disabled }) => (
          <button
            key={label}
            aria-current={!disabled ? "page" : undefined}
            className={
              disabled
                ? "flex flex-col items-center gap-1 rounded-lg px-3 py-2 text-xs text-slate-500"
                : "flex flex-col items-center gap-1 rounded-lg bg-cyan-400 px-3 py-2 text-xs font-semibold text-slate-950"
            }
            disabled={disabled}
            type="button"
          >
            <Icon className="h-4 w-4" aria-hidden="true" />
            {label}
          </button>
        ))}
      </div>
    </nav>
  );
}
