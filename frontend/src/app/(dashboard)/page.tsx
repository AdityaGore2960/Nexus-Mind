"use client";

import { motion } from "framer-motion";
import { TrendingUp, Layers, Target, Activity, ArrowRight, ChevronUp, ChevronDown } from "lucide-react";
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
  { id: "job-0912", area: "Pilbara Craton", status: "Completed", score: "High", time: "10 mins ago" },
  { id: "job-0911", area: "Gawler Craton", status: "Processing", score: "-", time: "45 mins ago" },
  { id: "job-0910", area: "Yilgarn Craton", status: "Completed", score: "Medium", time: "2 hours ago" },
  { id: "job-0909", area: "Mt Isa Inlier", status: "Completed", score: "Low", time: "5 hours ago" },
];

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-6 max-w-[1600px] mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 mb-1">Overview</h1>
          <p className="text-slate-600">Monitor model performance and prediction jobs.</p>
        </div>
        <div className="flex gap-3">
          <Link href="/upload">
            <Button variant="outline">Upload Data</Button>
          </Link>
          <Link href="/map">
            <Button variant="cyan" className="gap-2">
              Run Inference <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1, duration: 0.5, ease: "easeOut" }}
          >
            <StatCard {...stat} />
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart */}
        <motion.div 
          className="lg:col-span-2"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Prediction Trend Analysis</CardTitle>
              <CardDescription>Daily prospectivity inference volume and confidence.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] w-full">
                <PredictionTrendChart />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Feature Importance */}
        <motion.div 
          className="lg:col-span-1"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
        >
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Global Feature Importance</CardTitle>
              <CardDescription>Aggregate SHAP values across models.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] w-full">
                <FeatureImportanceChart />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.5 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Recent Inference Jobs</CardTitle>
            <CardDescription>Latest model prediction executions.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-slate-600 uppercase bg-white/60">
                  <tr>
                    <th className="px-4 py-3 rounded-l-lg font-medium">Job ID</th>
                    <th className="px-4 py-3 font-medium">Region / Dataset</th>
                    <th className="px-4 py-3 font-medium">Status</th>
                    <th className="px-4 py-3 font-medium">Avg Score</th>
                    <th className="px-4 py-3 rounded-r-lg font-medium text-right">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {recentJobs.map((job) => (
                    <tr key={job.id} className="border-b border-slate-200 hover:bg-slate-100 transition-colors">
                      <td className="px-4 py-3 font-mono text-cyan-400">{job.id}</td>
                      <td className="px-4 py-3 text-slate-700">{job.area}</td>
                      <td className="px-4 py-3">
                        <span className={cn(
                          "px-2 py-1 rounded-md text-xs font-medium",
                          job.status === "Completed" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : 
                          "bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse"
                        )}>
                          {job.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={cn(
                          job.score === "High" ? "text-emerald-400" :
                          job.score === "Medium" ? "text-amber-400" :
                          job.score === "Low" ? "text-slate-600" : "text-slate-500"
                        )}>
                          {job.score}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right text-slate-600">{job.time}</td>
                    </tr>
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
