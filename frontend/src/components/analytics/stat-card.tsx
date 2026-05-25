import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { ChevronUp, ChevronDown, LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  change: string;
  trend: "up" | "down";
  icon: LucideIcon;
  color: string;
}

export function StatCard({ title, value, change, trend, icon: Icon, color }: StatCardProps) {
  const colorMap: Record<string, string> = {
    cyan: "text-cyan-400 bg-cyan-400/10 border-cyan-400/20 shadow-cyan-900/20",
    emerald: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20 shadow-emerald-900/20",
    blue: "text-blue-400 bg-blue-400/10 border-blue-400/20 shadow-blue-900/20",
    purple: "text-purple-400 bg-purple-400/10 border-purple-400/20 shadow-purple-900/20",
  };
  
  const selectedColor = colorMap[color] || colorMap.cyan;

  return (
    <Card className="relative overflow-hidden group hover:border-slate-300 transition-all duration-300">
      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-white/5 to-transparent rounded-bl-full -mr-16 -mt-16 transition-transform group-hover:scale-110" />
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-slate-600">{title}</h3>
          <div className={cn("p-2 rounded-lg border shadow-sm", selectedColor)}>
            <Icon className="h-4 w-4" />
          </div>
        </div>
        <div className="flex items-baseline gap-3">
          <h2 className="text-3xl font-bold text-slate-900 tracking-tight">{value}</h2>
          <span className={cn(
            "flex items-center text-sm font-medium",
            trend === "up" ? "text-emerald-400" : "text-red-400"
          )}>
            {trend === "up" ? <ChevronUp className="h-3 w-3 mr-0.5" /> : <ChevronDown className="h-3 w-3 mr-0.5" />}
            {change}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
