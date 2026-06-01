"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Map as MapIcon,
  UploadCloud,
  Activity,
  Settings,
  HelpCircle,
  Zap
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const navItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard, desc: "Overview" },
  { name: "Exploration Map", href: "/map", icon: MapIcon, desc: "Geospatial" },
  { name: "Data Upload", href: "/upload", icon: UploadCloud, desc: "Ingest" },
  { name: "AI Analytics", href: "/analytics", icon: Activity, desc: "Insights" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-full w-64 flex-col border-r border-slate-200 bg-white relative overflow-hidden">
      {/* Top accent line */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent" />

      {/* Logo */}
      <div className="flex h-16 items-center px-5 border-b border-slate-100">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500 to-cyan-600 shadow-md shadow-cyan-200 group-hover:shadow-lg group-hover:shadow-cyan-300 transition-all duration-300">
            <Zap className="h-4 w-4 text-white" />
          </div>
          <div>
            <span className="text-base font-bold tracking-wide text-slate-900">
              NEXUS<span className="text-cyan-500">·</span>MIND
            </span>
            <div className="text-[10px] text-slate-400 font-medium tracking-wider uppercase">AI Platform</div>
          </div>
        </Link>
      </div>

      {/* Nav label */}
      <div className="px-5 pt-5 pb-2">
        <span className="text-[10px] font-semibold tracking-widest text-slate-400 uppercase">Navigation</span>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-4">
        <nav className="flex flex-col gap-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || (pathname?.startsWith(item.href) && item.href !== "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 group",
                  isActive ? "text-slate-900" : "text-slate-500 hover:text-slate-800"
                )}
              >
                <AnimatePresence>
                  {isActive && (
                    <motion.div
                      layoutId="sidebar-active"
                      className="absolute inset-0 rounded-xl bg-cyan-50 border border-cyan-200/80"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.2 }}
                    />
                  )}
                </AnimatePresence>
                <div className={cn(
                  "relative z-10 flex h-8 w-8 items-center justify-center rounded-lg transition-all duration-200",
                  isActive
                    ? "bg-cyan-500 text-white shadow-sm shadow-cyan-200"
                    : "bg-slate-100 text-slate-500 group-hover:bg-slate-200 group-hover:text-slate-700"
                )}>
                  <item.icon className="h-4 w-4" />
                </div>
                <div className="relative z-10 flex flex-col">
                  <span className="leading-none">{item.name}</span>
                  <span className={cn("text-[10px] mt-0.5", isActive ? "text-cyan-600" : "text-slate-400")}>{item.desc}</span>
                </div>
                {isActive && (
                  <div className="relative z-10 ml-auto h-1.5 w-1.5 rounded-full bg-cyan-500" />
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Divider */}
      <div className="mx-4 h-px bg-slate-100" />

      {/* Footer nav */}
      <div className="p-3">
        <nav className="flex flex-col gap-1">
          <Link href="/settings" className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-500 hover:text-slate-800 hover:bg-slate-50 transition-all group">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100 group-hover:bg-slate-200 transition-all">
              <Settings className="h-4 w-4" />
            </div>
            <span>Settings</span>
          </Link>
          <Link href="/help" className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-500 hover:text-slate-800 hover:bg-slate-50 transition-all group">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100 group-hover:bg-slate-200 transition-all">
              <HelpCircle className="h-4 w-4" />
            </div>
            <span>Help & Support</span>
          </Link>
        </nav>

        {/* User card */}
        <div className="mt-3 flex items-center gap-3 rounded-xl bg-slate-50 border border-slate-200 p-3 hover:bg-slate-100 transition-all cursor-pointer">
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-cyan-500 to-cyan-700 flex items-center justify-center text-white text-xs font-bold shadow-sm">
            A
          </div>
          <div className="flex flex-col">
            <span className="text-xs font-semibold text-slate-800">Admin User</span>
            <span className="text-[10px] text-slate-400">admin@nexus.ai</span>
          </div>
          <div className="ml-auto h-2 w-2 rounded-full bg-emerald-500 shadow-sm" />
        </div>
      </div>
    </div>
  );
}
