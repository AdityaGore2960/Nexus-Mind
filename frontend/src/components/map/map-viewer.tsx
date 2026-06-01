"use client";

import { useEffect } from "react";
import { MapContainer, TileLayer, ZoomControl, Polygon, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";

// Fix Leaflet marker icons in Next.js
import L from "leaflet";
const iconRetinaUrl = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png";
const iconUrl = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png";
const shadowUrl = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png";

// Mock data for a highly prospective area
const mockProspectivityGeoJSON = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: { score: 0.88, reason: "High magnetic anomaly, proximity to major fault line." },
      geometry: { type: "Polygon", coordinates: [[[-119.5, 35.0], [-119.5, 35.1], [-119.4, 35.1], [-119.4, 35.0], [-119.5, 35.0]]] }
    },
    {
      type: "Feature",
      properties: { score: 0.45, reason: "Average background values." },
      geometry: { type: "Polygon", coordinates: [[[-119.4, 35.0], [-119.4, 35.1], [-119.3, 35.1], [-119.3, 35.0], [-119.4, 35.0]]] }
    }
  ]
};

export default function MapViewer() {
  useEffect(() => {
    (async function init() {
      // Setup default icons
      // @ts-ignore
      delete L.Icon.Default.prototype._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl,
        iconUrl,
        shadowUrl,
      });
    })();
  }, []);

  // Style function for GeoJSON based on prospectivity score
  const styleFeature = (feature: any) => {
    const score = feature.properties?.score || 0;
    let color = "#475569"; // slate-600
    if (score > 0.7) color = "#10b981"; // emerald-500
    else if (score > 0.4) color = "#f59e0b"; // amber-500

    return {
      fillColor: color,
      weight: 2,
      opacity: 1,
      color: "rgba(15, 23, 42, 0.4)",
      fillOpacity: 0.45
    };
  };

  return (
    <MapContainer
      center={[35.05, -119.4]} // Default somewhere interesting
      zoom={11}
      zoomControl={false}
      style={{ height: "100%", width: "100%", background: "#f8fafc" }}
      className="z-0"
    >
      {/* Light map tiles (CartoDB Positron) */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        maxZoom={20}
      />
      
      {/* Move zoom control to bottom right so it doesn't conflict with our custom UI */}
      <ZoomControl position="bottomright" />

      {/* Render AI Predictions */}
      {mockProspectivityGeoJSON.features.map((feature, index) => {
        // react-leaflet Polygon expects [lat, lng] which is [y, x] from GeoJSON
        const positions = feature.geometry.coordinates[0].map(coord => [coord[1], coord[0]] as [number, number]);
        return (
          <Polygon 
            key={index} 
            positions={positions} 
            pathOptions={styleFeature(feature)}
          >
            <Tooltip className="custom-tooltip" sticky>
              <div className="flex flex-col gap-1 p-1">
                <div className="flex items-center justify-between border-b pb-2 mb-1">
                  <span className="font-bold text-slate-800">Prospectivity Score</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-700 font-bold text-sm">
                    {feature.properties.score.toFixed(2)}
                  </span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  <span className="font-semibold block mb-1">AI Reasoning:</span>
                  {feature.properties.reason}
                </p>
              </div>
            </Tooltip>
          </Polygon>
        );
      })}

    </MapContainer>
  );
}
