import type { ButtonHTMLAttributes, ElementType, ReactNode } from "react";
import { cn } from "@/lib/utils";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  icon?: ElementType;
  variant?: "primary" | "secondary";
};

export function Button({
  children,
  className,
  icon: Icon,
  variant = "primary",
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-cyan-300 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:cursor-not-allowed disabled:opacity-55",
        variant === "primary"
          ? "bg-cyan-400 text-slate-950 hover:bg-cyan-300"
          : "border border-white/10 bg-white/[0.03] text-slate-100 hover:bg-white/[0.07]",
        className,
      )}
      {...props}
    >
      {Icon ? <Icon className="h-4 w-4" aria-hidden="true" /> : null}
      {children}
    </button>
  );
}
