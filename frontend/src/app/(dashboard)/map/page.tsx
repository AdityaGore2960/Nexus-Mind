"use client";

import dynamic from "next/dynamic";
import { useState } from "react";
import { Layers, Map as MapIcon, SlidersHorizontal, Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { motion, AnimatePresence } from "framer-motion";

// Dynamically import the map to avoid SSR issues with Leaflet
const MapViewer = dynamic(() => import("@/components/map/map-viewer"), { 
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-white/60">
      <div className="flex flex-col items-center gap-3">
        <div className="h-8 w-8 rounded-full border-2 border-cyan-500 border-t-transparent animate-spin" />
        <p className="text-sm font-medium text-cyan-400 animate-pulse">Initializing Global Geospatial Engine...</p>
      </div>
    </div>
  )
});

export default function MapPage() {
  const [showControls, setShowControls] = useState(true);

  return (
    <div className="relative flex flex-col h-[calc(100vh-112px)] w-full rounded-2xl overflow-hidden border border-slate-200 shadow-2xl">
      {/* Absolute Header Overlay */}
      <div className="absolute top-0 left-0 right-0 z-20 flex justify-between items-center p-4 bg-gradient-to-b from-slate-950/80 to-transparent pointer-events-none">
        <div className="pointer-events-auto">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 drop-shadow-md flex items-center gap-2">
            <MapIcon className="h-6 w-6 text-cyan-400" />
            Exploration Map
          </h1>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          className="pointer-events-auto bg-white/70 backdrop-blur-md border-slate-300 hover:bg-slate-100"
          onClick={() => setShowControls(!showControls)}
        >
          <SlidersHorizontal className="h-4 w-4 mr-2" />
          {showControls ? "Hide Controls" : "Show Controls"}
        </Button>
      </div>

      {/* Main Map Area */}
      <div className="flex-1 w-full bg-slate-50 relative z-10">
        <MapViewer />
      </div>

      {/* Control Panel Overlay */}
      <AnimatePresence>
        {showControls && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="absolute top-20 right-4 z-20 w-80 max-h-[calc(100%-6rem)] overflow-y-auto pointer-events-auto"
          >
            <Card className="bg-white/90 backdrop-blur-xl border-slate-200 shadow-2xl">
              <CardHeader className="pb-3 border-b border-slate-200">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Layers className="h-5 w-5 text-cyan-400" />
                  Map Controls
                </CardTitle>
                <CardDescription>Toggle layers and run AI inference</CardDescription>
              </CardHeader>
              <CardContent className="pt-4 flex flex-col gap-5">
                
                {/* Datasets */}
                <div className="space-y-3">
                  <h4 className="text-xs font-semibold text-slate-600 uppercase tracking-wider">Active Layers</h4>
                  
                  <div className="flex items-center justify-between p-2 rounded-lg bg-white/5 hover:bg-slate-200 transition-colors border border-slate-200 cursor-pointer">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
                      <span className="text-sm font-medium text-slate-700">Pilbara Base Map (Sat)</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between p-2 rounded-lg bg-white/5 hover:bg-slate-200 transition-colors border border-slate-200 cursor-pointer">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.8)]" />
                      <span className="text-sm font-medium text-slate-700">Magnetic Anomalies</span>
                    </div>
                  </div>
                </div>

                {/* AI Models */}
                <div className="space-y-3">
                  <h4 className="text-xs font-semibold text-slate-600 uppercase tracking-wider">AI Inference Engine</h4>
                  <div className="p-3 rounded-lg border border-cyan-500/30 bg-cyan-500/5">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-cyan-300">Ensemble Pipeline</span>
                      <span className="text-xs text-cyan-500 bg-cyan-500/10 px-2 py-0.5 rounded">v2.4.1</span>
                    </div>
                    <p className="text-xs text-slate-600 mb-3">Combines CNN vision with XGBoost tabular features for max accuracy.</p>
                    <Button variant="cyan" className="w-full text-xs h-8">
                      Run Inference Area
                    </Button>
                  </div>
                </div>

                {/* Legend */}
                <div className="space-y-2 mt-2">
                  <div className="flex items-center gap-2 text-xs text-slate-600 mb-1">
                    <Info className="h-3.5 w-3.5" />
                    Prospectivity Legend
                  </div>
                  <div className="h-2 w-full rounded-full bg-gradient-to-r from-slate-700 via-amber-500 to-emerald-500" />
                  <div className="flex justify-between text-[10px] text-slate-500 font-medium px-1">
                    <span>Low (0.0)</span>
                    <span>Med (0.5)</span>
                    <span>High (1.0)</span>
                  </div>
                </div>

              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
