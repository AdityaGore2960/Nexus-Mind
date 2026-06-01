import * as React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost" | "cyan" | "emerald" | "subtle";
  size?: "default" | "sm" | "lg" | "icon";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500/40 disabled:pointer-events-none disabled:opacity-50",
          {
            "bg-slate-900 text-white hover:bg-slate-800 shadow-sm": variant === "default",
            "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-300 hover:text-slate-900 shadow-sm": variant === "outline",
            "text-slate-600 hover:bg-slate-100 hover:text-slate-900": variant === "ghost",
            "bg-cyan-600 text-white hover:bg-cyan-700 shadow-sm shadow-cyan-200": variant === "cyan",
            "bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm shadow-emerald-200": variant === "emerald",
            "bg-slate-100 text-slate-700 hover:bg-slate-200 hover:text-slate-900 border border-slate-200": variant === "subtle",
            "h-9 px-4 py-2": size === "default",
            "h-8 rounded-lg px-3 text-xs": size === "sm",
            "h-10 rounded-xl px-6": size === "lg",
            "h-9 w-9": size === "icon",
          },
          className
        )}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button }
