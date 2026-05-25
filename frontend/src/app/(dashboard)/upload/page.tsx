"use client";

import { motion } from "framer-motion";
import { UploadCloud, FileType2, Map, CheckCircle2, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { FileDropzone } from "@/components/upload/file-dropzone";

export default function UploadPage() {
  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 mb-2">Data Upload Center</h1>
        <p className="text-slate-600">Ingest geospatial and tabular datasets for model training or inference.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <Card className="h-full border-cyan-500/20 shadow-[0_0_30px_rgba(6,182,212,0.05)]">
            <CardHeader>
              <div className="w-10 h-10 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center mb-4">
                <Map className="h-5 w-5" />
              </div>
              <CardTitle>Raster Data (GeoTIFF)</CardTitle>
              <CardDescription>Upload satellite imagery, elevation models, or geophysical grids.</CardDescription>
            </CardHeader>
            <CardContent>
              <FileDropzone 
                accept=".tif,.tiff" 
                maxSize="2GB" 
                type="raster"
              />
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <Card className="h-full border-emerald-500/20 shadow-[0_0_30px_rgba(16,185,129,0.05)]">
            <CardHeader>
              <div className="w-10 h-10 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4">
                <FileType2 className="h-5 w-5" />
              </div>
              <CardTitle>Tabular Data (CSV)</CardTitle>
              <CardDescription>Upload geochemical assays, drill hole data, or fault lines.</CardDescription>
            </CardHeader>
            <CardContent>
              <FileDropzone 
                accept=".csv" 
                maxSize="500MB" 
                type="tabular"
              />
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Upload Guidelines */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <Card className="bg-white/60">
          <CardContent className="p-6">
            <h3 className="text-lg font-medium text-slate-900 mb-4">Ingestion Requirements</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-600">
              <ul className="space-y-2">
                <li className="flex gap-2 items-start"><CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 shrink-0" /> GeoTIFFs must have valid CRS definitions (EPSG projection).</li>
                <li className="flex gap-2 items-start"><CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 shrink-0" /> Multi-band rasters are supported (up to 12 bands).</li>
                <li className="flex gap-2 items-start"><CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 shrink-0" /> CSV files must include 'latitude' and 'longitude' (or x, y) columns.</li>
              </ul>
              <ul className="space-y-2">
                <li className="flex gap-2 items-start"><AlertCircle className="h-4 w-4 text-amber-400 mt-0.5 shrink-0" /> Background processing will begin automatically upon upload.</li>
                <li className="flex gap-2 items-start"><AlertCircle className="h-4 w-4 text-amber-400 mt-0.5 shrink-0" /> Large files (&gt;1GB) may take several minutes to index geographically.</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
