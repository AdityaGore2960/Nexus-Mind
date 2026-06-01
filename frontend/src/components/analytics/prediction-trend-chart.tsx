"use client";

import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";

const data = [
  { name: "Mon", count: 400, confidence: 72 },
  { name: "Tue", count: 300, confidence: 76 },
  { name: "Wed", count: 550, confidence: 81 },
  { name: "Thu", count: 278, confidence: 85 },
  { name: "Fri", count: 189, confidence: 88 },
  { name: "Sat", count: 239, confidence: 90 },
  { name: "Sun", count: 349, confidence: 92 },
];

export function PredictionTrendChart() {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#0891b2" stopOpacity={0.18} />
            <stop offset="95%" stopColor="#0891b2" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="colorConf" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.12} />
            <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(15,23,42,0.06)" vertical={false} />
        <XAxis
          dataKey="name"
          fontSize={11}
          tickLine={false}
          axisLine={false}
          dy={8}
          tick={{ fill: "#94a3b8" }}
        />
        <YAxis
          fontSize={11}
          tickLine={false}
          axisLine={false}
          tick={{ fill: "#94a3b8" }}
          tickFormatter={(v) => `${v}`}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "rgba(255, 255, 255, 0.97)",
            borderColor: "rgba(15, 23, 42, 0.08)",
            borderRadius: "10px",
            boxShadow: "0 8px 24px rgba(0,0,0,0.10)",
            color: "#0f172a",
            fontSize: "12px",
            padding: "10px 14px"
          }}
          labelStyle={{ color: "#64748b", marginBottom: "4px", fontWeight: 600 }}
          itemStyle={{ color: "#0891b2" }}
          cursor={{ stroke: "rgba(8, 145, 178, 0.15)", strokeWidth: 1, strokeDasharray: "4 2" }}
        />
        <Area
          type="monotone"
          dataKey="count"
          stroke="#0891b2"
          strokeWidth={2}
          fillOpacity={1}
          fill="url(#colorCount)"
          activeDot={{ r: 5, fill: "#0891b2", stroke: "#fff", strokeWidth: 2 }}
        />
        <Area
          type="monotone"
          dataKey="confidence"
          stroke="#7c3aed"
          strokeWidth={1.5}
          fillOpacity={1}
          fill="url(#colorConf)"
          strokeDasharray="4 2"
          activeDot={{ r: 4, fill: "#7c3aed", stroke: "#fff", strokeWidth: 2 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
