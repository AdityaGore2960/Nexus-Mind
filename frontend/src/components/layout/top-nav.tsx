"use client";

import { Bell, Search, User } from "lucide-react";
import { Button } from "@/components/ui/button";

export function TopNav() {
  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white/60 px-6 backdrop-blur-xl">
      <div className="flex flex-1 items-center gap-4">
        <div className="relative w-full max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-600" />
          <input
            type="text"
            placeholder="Search datasets, models, or locations..."
            className="h-10 w-full rounded-lg border border-slate-200 bg-white/50 pl-10 pr-4 text-sm text-slate-700 placeholder:text-slate-500 focus:border-cyan-500/50 focus:outline-none focus:ring-1 focus:ring-cyan-500/50 transition-all shadow-inner"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
          <span className="text-xs font-medium text-slate-600">System Online</span>
        </div>
        
        <div className="h-6 w-px bg-white/10 mx-2" />
        
        <Button variant="ghost" size="icon" className="relative text-slate-600 hover:text-slate-900 rounded-full">
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
          </span>
        </Button>
        
        <Button variant="outline" className="gap-2 rounded-full border-slate-200 bg-slate-800/50 pl-2 pr-4 hover:bg-slate-100">
          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-cyan-500/20 text-cyan-400">
            <User className="h-4 w-4" />
          </div>
          <span className="text-sm">Admin</span>
        </Button>
      </div>
    </header>
  );
}
