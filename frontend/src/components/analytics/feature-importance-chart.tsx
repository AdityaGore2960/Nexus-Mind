"use client";

import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from "recharts";

const data = [
  { name: "Magnetic Anom", value: 0.35, color: "#0ea5e9" }, // sky
  { name: "Gravity (Bouguer)", value: 0.28, color: "#06b6d4" }, // cyan
  { name: "Silica Content", value: 0.18, color: "#10b981" }, // emerald
  { name: "Dist. to Fault", value: 0.12, color: "#8b5cf6" }, // violet
  { name: "NDVI", value: 0.07, color: "#64748b" }, // slate
];

export function FeatureImportanceChart() {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} layout="vertical" margin={{ top: 10, right: 10, left: 20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
        <XAxis type="number" hide />
        <YAxis 
          dataKey="name" 
          type="category" 
          axisLine={false} 
          tickLine={false} 
          stroke="#94a3b8" 
          fontSize={11}
          width={100}
        />
        <Tooltip 
          cursor={{ fill: "rgba(255,255,255,0.05)" }}
          contentStyle={{ 
            backgroundColor: "rgba(15, 23, 42, 0.9)", 
            borderColor: "rgba(255,255,255,0.1)",
            borderRadius: "8px",
            color: "#f8fafc",
            fontSize: "12px"
          }}
          formatter={(value: any) => [Number(value).toFixed(2), "SHAP Impact"]}
        />
        <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
