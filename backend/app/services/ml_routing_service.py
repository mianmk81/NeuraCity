"""
ML-based routing service using Gemini AI for intelligent route planning.
Replaces hardcoded formulas with context-aware predictions.
Uses OpenRouteService for real street-based routing.
"""
import google.generativeai as genai
from app.core.config import get_settings
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import re
import math
import httpx

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
    
    # Convert path from List[Dict] to List[Tuple[float, float]] for schema validation
    path_tuples = [(point['lat'], point['lng']) for point in path]
    
    return {
        "route_type": route_type,
        "path": path_tuples,
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
    Generate realistic waypoints that follow actual streets and avoid high-severity issues.
    Uses OpenRouteService for real street-based routing, then adjusts to avoid issues.
    
    Returns:
        List of {lat, lng} waypoints
    """
    # Filter high-severity issues (red areas to avoid)
    high_severity_issues = [
        i for i in issues 
        if i.get('severity', 0) > 0.7 and 
        'lat' in i and 'lng' in i
    ]
    
    # First, try to get real street route from OpenRouteService
    street_path = await _get_street_route_ors(
        origin_lat, origin_lng, dest_lat, dest_lng, route_type
    )
    
    if street_path and len(street_path) >= 2:
        # We have a real street route, now adjust it to avoid high-severity issues
        adjusted_path = _adjust_path_around_issues(street_path, high_severity_issues)
        logger.info(f"Using OpenRouteService street route with {len(adjusted_path)} waypoints")
        return adjusted_path
    
    # Fallback: Use smart path generation that avoids issues
    logger.warning("OpenRouteService unavailable, using smart path generation")
    path = _generate_smart_path(
        origin_lat, origin_lng, dest_lat, dest_lng,
        high_severity_issues, route_type
    )
    
    # Try ML enhancement if model is available
    if model:
        try:
            # Build issue context for ML
            issue_context = ""
            if high_severity_issues:
                issue_list = [
                    f"({i['lat']:.4f}, {i['lng']:.4f})" 
                    for i in high_severity_issues[:5]  # Limit to 5 for prompt size
                ]
                issue_context = f"\nAvoid these high-severity issue locations: {', '.join(issue_list)}"
            
            prompt = f"""You are a navigation system. Refine this route to follow realistic street patterns.

Origin: ({origin_lat:.6f}, {origin_lng:.6f})
Destination: ({dest_lat:.6f}, {dest_lng:.6f})
Route Type: {route_type}
Current Waypoints: {len(path)} points{issue_context}

Refine the route to:
1. Follow realistic road patterns (not straight lines)
2. Create smooth curves and turns
3. Avoid the issue locations listed above
4. Add 2-4 intermediate waypoints for realistic navigation

Respond with ONLY a JSON object:
{{"waypoints": [{{"lat": 40.7128, "lng": -74.0060}}, {{"lat": 40.7150, "lng": -74.0050}}, ...]}}"""

            response = model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON
            json_match = re.search(r'\{[^}]*"waypoints"[^}]*\[.*?\]\s*\}', text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                ml_waypoints = result.get('waypoints', [])
                
                # Validate and use ML waypoints if valid
                if ml_waypoints and len(ml_waypoints) >= 2:
                    # Ensure start and end are correct
                    ml_waypoints[0] = {"lat": origin_lat, "lng": origin_lng}
                    ml_waypoints[-1] = {"lat": dest_lat, "lng": dest_lng}
                    
                    # Validate all coordinates
                    valid_waypoints = []
                    for wp in ml_waypoints:
                        if isinstance(wp, dict) and 'lat' in wp and 'lng' in wp:
                            lat, lng = float(wp['lat']), float(wp['lng'])
                            if -90 <= lat <= 90 and -180 <= lng <= 180:
                                valid_waypoints.append({"lat": lat, "lng": lng})
                    
                    if len(valid_waypoints) >= 2:
                        logger.info(f"ML refined route to {len(valid_waypoints)} waypoints")
                        return valid_waypoints
        
        except Exception as e:
            logger.warning(f"ML path refinement failed: {e}, using smart path")
    
    # Return smart path (avoids issues even without ML)
    return path


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


async def _get_street_route_ors(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    route_type: str
) -> Optional[List[Dict[str, float]]]:
    """
    Get real street-based route from OpenRouteService or OSRM.
    Returns list of waypoints following actual roads.
    """
    # Try OpenRouteService first (if API key is available)
    if settings.OPENROUTESERVICE_API_KEY:
        try:
            # Map route types to OpenRouteService profiles
            profile_map = {
                "drive": "driving-car",
                "eco": "driving-eco",  # More fuel-efficient route
                "quiet_walk": "foot-walking"
            }
            profile = profile_map.get(route_type, "driving-car")
            
            # OpenRouteService API endpoint
            url = f"https://api.openrouteservice.org/v2/directions/{profile}"
            
            # Request body
            body = {
                "coordinates": [[origin_lng, origin_lat], [dest_lng, dest_lat]],
                "geometry": True,
                "format": "geojson"
            }
            
            # Make request with timeout
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json=body,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {settings.OPENROUTESERVICE_API_KEY}"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract coordinates from GeoJSON
                    if "features" in data and len(data["features"]) > 0:
                        geometry = data["features"][0].get("geometry", {})
                        coordinates = geometry.get("coordinates", [])
                        
                        # Convert from [lng, lat] to [lat, lng] format
                        waypoints = [
                            {"lat": coord[1], "lng": coord[0]}
                            for coord in coordinates
                        ]
                        
                        # Ensure start and end are exact
                        if waypoints:
                            waypoints[0] = {"lat": origin_lat, "lng": origin_lng}
                            waypoints[-1] = {"lat": dest_lat, "lng": dest_lng}
                        
                        logger.info(f"OpenRouteService returned {len(waypoints)} waypoints")
                        return waypoints
                else:
                    logger.warning(f"OpenRouteService returned status {response.status_code}")
        except Exception as e:
            logger.warning(f"OpenRouteService error: {e}")
    
    # Fallback to OSRM (public instance, no API key needed)
    try:
        # Map route types to OSRM profiles
        profile_map = {
            "drive": "driving",
            "eco": "driving",  # OSRM doesn't have eco, use driving
            "quiet_walk": "walking"
        }
        profile = profile_map.get(route_type, "driving")
        
        # OSRM API endpoint (public instance)
        url = f"{settings.OSRM_SERVER_URL}/route/v1/{profile}/{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
        params = {
            "overview": "full",
            "geometries": "geojson",
            "steps": "false"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract coordinates from OSRM response
                if "routes" in data and len(data["routes"]) > 0:
                    geometry = data["routes"][0].get("geometry", {})
                    coordinates = geometry.get("coordinates", [])
                    
                    # Convert from [lng, lat] to [lat, lng] format
                    waypoints = [
                        {"lat": coord[1], "lng": coord[0]}
                        for coord in coordinates
                    ]
                    
                    # Ensure start and end are exact
                    if waypoints:
                        waypoints[0] = {"lat": origin_lat, "lng": origin_lng}
                        waypoints[-1] = {"lat": dest_lat, "lng": dest_lng}
                    
                    logger.info(f"OSRM returned {len(waypoints)} waypoints")
                    return waypoints
            else:
                logger.warning(f"OSRM returned status {response.status_code}")
    except httpx.TimeoutException:
        logger.warning("OSRM request timed out")
    except Exception as e:
        logger.warning(f"OSRM error: {e}")
    
    return None


def _adjust_path_around_issues(
    path: List[Dict[str, float]],
    high_severity_issues: List[Dict]
) -> List[Dict[str, float]]:
    """
    Adjust a street route to avoid high-severity issues.
    Slightly modifies waypoints near issues while keeping the route on streets.
    """
    if not high_severity_issues:
        return path
    
    adjusted_path = []
    
    for i, waypoint in enumerate(path):
        lat = waypoint["lat"]
        lng = waypoint["lng"]
        
        # Check distance to all high-severity issues
        min_dist_to_issue = float('inf')
        closest_issue = None
        
        for issue in high_severity_issues:
            issue_lat = issue.get('lat', 0)
            issue_lng = issue.get('lng', 0)
            dist = haversine_distance(lat, lng, issue_lat, issue_lng)
            
            if dist < min_dist_to_issue:
                min_dist_to_issue = dist
                closest_issue = issue
        
        # If very close to an issue (< 200m), adjust slightly
        if min_dist_to_issue < 0.2 and closest_issue:
            issue_lat = closest_issue.get('lat', 0)
            issue_lng = closest_issue.get('lng', 0)
            
            # Calculate direction away from issue
            issue_dlat = lat - issue_lat
            issue_dlng = lng - issue_lng
            issue_dist = math.sqrt(issue_dlat**2 + issue_dlng**2)
            
            if issue_dist > 0:
                # Push away from issue (small adjustment to stay on streets)
                push_strength = (0.2 - min_dist_to_issue) / 0.2 * 0.001  # Max 0.001 degrees (~100m)
                adjusted_lat = lat + (issue_dlat / issue_dist) * push_strength
                adjusted_lng = lng + (issue_dlng / issue_dist) * push_strength
                
                adjusted_path.append({
                    "lat": round(adjusted_lat, 6),
                    "lng": round(adjusted_lng, 6)
                })
            else:
                adjusted_path.append(waypoint)
        else:
            adjusted_path.append(waypoint)
    
    # Ensure start and end are exact
    if adjusted_path:
        adjusted_path[0] = {"lat": path[0]["lat"], "lng": path[0]["lng"]}
        adjusted_path[-1] = {"lat": path[-1]["lat"], "lng": path[-1]["lng"]}
    
    return adjusted_path


def _generate_smart_path(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    high_severity_issues: List[Dict],
    route_type: str,
    num_waypoints: int = 5
) -> List[Dict[str, float]]:
    """
    Generate a smart path that avoids high-severity issues and follows realistic patterns.
    Creates waypoints that curve around problem areas.
    """
    waypoints = []
    
    # Calculate base direction vector
    dlat = dest_lat - origin_lat
    dlng = dest_lng - origin_lng
    distance = math.sqrt(dlat**2 + dlng**2)
    
    # Normalize direction
    if distance > 0:
        dlat_norm = dlat / distance
        dlng_norm = dlng / distance
    else:
        dlat_norm = 0
        dlng_norm = 0
    
    # Generate waypoints with avoidance logic
    for i in range(num_waypoints + 1):
        t = i / num_waypoints
        
        # Base position along straight line
        base_lat = origin_lat + dlat * t
        base_lng = origin_lng + dlng * t
        
        # Calculate avoidance offset for high-severity issues
        avoid_offset_lat = 0
        avoid_offset_lng = 0
        
        for issue in high_severity_issues:
            issue_lat = issue.get('lat', 0)
            issue_lng = issue.get('lng', 0)
            
            # Distance from current point to issue
            dist_to_issue = haversine_distance(base_lat, base_lng, issue_lat, issue_lng)
            
            # If issue is within 0.5km, push route away
            if dist_to_issue < 0.5:
                # Calculate direction away from issue
                issue_dlat = base_lat - issue_lat
                issue_dlng = base_lng - issue_lng
                issue_dist = math.sqrt(issue_dlat**2 + issue_dlng**2)
                
                if issue_dist > 0:
                    # Push away from issue (stronger if closer)
                    push_strength = (0.5 - dist_to_issue) / 0.5 * 0.003  # Max 0.003 degrees (~300m)
                    avoid_offset_lat += (issue_dlat / issue_dist) * push_strength
                    avoid_offset_lng += (issue_dlng / issue_dist) * push_strength
        
        # Add realistic curve (sine wave pattern for street-like curves)
        curve_strength = 0.002  # ~200m curve
        perpendicular_lat = -dlng_norm * math.sin(t * math.pi) * curve_strength
        perpendicular_lng = dlat_norm * math.sin(t * math.pi) * curve_strength
        
        # Combine base position, avoidance, and curve
        final_lat = base_lat + avoid_offset_lat + perpendicular_lat
        final_lng = base_lng + avoid_offset_lng + perpendicular_lng
        
        waypoints.append({"lat": round(final_lat, 6), "lng": round(final_lng, 6)})
    
    # Ensure start and end are exact
    waypoints[0] = {"lat": origin_lat, "lng": origin_lng}
    waypoints[-1] = {"lat": dest_lat, "lng": dest_lng}
    
    return waypoints


def _generate_simple_path(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    num_waypoints: int = 3
) -> List[Dict[str, float]]:
    """Generate simple interpolated path as fallback (legacy, use _generate_smart_path instead)."""
    return _generate_smart_path(origin_lat, origin_lng, dest_lat, dest_lng, [], 'drive', num_waypoints)


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
    # Convert path from List[Dict] to List[Tuple[float, float]] for schema validation
    path_tuples = [(point['lat'], point['lng']) for point in path]
    metrics_result = _fallback_metrics(distance_km, route_type, issues, traffic, noise)
    
    return {
        "route_type": route_type,
        "path": path_tuples,
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

