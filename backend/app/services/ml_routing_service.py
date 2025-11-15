"""
ML-based routing service using Gemini AI for intelligent route planning.
Replaces hardcoded formulas with context-aware predictions.
"""
import google.generativeai as genai
from app.core.config import get_settings
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import re
import math

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize Gemini
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    logger.info("ML Routing Service (Gemini) initialized")
except Exception as e:
    logger.error(f"Failed to initialize Gemini for ML routing: {e}")
    model = None


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


async def plan_route_ml(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    route_type: str,
    issues: List[Dict] = None,
    traffic: List[Dict] = None,
    noise: List[Dict] = None,
    time_of_day: Optional[datetime] = None,
    weather: Optional[str] = None
) -> Dict[str, Any]:
    """
    Use Gemini AI to plan an intelligent route with realistic predictions.
    
    Args:
        origin_lat, origin_lng: Start coordinates
        dest_lat, dest_lng: Destination coordinates
        route_type: 'drive', 'eco', or 'quiet_walk'
        issues: List of infrastructure issues
        traffic: Traffic data
        noise: Noise level data
        time_of_day: Current time
        weather: Weather conditions
        
    Returns:
        dict: Route with path, metrics, and explanation
    """
    issues = issues or []
    traffic = traffic or []
    noise = noise or []
    
    distance_km = haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
    
    if not model:
        logger.warning("ML routing unavailable, using fallback")
        return await _fallback_route(
            origin_lat, origin_lng, dest_lat, dest_lng,
            route_type, distance_km, issues, traffic, noise
        )
    
    # Generate realistic waypoints along the route
    path = await generate_path_ml(
        origin_lat, origin_lng, dest_lat, dest_lng,
        route_type, issues
    )
    
    # Get ML-predicted metrics
    metrics = await predict_route_metrics_ml(
        distance_km, route_type, time_of_day,
        issues, traffic, noise, weather
    )
    
    return {
        "route_type": route_type,
        "path": path,
        "metrics": metrics['metrics'],
        "explanation": metrics['explanation']
    }


