import { Brain, Home, PenLine, Search } from "lucide-react";

const items = [
  { href: "#top", icon: Home, label: "Home" },
  { href: "#brand-brain-title", icon: Brain, label: "Brand" },
  { href: "#research-hub-title", icon: Search, label: "Research" },
  { href: "#content-studio-title", icon: PenLine, label: "Studio" },
];

export function MobileNavigation() {
  return (
    <nav
      aria-label="Mobile navigation"
      className="sticky bottom-0 z-30 border-t border-white/10 bg-[#050812]/95 px-4 py-2 backdrop-blur lg:hidden"
    >
      <div className="grid grid-cols-4 gap-2">
        {items.map(({ href, icon: Icon, label }) => (
          <a
            key={label}
            className="flex flex-col items-center gap-1 rounded-lg px-2 py-2 text-xs font-medium text-slate-300 transition hover:bg-white/[0.06] focus:outline-none focus:ring-2 focus:ring-cyan-300"
            href={href}
          >
            <Icon className="h-4 w-4" aria-hidden="true" />
            {label}
          </a>
        ))}
      </div>
    </nav>
  );
}
