"use client";

import { Bell, Search, Command, ChevronDown } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

export function TopNav() {
  const [searchFocused, setSearchFocused] = useState(false);

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white/90 px-6 backdrop-blur-xl">
      {/* Search */}
      <div className="flex flex-1 items-center gap-4">
        <div className={cn(
          "relative w-full max-w-sm transition-all duration-300",
          searchFocused ? "max-w-md" : ""
        )}>
          <Search className={cn(
            "absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 transition-colors duration-200",
            searchFocused ? "text-cyan-500" : "text-slate-400"
          )} />
          <input
            type="text"
            placeholder="Search datasets, models, locations..."
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setSearchFocused(false)}
            className={cn(
              "h-9 w-full rounded-xl border bg-slate-50 pl-10 pr-12 text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none transition-all duration-300",
              searchFocused
                ? "border-cyan-400 bg-white shadow-sm shadow-cyan-100 ring-1 ring-cyan-400/30"
                : "border-slate-200 hover:border-slate-300"
            )}
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1 opacity-50">
            <kbd className="flex items-center gap-0.5 rounded border border-slate-200 bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-500">
              <Command className="h-2.5 w-2.5" /> K
            </kbd>
          </div>
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-2">
        {/* System status */}
        <div className="hidden sm:flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5">
          <div className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-50" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
          </div>
          <span className="text-xs font-medium text-emerald-700">All Systems Online</span>
        </div>

        <div className="h-5 w-px bg-slate-200 mx-1" />

        {/* Notifications */}
        <button className="relative flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-500 hover:text-slate-800 hover:bg-slate-50 hover:border-slate-300 transition-all duration-200">
          <Bell className="h-4 w-4" />
          <span className="absolute top-1.5 right-1.5 flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500" />
          </span>
        </button>

        {/* User */}
        <button className="flex items-center gap-2.5 rounded-xl border border-slate-200 bg-white px-3 py-1.5 hover:bg-slate-50 hover:border-slate-300 transition-all duration-200 group">
          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-cyan-500 to-cyan-700 text-white text-xs font-bold shadow-sm">
            A
          </div>
          <span className="text-sm font-medium text-slate-700 hidden sm:block">Admin</span>
          <ChevronDown className="h-3.5 w-3.5 text-slate-400 group-hover:text-slate-600 transition-colors" />
        </button>
      </div>
    </header>
  );
}
