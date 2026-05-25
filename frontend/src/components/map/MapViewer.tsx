"use client";

import React, { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useMapStore } from '@/store/mapStore';
import L from 'leaflet';

// Fix for default Leaflet icon paths in Next.js
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon.src,
  iconRetinaUrl: markerIcon2x.src,
  shadowUrl: markerShadow.src,
});

function MapController() {
  const map = useMap();
  const center = useMapStore(state => state.center);
  const zoom = useMapStore(state => state.zoom);

  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);

  return null;
}

// Color scale for heatmaps (Blue -> Green -> Yellow -> Red)
function getColor(score: number) {
  return score > 0.9 ? '#d73027' :
         score > 0.7 ? '#fc8d59' :
         score > 0.5 ? '#fee090' :
         score > 0.3 ? '#e0f3f8' :
         score > 0.1 ? '#91bfdb' :
                       '#4575b4';
}

export default function MapViewer({ geoData }: { geoData?: any }) {
  const center = useMapStore(state => state.center);
  const zoom = useMapStore(state => state.zoom);
  const activeLayers = useMapStore(state => state.activeLayers);

  // GeoJSON style function for prospectivity heatmaps
  const geoJsonStyle = (feature: any) => {
    const score = feature.properties?.prospectivity_score || 0;
    return {
      fillColor: getColor(score),
      weight: 1,
      opacity: 1,
      color: 'white',
      dashArray: '3',
      fillOpacity: 0.7
    };
  };

  // Add interactive tooltips
  const onEachFeature = (feature: any, layer: L.Layer) => {
    if (feature.properties) {
      const { prospectivity_score, mineral_target, reasoning } = feature.properties;
      const pct = (prospectivity_score * 100).toFixed(1);
      
      let popupContent = `
        <div class="p-1">
          <h4 class="font-bold text-sm mb-1">${mineral_target || 'Target'} Prospectivity</h4>
          <div class="flex items-center gap-2 mb-2">
            <div class="h-3 w-3 rounded-full" style="background-color: ${getColor(prospectivity_score)}"></div>
            <span class="font-medium">${pct}% Confidence</span>
          </div>
      `;
      
      if (reasoning) {
        popupContent += `<p class="text-xs text-gray-600 mt-2 border-t pt-2">${reasoning}</p>`;
      }
      
      popupContent += `</div>`;
      layer.bindTooltip(popupContent, { sticky: true, className: 'custom-tooltip' });
    }
  };

  // Re-render GeoJSON only when data changes to prevent flickering
  const geoJsonLayer = useMemo(() => {
    if (geoData && activeLayers.includes('predictions')) {
      return (
        <GeoJSON 
          key={JSON.stringify(geoData)} // Force remount if data changes
          data={geoData} 
          style={geoJsonStyle}
          onEachFeature={onEachFeature}
        />
      );
    }
    return null;
  }, [geoData, activeLayers]);

  return (
    <MapContainer 
      center={center} 
      zoom={zoom} 
      style={{ height: '100%', width: '100%' }}
      zoomControl={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {geoJsonLayer}
      
      <MapController />
    </MapContainer>
  );
}
