"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { PredictionTrendChart } from "@/components/analytics/prediction-trend-chart";
import { FeatureImportanceChart } from "@/components/analytics/feature-importance-chart";
import { Activity, ShieldCheck, Zap, Database } from "lucide-react";

export default function AnalyticsPage() {
  return (
    <div className="flex flex-col gap-6 max-w-[1600px] mx-auto pb-10">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 mb-1">AI Analytics</h1>
        <p className="text-slate-600">Deep dive into model performance, interpretability, and system health.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-white/60">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-400">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-600">System Status</p>
              <h3 className="text-xl font-bold text-slate-900">Operational</h3>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/60">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 rounded-lg bg-cyan-500/10 text-cyan-400">
              <Zap className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-600">Inference Latency</p>
              <h3 className="text-xl font-bold text-slate-900">2.4s avg</h3>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/60">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 rounded-lg bg-purple-500/10 text-purple-400">
              <Activity className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-600">Active Models</p>
              <h3 className="text-xl font-bold text-slate-900">4 Ensembles</h3>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/60">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 rounded-lg bg-blue-500/10 text-blue-400">
              <Database className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-600">Data Processed</p>
              <h3 className="text-xl font-bold text-slate-900">14.2 TB</h3>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
        >
          <Card className="h-[450px]">
            <CardHeader>
              <CardTitle>SHAP Global Explainability</CardTitle>
              <CardDescription>Average absolute SHAP value by feature across all predictions.</CardDescription>
            </CardHeader>
            <CardContent className="h-[350px]">
              <FeatureImportanceChart />
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <Card className="h-[450px]">
            <CardHeader>
              <CardTitle>Inference Volume & Confidence</CardTitle>
              <CardDescription>Daily prediction requests and average confidence score.</CardDescription>
            </CardHeader>
            <CardContent className="h-[350px]">
              <PredictionTrendChart />
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Model Version History</CardTitle>
            <CardDescription>Performance tracking across ensemble updates.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-slate-600 uppercase bg-white/60">
                  <tr>
                    <th className="px-4 py-3 rounded-l-lg font-medium">Version</th>
                    <th className="px-4 py-3 font-medium">Release Date</th>
                    <th className="px-4 py-3 font-medium">ROC AUC</th>
                    <th className="px-4 py-3 font-medium">F1 Score</th>
                    <th className="px-4 py-3 font-medium">Precision</th>
                    <th className="px-4 py-3 rounded-r-lg font-medium">Recall</th>
                  </tr>
                </thead>
                <tbody className="text-slate-600">
                  <tr className="border-b border-slate-200 hover:bg-slate-100">
                    <td className="px-4 py-3 font-mono text-emerald-400">v2.4.1 (Current)</td>
                    <td className="px-4 py-3">Oct 12, 2023</td>
                    <td className="px-4 py-3">0.942</td>
                    <td className="px-4 py-3">0.915</td>
                    <td className="px-4 py-3">0.902</td>
                    <td className="px-4 py-3">0.928</td>
                  </tr>
                  <tr className="border-b border-slate-200 hover:bg-slate-100">
                    <td className="px-4 py-3 font-mono text-slate-600">v2.4.0</td>
                    <td className="px-4 py-3">Sep 28, 2023</td>
                    <td className="px-4 py-3">0.935</td>
                    <td className="px-4 py-3">0.901</td>
                    <td className="px-4 py-3">0.895</td>
                    <td className="px-4 py-3">0.908</td>
                  </tr>
                  <tr className="hover:bg-slate-100">
                    <td className="px-4 py-3 font-mono text-slate-600">v2.3.5</td>
                    <td className="px-4 py-3">Aug 15, 2023</td>
                    <td className="px-4 py-3">0.918</td>
                    <td className="px-4 py-3">0.884</td>
                    <td className="px-4 py-3">0.871</td>
                    <td className="px-4 py-3">0.897</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
