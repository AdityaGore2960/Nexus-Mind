"use client";

import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from "recharts";

const data = [
  { name: "Magnetic Anom", value: 0.35, color: "#0891b2" },
  { name: "Gravity (Bouguer)", value: 0.28, color: "#2563eb" },
  { name: "Silica Content", value: 0.18, color: "#059669" },
  { name: "Dist. to Fault", value: 0.12, color: "#7c3aed" },
  { name: "NDVI", value: 0.07, color: "#94a3b8" },
];

export function FeatureImportanceChart() {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} layout="vertical" margin={{ top: 10, right: 20, left: 20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(15,23,42,0.06)" horizontal={false} />
        <XAxis
          type="number"
          fontSize={11}
          tickLine={false}
          axisLine={false}
          tick={{ fill: "#94a3b8" }}
          tickFormatter={(v) => v.toFixed(2)}
        />
        <YAxis
          dataKey="name"
          type="category"
          axisLine={false}
          tickLine={false}
          fontSize={11}
          width={110}
          tick={{ fill: "#64748b" }}
        />
        <Tooltip
          cursor={{ fill: "rgba(15,23,42,0.03)" }}
          contentStyle={{
            backgroundColor: "rgba(255, 255, 255, 0.97)",
            borderColor: "rgba(15, 23, 42, 0.08)",
            borderRadius: "10px",
            boxShadow: "0 8px 24px rgba(0,0,0,0.10)",
            color: "#0f172a",
            fontSize: "12px",
            padding: "10px 14px"
          }}
          formatter={(value: unknown) => [Number(value).toFixed(2), "SHAP Impact"]}
        />
        <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={18}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} opacity={0.85} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
