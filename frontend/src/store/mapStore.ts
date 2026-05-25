import { create } from 'zustand';

interface MapState {
  center: [number, number];
  zoom: number;
  activeLayers: string[];
  setCenter: (center: [number, number]) => void;
  setZoom: (zoom: number) => void;
  toggleLayer: (layerId: string) => void;
}

export const useMapStore = create<MapState>((set) => ({
  center: [20.5937, 78.9629], // Default to center of India or relevant AOI
  zoom: 5,
  activeLayers: [],
  setCenter: (center) => set({ center }),
  setZoom: (zoom) => set({ zoom }),
  toggleLayer: (layerId) => set((state) => ({
    activeLayers: state.activeLayers.includes(layerId)
      ? state.activeLayers.filter((id) => id !== layerId)
      : [...state.activeLayers, layerId],
  })),
}));
