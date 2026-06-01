"use client";

import { motion } from "framer-motion";
import { TrendingUp, Layers, Target, Activity, ArrowRight, RefreshCw, Download, Filter } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PredictionTrendChart } from "@/components/analytics/prediction-trend-chart";
import { FeatureImportanceChart } from "@/components/analytics/feature-importance-chart";
import { StatCard } from "@/components/analytics/stat-card";
import Link from "next/link";
import { cn } from "@/lib/utils";

const stats = [
  {
    title: "Total Predictions",
    value: "24,593",
    change: "+12%",
    trend: "up" as const,
    icon: Activity,
    color: "cyan",
  },
  {
    title: "High Prospectivity Zones",
    value: "1,204",
    change: "+5%",
    trend: "up" as const,
    icon: Target,
    color: "emerald",
  },
  {
    title: "Model Accuracy (AUC)",
    value: "0.942",
    change: "+0.01",
    trend: "up" as const,
    icon: TrendingUp,
    color: "blue",
  },
  {
    title: "Active Datasets",
    value: "48",
    change: "-2",
    trend: "down" as const,
    icon: Layers,
    color: "purple",
  },
];

const recentJobs = [
  { id: "job-0912", area: "Pilbara Craton", region: "Western Australia", status: "Completed", score: "High", confidence: "94%", time: "10 mins ago" },
  { id: "job-0911", area: "Gawler Craton", region: "South Australia", status: "Processing", score: "-", confidence: "-", time: "45 mins ago" },
  { id: "job-0910", area: "Yilgarn Craton", region: "Western Australia", status: "Completed", score: "Medium", confidence: "71%", time: "2 hours ago" },
  { id: "job-0909", area: "Mt Isa Inlier", region: "Queensland", status: "Completed", score: "Low", confidence: "42%", time: "5 hours ago" },
];

const scoreConfig: Record<string, string> = {
  High: "text-emerald-700 bg-emerald-50 border-emerald-200",
  Medium: "text-amber-700 bg-amber-50 border-amber-200",
  Low: "text-slate-600 bg-slate-100 border-slate-200",
};

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-7 max-w-[1600px] mx-auto">

      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <div className="h-1 w-6 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500" />
            <span className="text-xs font-semibold text-cyan-600 uppercase tracking-widest">Overview</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 mb-1">
            Mission Control
          </h1>
          <p className="text-slate-500 text-sm">Monitor AI model performance and inference jobs in real time.</p>
        </div>
        <div className="flex gap-2.5 mt-1">
          <Button variant="outline" size="sm" className="gap-1.5">
            <RefreshCw className="h-3.5 w-3.5" /> Refresh
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5">
            <Download className="h-3.5 w-3.5" /> Export
          </Button>
          <Link href="/upload">
            <Button variant="subtle" size="sm">Upload Data</Button>
          </Link>
          <Link href="/map">
            <Button variant="cyan" size="sm" className="gap-2">
              Run Inference <ArrowRight className="h-3.5 w-3.5" />
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08, duration: 0.5, ease: "easeOut" }}
          >
            <StatCard {...stat} />
          </motion.div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Main Chart */}
        <motion.div
          className="lg:col-span-2"
          initial={{ opacity: 0, x: -16 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          <Card className="h-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Prediction Trend Analysis</CardTitle>
                  <CardDescription className="mt-1">Daily prospectivity inference volume and model confidence.</CardDescription>
                </div>
                <div className="flex gap-1.5">
                  {["7D", "30D", "90D"].map((r, i) => (
                    <button key={r} className={cn(
                      "px-2.5 py-1 rounded-lg text-xs font-medium transition-all",
                      i === 0
                        ? "bg-cyan-50 text-cyan-700 border border-cyan-200"
                        : "text-slate-500 hover:text-slate-700 hover:bg-slate-100"
                    )}>{r}</button>
                  ))}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-[280px] w-full">
                <PredictionTrendChart />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Feature Importance */}
        <motion.div
          className="lg:col-span-1"
          initial={{ opacity: 0, x: 16 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
        >
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Feature Importance</CardTitle>
              <CardDescription className="mt-1">Aggregate SHAP values across active ensemble models.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[280px] w-full">
                <FeatureImportanceChart />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.5 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Inference Jobs</CardTitle>
                <CardDescription className="mt-1">Latest model prediction executions across exploration zones.</CardDescription>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="gap-1.5">
                  <Filter className="h-3.5 w-3.5" /> Filter
                </Button>
                <Link href="/analytics">
                  <Button variant="subtle" size="sm">View All</Button>
                </Link>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto -mx-1">
              <table className="w-full text-sm text-left">
                <thead>
                  <tr className="border-b border-slate-100">
                    {["Job ID", "Region / Dataset", "Location", "Status", "Avg Score", "Confidence", "Time"].map((h) => (
                      <th key={h} className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider whitespace-nowrap">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {recentJobs.map((job, i) => (
                    <motion.tr
                      key={job.id}
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.5 + i * 0.06 }}
                      className="border-b border-slate-50 hover:bg-slate-50 transition-colors cursor-pointer"
                    >
                      <td className="px-4 py-3.5">
                        <span className="font-mono text-xs text-cyan-600 bg-cyan-50 border border-cyan-200 px-2 py-1 rounded-md">
                          {job.id}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 font-medium text-slate-800">{job.area}</td>
                      <td className="px-4 py-3.5 text-slate-400 text-xs">{job.region}</td>
                      <td className="px-4 py-3.5">
                        <span className={cn(
                          "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border",
                          job.status === "Completed"
                            ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                            : "bg-amber-50 text-amber-700 border-amber-200"
                        )}>
                          <span className={cn(
                            "h-1.5 w-1.5 rounded-full",
                            job.status === "Completed" ? "bg-emerald-500" : "bg-amber-500 animate-pulse"
                          )} />
                          {job.status}
                        </span>
                      </td>
                      <td className="px-4 py-3.5">
                        {job.score !== "-" ? (
                          <span className={cn("px-2.5 py-1 rounded-lg text-xs font-medium border", scoreConfig[job.score] ?? "text-slate-500")}>
                            {job.score}
                          </span>
                        ) : (
                          <span className="text-slate-300 text-xs">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3.5">
                        <span className="text-slate-700 text-sm font-medium">{job.confidence}</span>
                      </td>
                      <td className="px-4 py-3.5 text-slate-400 text-xs whitespace-nowrap">{job.time}</td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
