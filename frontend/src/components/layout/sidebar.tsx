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
  HelpCircle
} from "lucide-react";
import { motion } from "framer-motion";

const navItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Exploration Map", href: "/map", icon: MapIcon },
  { name: "Data Upload", href: "/upload", icon: UploadCloud },
  { name: "AI Analytics", href: "/analytics", icon: Activity },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-full w-64 flex-col border-r border-slate-200 bg-white/60 backdrop-blur-xl">
      <div className="flex h-16 items-center px-6">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-[0_0_15px_rgba(6,182,212,0.3)]">
            <MapIcon className="h-5 w-5" />
          </div>
          <span className="text-lg font-bold tracking-tight text-slate-900">NEXUS-MIND</span>
        </Link>
      </div>

      <div className="flex-1 overflow-y-auto py-6 px-4">
        <nav className="flex flex-col gap-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href || (pathname?.startsWith(item.href) && item.href !== "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 group",
                  isActive 
                    ? "text-slate-900" 
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                )}
              >
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute inset-0 rounded-lg bg-cyan-500/10 border border-cyan-500/20 shadow-[inset_0_0_15px_rgba(6,182,212,0.1)]"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  />
                )}
                <item.icon className={cn("h-5 w-5 relative z-10 transition-colors", isActive ? "text-cyan-400" : "group-hover:text-cyan-400/70")} />
                <span className="relative z-10">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>
      
      <div className="p-4 border-t border-slate-200">
        <nav className="flex flex-col gap-2">
          <Link href="/settings" className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-all">
            <Settings className="h-5 w-5" />
            <span>Settings</span>
          </Link>
          <Link href="/help" className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-all">
            <HelpCircle className="h-5 w-5" />
            <span>Help & Support</span>
          </Link>
        </nav>
      </div>
    </div>
  );
}
