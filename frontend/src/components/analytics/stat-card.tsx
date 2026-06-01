import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown, LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  change: string;
  trend: "up" | "down";
  icon: LucideIcon;
  color: string;
}

export function StatCard({ title, value, change, trend, icon: Icon, color }: StatCardProps) {
  const colorConfig: Record<string, { icon: string; bar: string; badge: string }> = {
    cyan: {
      icon: "text-cyan-600 bg-cyan-50 border-cyan-200",
      bar: "from-cyan-500 to-cyan-400",
      badge: "text-cyan-700 bg-cyan-50 border-cyan-200",
    },
    emerald: {
      icon: "text-emerald-600 bg-emerald-50 border-emerald-200",
      bar: "from-emerald-500 to-emerald-400",
      badge: "text-emerald-700 bg-emerald-50 border-emerald-200",
    },
    blue: {
      icon: "text-blue-600 bg-blue-50 border-blue-200",
      bar: "from-blue-500 to-blue-400",
      badge: "text-blue-700 bg-blue-50 border-blue-200",
    },
    purple: {
      icon: "text-purple-600 bg-purple-50 border-purple-200",
      bar: "from-purple-500 to-purple-400",
      badge: "text-purple-700 bg-purple-50 border-purple-200",
    },
  };

  const cfg = colorConfig[color] ?? colorConfig.cyan;

  return (
    <Card className="relative overflow-hidden group cursor-default">
      {/* Top accent bar */}
      <div className={cn("absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r", cfg.bar)} />

      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-4">
          <div className={cn("p-2.5 rounded-xl border", cfg.icon)}>
            <Icon className="h-4 w-4" />
          </div>
          <div className={cn(
            "flex items-center gap-1 px-2 py-1 rounded-lg border text-xs font-medium",
            trend === "up"
              ? "text-emerald-700 bg-emerald-50 border-emerald-200"
              : "text-red-600 bg-red-50 border-red-200"
          )}>
            {trend === "up" ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            {change}
          </div>
        </div>
        <div>
          <div className="text-2xl font-bold text-slate-900 tracking-tight mb-1">{value}</div>
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wide">{title}</div>
        </div>
      </CardContent>
    </Card>
  );
}
