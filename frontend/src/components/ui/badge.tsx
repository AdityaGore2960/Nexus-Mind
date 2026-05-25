import * as React from "react"
import { cn } from "@/lib/utils"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline" | "success" | "warning";
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2",
        {
          "border-transparent bg-slate-50 text-slate-900 shadow hover:bg-slate-50/80": variant === "default",
          "border-transparent bg-slate-800 text-slate-50 hover:bg-slate-100/80": variant === "secondary",
          "border-transparent bg-red-500/20 text-red-400 hover:bg-red-500/30 border-red-500/20": variant === "destructive",
          "text-slate-700 border-slate-300": variant === "outline",
          "border-transparent bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 border-emerald-500/20": variant === "success",
          "border-transparent bg-amber-500/20 text-amber-400 hover:bg-amber-500/30 border-amber-500/20": variant === "warning",
        },
        className
      )}
      {...props}
    />
  )
}

export { Badge }
