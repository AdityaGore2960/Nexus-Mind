"use client";

import { useState, useCallback } from "react";
import { UploadCloud, File, X, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface FileDropzoneProps {
  accept: string;
  maxSize: string;
  type: "raster" | "tabular";
}

export function FileDropzone({ accept, maxSize, type }: FileDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileSelection = (selectedFile: File) => {
    setFile(selectedFile);
    // Simulate upload progress
    setProgress(0);
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 5;
      });
    }, 100);
  };

  const themeColor = type === "raster" ? "cyan" : "emerald";

  if (file) {
    return (
      <div className="flex flex-col gap-4 p-4 rounded-xl border border-slate-200 bg-white/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={cn("p-2 rounded-lg bg-opacity-20", 
              themeColor === "cyan" ? "bg-cyan-500 text-cyan-400" : "bg-emerald-500 text-emerald-400"
            )}>
              <File className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-700 truncate max-w-[200px]">{file.name}</p>
              <p className="text-xs text-slate-600">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
            </div>
          </div>
          {progress === 100 ? (
            <CheckCircle className="h-5 w-5 text-emerald-400" />
          ) : (
            <Button variant="ghost" size="icon" onClick={() => setFile(null)} className="h-8 w-8 text-slate-600 hover:text-slate-900">
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
        
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-medium">
            <span className="text-slate-600">{progress === 100 ? "Processing complete" : "Uploading..."}</span>
            <span className={themeColor === "cyan" ? "text-cyan-400" : "text-emerald-400"}>{progress}%</span>
          </div>
          <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
            <div 
              className={cn("h-full transition-all duration-300", 
                themeColor === "cyan" ? "bg-cyan-500 shadow-[0_0_10px_#06b6d4]" : "bg-emerald-500 shadow-[0_0_10px_#10b981]"
              )} 
              style={{ width: `${progress}%` }} 
            />
          </div>
        </div>
        
        {progress === 100 && (
          <Button variant={themeColor} className="w-full mt-2">
            View Dataset
          </Button>
        )}
      </div>
    );
  }

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={cn(
        "flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-8 transition-colors cursor-pointer group",
        isDragging 
          ? themeColor === "cyan" ? "border-cyan-500 bg-cyan-500/5" : "border-emerald-500 bg-emerald-500/5" 
          : "border-slate-300 bg-white/50 hover:bg-slate-100 hover:border-slate-400"
      )}
      onClick={() => document.getElementById(`file-upload-${type}`)?.click()}
    >
      <input 
        id={`file-upload-${type}`}
        type="file" 
        accept={accept}
        className="hidden" 
        onChange={(e) => e.target.files && handleFileSelection(e.target.files[0])}
      />
      <div className={cn("p-4 rounded-full bg-slate-800/80 mb-4 transition-transform group-hover:scale-110",
        isDragging && (themeColor === "cyan" ? "bg-cyan-500/20 text-cyan-400" : "bg-emerald-500/20 text-emerald-400")
      )}>
        <UploadCloud className="h-8 w-8 text-slate-600 group-hover:text-slate-900" />
      </div>
      <h3 className="text-sm font-medium text-slate-700 mb-1">
        Drag & drop or <span className={themeColor === "cyan" ? "text-cyan-400" : "text-emerald-400"}>browse</span>
      </h3>
      <p className="text-xs text-slate-500">Supports {accept} (Max {maxSize})</p>
    </div>
  );
}
