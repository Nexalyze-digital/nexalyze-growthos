import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

type CardProps = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode;
};

export function Card({ children, className, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-lg border border-white/10 bg-white/[0.035] p-6 shadow-xl shadow-black/10",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
