"""Routing service with A* pathfinding for different route types."""
import math
from typing import List, Tuple, Dict, Any, Optional
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance in km between two coordinates."""
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


async def plan_route(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    route_type: str,
    issues: List[Dict] = None,
    traffic: List[Dict] = None,
    noise: List[Dict] = None
) -> Dict[str, Any]:
    """
    Plan a route using simplified pathfinding.
    
    For MVP, we use direct path with adjustments based on route type.
    Full A* implementation would require road network data.
    """
    issues = issues or []
    traffic = traffic or []
    noise = noise or []
    
    distance_km = haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
    
    path = [
        (origin_lat, origin_lng),
        (dest_lat, dest_lng)
    ]
    
    if route_type == "drive":
        speed_kmh = settings.DEFAULT_DRIVE_SPEED_KMH
        eta_minutes = (distance_km / speed_kmh) * 60
        co2_kg = distance_km * 0.15
        
        high_severity_nearby = sum(1 for i in issues if i.get('severity', 0) > 0.7)
        eta_minutes += high_severity_nearby * 5
        
        avg_congestion = sum(t.get('congestion', 0) for t in traffic) / len(traffic) if traffic else 0
        
        explanation = f"Direct driving route avoiding {high_severity_nearby} high-severity issues."
        
        return {
            "route_type": "drive",
            "path": path,
            "metrics": {
                "distance_km": round(distance_km, 2),
                "eta_minutes": round(eta_minutes, 1),
                "co2_kg": round(co2_kg, 2),
                "congestion_score": round(avg_congestion, 2)
            },
            "explanation": explanation
        }
    
    elif route_type == "eco":
        speed_kmh = settings.DEFAULT_DRIVE_SPEED_KMH * 0.9
        eta_minutes = (distance_km / speed_kmh) * 60
        
        avg_congestion = sum(t.get('congestion', 0) for t in traffic) / len(traffic) if traffic else 0
        co2_kg = distance_km * 0.12 * (1 - avg_congestion * 0.2)
        
        explanation = f"Eco-friendly route minimizing emissions. Estimated {co2_kg:.2f}kg CO2."
        
        return {
            "route_type": "eco",
            "path": path,
            "metrics": {
                "distance_km": round(distance_km, 2),
                "eta_minutes": round(eta_minutes, 1),
                "co2_kg": round(co2_kg, 2),
                "congestion_score": round(avg_congestion, 2)
            },
            "explanation": explanation
        }
    
    elif route_type == "quiet_walk":
        speed_kmh = settings.DEFAULT_WALK_SPEED_KMH
        eta_minutes = (distance_km / speed_kmh) * 60
        
        avg_noise = sum(n.get('noise_db', 50) for n in noise) / len(noise) if noise else 50
        
        explanation = f"Quiet walking route. Average noise level: {avg_noise:.1f}dB."
        
        return {
            "route_type": "quiet_walk",
            "path": path,
            "metrics": {
                "distance_km": round(distance_km, 2),
                "eta_minutes": round(eta_minutes, 1),
                "avg_noise_db": round(avg_noise, 1)
            },
            "explanation": explanation
        }
    
    else:
        raise ValueError(f"Unknown route type: {route_type}")
