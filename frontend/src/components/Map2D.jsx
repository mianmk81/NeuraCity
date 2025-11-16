import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { getPriorityColor, getMoodColor, getNoiseColor, getTrafficColor } from '../lib/helpers';

// Fix for default marker icons in Leaflet with Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const Map2D = ({
  center = [40.7128, -74.0060], // Default to New York City
  zoom = 13,
  height = '500px',
  onMapClick,
  issues = [],
  moodAreas = [],
  noiseSegments = [],
  trafficSegments = [],
  route = null,
  markers = [],
}) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const onMapClickRef = useRef(onMapClick);
  const layersRef = useRef({
    issues: L.layerGroup(),
    mood: L.layerGroup(),
    noise: L.layerGroup(),
    traffic: L.layerGroup(),
    route: L.layerGroup(),
    markers: L.layerGroup(),
  });

  // Update the ref whenever onMapClick changes
  useEffect(() => {
    onMapClickRef.current = onMapClick;
  }, [onMapClick]);

  // Initialize map
  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    mapInstanceRef.current = L.map(mapRef.current).setView(center, zoom);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(mapInstanceRef.current);

    // Add all layer groups to map
    Object.values(layersRef.current).forEach(layer => {
      layer.addTo(mapInstanceRef.current);
    });

    // Handle map clicks using ref to avoid stale closures
    mapInstanceRef.current.on('click', (e) => {
      if (onMapClickRef.current) {
        onMapClickRef.current({ lat: e.latlng.lat, lng: e.latlng.lng });
      }
    });

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update center and zoom
  useEffect(() => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.setView(center, zoom);
    }
  }, [center, zoom]);

  // Render issue markers
  useEffect(() => {
    const layer = layersRef.current.issues;
    layer.clearLayers();

    issues.forEach((issue) => {
      const isAccident = issue.issue_type && (
        issue.issue_type.toLowerCase().includes('accident') ||
        issue.issue_type.toLowerCase().includes('crash') ||
        issue.issue_type.toLowerCase().includes('collision')
      );
      
      const color = getPriorityColor(issue.priority);
      const size = isAccident ? 32 : 24; // Larger marker for accidents
      const icon = L.divIcon({
        className: 'custom-marker',
        html: `<div style="background-color: ${color}; width: ${size}px; height: ${size}px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.5); ${isAccident ? 'animation: pulse 2s infinite;' : ''}">
          ${isAccident ? '<span style="color: white; font-size: 16px; display: flex; align-items: center; justify-content: center; height: 100%;">🚨</span>' : ''}
        </div>`,
        iconSize: [size, size],
        iconAnchor: [size / 2, size / 2],
      });

      const marker = L.marker([issue.lat, issue.lng], { icon });

      marker.bindPopup(`
        <div style="min-width: 200px;">
          <h3 style="font-weight: bold; margin-bottom: 8px; color: ${isAccident ? '#dc2626' : '#333'};">
            ${isAccident ? '🚨 ' : ''}${issue.issue_type || 'Issue'}
          </h3>
          ${issue.description ? `<p style="margin-bottom: 8px;">${issue.description}</p>` : ''}
          <p style="font-size: 12px; color: #666;">
            <strong>Priority:</strong> <span style="color: ${color};">${issue.priority || 'N/A'}</span><br>
            <strong>Severity:</strong> ${issue.severity?.toFixed(2) || 'N/A'}<br>
            <strong>Status:</strong> ${issue.status || 'open'}<br>
            ${isAccident ? '<strong style="color: #dc2626;">⚠️ URGENT - ACCIDENT</strong><br>' : ''}
            <strong>Reported:</strong> ${issue.created_at ? new Date(issue.created_at).toLocaleString() : 'N/A'}
          </p>
        </div>
      `);

      marker.addTo(layer);
    });
  }, [issues]);

  // Render mood area circles
  useEffect(() => {
    const layer = layersRef.current.mood;
    layer.clearLayers();

    moodAreas.forEach((area) => {
      const color = getMoodColor(area.mood_score);
      const circle = L.circle([area.lat, area.lng], {
        radius: 800, // Increased from 500 to 800 meters for better visibility
        fillColor: color,
        fillOpacity: 0.5, // Increased from 0.3 to 0.5 for better visibility
        color: color,
        weight: 3, // Increased from 2 to 3
      });

      circle.bindPopup(`
        <div style="min-width: 200px; padding: 4px;">
          <h3 style="font-weight: bold; margin-bottom: 8px; color: ${color};">${area.area_id || 'Area'}</h3>
          <p style="font-size: 13px; line-height: 1.6;">
            <strong>Mood Score:</strong> ${area.mood_score?.toFixed(2) || 'N/A'}<br>
            <strong>Posts Analyzed:</strong> ${area.post_count || 0}<br>
            <strong>Sentiment:</strong> ${area.mood_score >= 0.5 ? '😊 Positive' : area.mood_score >= 0 ? '😐 Neutral' : '😞 Negative'}
          </p>
        </div>
      `);

      circle.addTo(layer);
    });
  }, [moodAreas]);

  // Render noise segments
  useEffect(() => {
    const layer = layersRef.current.noise;
    layer.clearLayers();

    noiseSegments.forEach((segment) => {
      const color = getNoiseColor(segment.noise_db);
      const circle = L.circle([segment.lat, segment.lng], {
        radius: 300, // Increased from 200 for better visibility
        fillColor: color,
        fillOpacity: 0.6, // Increased from 0.4 for better visibility
        color: color,
        weight: 2, // Increased from 1
      });

      circle.bindPopup(`
        <div style="min-width: 150px; padding: 4px;">
          <h3 style="font-weight: bold; margin-bottom: 8px; color: ${color};">🔊 Noise Level</h3>
          <p style="font-size: 13px;">
            <strong>Decibels:</strong> ${segment.noise_db?.toFixed(1) || 'N/A'} dB<br>
            <strong>Level:</strong> ${segment.noise_db > 70 ? 'High' : segment.noise_db > 50 ? 'Medium' : 'Low'}
          </p>
        </div>
      `);

      circle.addTo(layer);
    });
  }, [noiseSegments]);

  // Render traffic segments
  useEffect(() => {
    const layer = layersRef.current.traffic;
    layer.clearLayers();

    trafficSegments.forEach((segment) => {
      const color = getTrafficColor(segment.congestion);
      const circle = L.circle([segment.lat, segment.lng], {
        radius: 250, // Increased from 150 for better visibility
        fillColor: color,
        fillOpacity: 0.6, // Increased from 0.5 for better visibility
        color: color,
        weight: 3, // Increased from 2
      });

      circle.bindPopup(`
        <div style="min-width: 150px; padding: 4px;">
          <h3 style="font-weight: bold; margin-bottom: 8px; color: ${color};">🚗 Traffic</h3>
          <p style="font-size: 13px;">
            <strong>Congestion:</strong> ${(segment.congestion * 100).toFixed(0)}%<br>
            <strong>Level:</strong> ${segment.congestion > 0.7 ? 'Heavy' : segment.congestion > 0.4 ? 'Moderate' : 'Light'}
          </p>
        </div>
      `);

      circle.addTo(layer);
    });
  }, [trafficSegments]);

  // Render route polyline
  useEffect(() => {
    const layer = layersRef.current.route;
    layer.clearLayers();

    if (route && route.path && route.path.length > 0) {
      // Handle both tuple format [lat, lng] and object format {lat, lng}
      const pathCoords = route.path.map(p => {
        if (Array.isArray(p)) {
          // Tuple format: [lat, lng]
          return [p[0], p[1]];
        } else {
          // Object format: {lat, lng}
          return [p.lat, p.lng];
        }
      });
      
      const polyline = L.polyline(
        pathCoords,
        {
          color: '#0284c7',
          weight: 4,
          opacity: 0.8,
        }
      );

      polyline.addTo(layer);

      // Fit map to route bounds
      if (mapInstanceRef.current) {
        mapInstanceRef.current.fitBounds(polyline.getBounds(), { padding: [50, 50] });
      }
    }
  }, [route]);

  // Render custom markers (for origin/destination selection)
  useEffect(() => {
    const layer = layersRef.current.markers;
    layer.clearLayers();

    markers.forEach((markerData) => {
      const icon = L.divIcon({
        className: 'custom-marker',
        html: `<div style="background-color: ${markerData.color || '#0284c7'}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">${markerData.label || ''}</div>`,
        iconSize: [60, 30],
        iconAnchor: [30, 15],
      });

      const marker = L.marker([markerData.lat, markerData.lng], { icon });
      marker.addTo(layer);
    });
  }, [markers]);

  return (
    <div
      ref={mapRef}
      style={{ height, width: '100%' }}
      className="rounded-lg shadow-lg z-0"
    />
  );
};

export default Map2D;
