"use client";

import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";

const data = [
  { name: "Mon", count: 400, confidence: 0.72 },
  { name: "Tue", count: 300, confidence: 0.76 },
  { name: "Wed", count: 550, confidence: 0.81 },
  { name: "Thu", count: 278, confidence: 0.85 },
  { name: "Fri", count: 189, confidence: 0.88 },
  { name: "Sat", count: 239, confidence: 0.90 },
  { name: "Sun", count: 349, confidence: 0.92 },
];

export function PredictionTrendChart() {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
        <XAxis 
          dataKey="name" 
          stroke="#64748b" 
          fontSize={12} 
          tickLine={false} 
          axisLine={false} 
          dy={10} 
        />
        <YAxis 
          stroke="#64748b" 
          fontSize={12} 
          tickLine={false} 
          axisLine={false} 
          tickFormatter={(value) => `${value}`} 
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: "rgba(15, 23, 42, 0.9)", 
            borderColor: "rgba(255,255,255,0.1)",
            borderRadius: "8px",
            boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.5)",
            color: "#f8fafc"
          }} 
          itemStyle={{ color: "#06b6d4" }}
        />
        <Area 
          type="monotone" 
          dataKey="count" 
          stroke="#06b6d4" 
          strokeWidth={2}
          fillOpacity={1} 
          fill="url(#colorCount)" 
          activeDot={{ r: 6, fill: "#06b6d4", stroke: "#fff", strokeWidth: 2 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