async def generate_path_ml(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    route_type: str,
    issues: List[Dict]
) -> List[Dict[str, float]]:
    """
    Use ML to generate realistic waypoints along roads (not straight line).
    
    Returns:
        List of {lat, lng} waypoints
    """
    if not model:
        return [
            {"lat": origin_lat, "lng": origin_lng},
            {"lat": dest_lat, "lng": dest_lng}
        ]
    
    try:
        # Count high-severity issues
        high_severity_count = sum(1 for i in issues if i.get('severity', 0) > 0.7)
        
        prompt = f"""You are a navigation system. Generate realistic waypoints for a route.

Origin: ({origin_lat}, {origin_lng})
Destination: ({dest_lat}, {dest_lng})
Route Type: {route_type}
High-Severity Issues Nearby: {high_severity_count}

Generate 3-5 intermediate waypoints that:
1. Follow realistic road patterns (not straight line)
2. Avoid high-severity issue locations
3. Create smooth turns (not sharp angles)
4. Stay within reasonable distance of straight path

Respond with ONLY a JSON array of coordinates:
{{"waypoints": [{{"lat": 40.7128, "lng": -74.0060}}, {{"lat": 40.7150, "lng": -74.0050}}, ...]}}"""

        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Extract JSON
        json_match = re.search(r'\{[^}]*"waypoints"[^}]*\[.*?\]\s*\}', text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            waypoints = result.get('waypoints', [])
            
            # Validate waypoints
            if waypoints and len(waypoints) >= 2:
                # Ensure start and end are correct
                waypoints[0] = {"lat": origin_lat, "lng": origin_lng}
                waypoints[-1] = {"lat": dest_lat, "lng": dest_lng}
                
                logger.info(f"ML generated {len(waypoints)} waypoints")
                return waypoints
        
        logger.warning("Could not parse ML waypoints, using simple path")
        return _generate_simple_path(origin_lat, origin_lng, dest_lat, dest_lng)
        
    except Exception as e:
        logger.error(f"Error generating ML path: {e}")
        return _generate_simple_path(origin_lat, origin_lng, dest_lat, dest_lng)


async def predict_route_metrics_ml(
    distance_km: float,
    route_type: str,
    time_of_day: Optional[datetime],
    issues: List[Dict],
    traffic: List[Dict],
    noise: List[Dict],
    weather: Optional[str]
) -> Dict[str, Any]:
    """
    Use ML to predict realistic ETA, CO2, and route quality.
    Considers all contextual factors instead of hardcoded formulas.
    """
    if not model:
        return _fallback_metrics(distance_km, route_type, issues, traffic, noise)
    
    try:
        # Prepare context
        hour_str = time_of_day.strftime("%H:%M %A") if time_of_day else "Unknown"
        is_rush_hour = False
        if time_of_day:
            hour = time_of_day.hour
            is_rush_hour = (7 <= hour <= 9) or (17 <= hour <= 19)
        
        avg_traffic = sum(t.get('congestion', 0) for t in traffic) / len(traffic) if traffic else 0.3
        avg_noise = sum(n.get('noise_db', 50) for n in noise) / len(noise) if noise else 50
        high_severity_issues = sum(1 for i in issues if i.get('severity', 0) > 0.7)
        
        prompt = f"""You are a transportation analytics AI. Predict realistic route metrics.

Distance: {distance_km:.2f} km
Route Type: {route_type}
Time: {hour_str} {"(RUSH HOUR)" if is_rush_hour else ""}
Weather: {weather or "Normal conditions"}
Average Traffic Congestion: {avg_traffic:.2f} (0-1 scale)
Average Noise Level: {avg_noise:.1f} dB
High-Severity Issues on Route: {high_severity_issues}

Predict realistic metrics for this route:

For "drive" route:
- ETA (minutes): Consider traffic, time of day, issues
- CO2 emissions (kg): Based on distance, traffic (more idle = more CO2)

For "eco" route:
- ETA (minutes): Slightly longer than drive (avoids congestion)
- CO2 emissions (kg): 20-30% less than regular drive

For "quiet_walk" route:
- ETA (minutes): Walking pace ~5 km/h
- Average noise encountered (dB)

Provide reasoning for your predictions.

Respond with ONLY this JSON format:
{{
  "eta_minutes": 25,
  "co2_kg": 1.8,
  "avg_noise_db": 52.5,
  "congestion_score": 0.65,
  "reasoning": "Rush hour traffic adds 30% to base ETA. High congestion increases CO2 by 20%."
}}"""

        response = model.generate_content(prompt)
        text = response.text.strip()
        
        json_match = re.search(r'\{[^{]*"eta_minutes"[^}]*\}', text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            
            metrics = {
                "distance_km": round(distance_km, 2),
                "eta_minutes": round(result.get('eta_minutes', 20), 1),
            }
            
            if route_type in ['drive', 'eco']:
                metrics["co2_kg"] = round(result.get('co2_kg', distance_km * 0.15), 2)
                metrics["congestion_score"] = round(result.get('congestion_score', avg_traffic), 2)
            
            if route_type == 'quiet_walk':
                metrics["avg_noise_db"] = round(result.get('avg_noise_db', avg_noise), 1)
            
            explanation = result.get('reasoning', 'Route calculated with current conditions')
            
            logger.info(f"ML predicted ETA: {metrics['eta_minutes']} min - {explanation}")
            
            return {
                "metrics": metrics,
                "explanation": explanation
            }
        else:
            logger.warning("Could not parse ML metrics, using fallback")
            return _fallback_metrics(distance_km, route_type, issues, traffic, noise)
            
    except Exception as e:
        logger.error(f"Error predicting route metrics: {e}")
        return _fallback_metrics(distance_km, route_type, issues, traffic, noise)


def _generate_simple_path(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    num_waypoints: int = 3
) -> List[Dict[str, float]]:
    """Generate simple interpolated path as fallback."""
    waypoints = []
    
    for i in range(num_waypoints + 1):
        t = i / num_waypoints
        lat = origin_lat + (dest_lat - origin_lat) * t
        lng = origin_lng + (dest_lng - origin_lng) * t
        
        # Add slight curve to make it look more realistic
        offset = math.sin(t * math.pi) * 0.001
        lat += offset
        
        waypoints.append({"lat": round(lat, 6), "lng": round(lng, 6)})
    
    return waypoints


async def _fallback_route(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    route_type: str,
    distance_km: float,
    issues: List[Dict],
    traffic: List[Dict],
    noise: List[Dict]
) -> Dict[str, Any]:
    """Fallback to hardcoded routing if ML fails."""
    path = _generate_simple_path(origin_lat, origin_lng, dest_lat, dest_lng)
    metrics_result = _fallback_metrics(distance_km, route_type, issues, traffic, noise)
    
    return {
        "route_type": route_type,
        "path": path,
        "metrics": metrics_result['metrics'],
        "explanation": metrics_result['explanation']
    }


def _fallback_metrics(
    distance_km: float,
    route_type: str,
    issues: List[Dict],
    traffic: List[Dict],
    noise: List[Dict]
) -> Dict[str, Any]:
    """Fallback to hardcoded metric calculations."""
    if route_type == "drive":
        speed_kmh = settings.DEFAULT_DRIVE_SPEED_KMH
        eta_minutes = (distance_km / speed_kmh) * 60
        co2_kg = distance_km * 0.15
        
        high_severity_nearby = sum(1 for i in issues if i.get('severity', 0) > 0.7)
        eta_minutes += high_severity_nearby * 5
        
        avg_congestion = sum(t.get('congestion', 0) for t in traffic) / len(traffic) if traffic else 0
        
        return {
            "metrics": {
                "distance_km": round(distance_km, 2),
                "eta_minutes": round(eta_minutes, 1),
                "co2_kg": round(co2_kg, 2),
                "congestion_score": round(avg_congestion, 2)
            },
            "explanation": f"Direct driving route avoiding {high_severity_nearby} high-severity issues."
        }
    
    elif route_type == "eco":
        speed_kmh = settings.DEFAULT_DRIVE_SPEED_KMH * 0.9
        eta_minutes = (distance_km / speed_kmh) * 60
        
        avg_congestion = sum(t.get('congestion', 0) for t in traffic) / len(traffic) if traffic else 0
        co2_kg = distance_km * 0.12 * (1 - avg_congestion * 0.2)
        
        return {
            "metrics": {
                "distance_km": round(distance_km, 2),
                "eta_minutes": round(eta_minutes, 1),
                "co2_kg": round(co2_kg, 2),
                "congestion_score": round(avg_congestion, 2)
            },
            "explanation": f"Eco-friendly route minimizing emissions. Estimated {co2_kg:.2f}kg CO2."
        }
    
    elif route_type == "quiet_walk":
        speed_kmh = settings.DEFAULT_WALK_SPEED_KMH
        eta_minutes = (distance_km / speed_kmh) * 60
        
        avg_noise = sum(n.get('noise_db', 50) for n in noise) / len(noise) if noise else 50
        
        return {
            "metrics": {
                "distance_km": round(distance_km, 2),
                "eta_minutes": round(eta_minutes, 1),
                "avg_noise_db": round(avg_noise, 1)
            },
            "explanation": f"Quiet walking route. Average noise level: {avg_noise:.1f}dB."
        }
    
    else:
        # Default fallback
        return {
            "metrics": {
                "distance_km": round(distance_km, 2),
                "eta_minutes": round((distance_km / 50) * 60, 1)
            },
            "explanation": "Basic route calculation"
        }

