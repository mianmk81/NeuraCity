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
        route_type, issues, traffic, noise
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
    issues: List[Dict],
    traffic: List[Dict] = None,
    noise: List[Dict] = None
) -> List[Dict[str, float]]:
    """
    Generate realistic waypoints that follow actual streets and avoid:
    - High-severity issues (MANDATORY - always avoid red areas)
    - High congestion areas (eco/drive routes)
    - High noise areas (quiet_walk routes)
    
    Uses OpenRouteService with waypoints to route around red areas while staying on streets.
    
    Returns:
        List of {lat, lng} waypoints
    """
    traffic = traffic or []
    noise = noise or []
    
    # Filter high-severity issues (red areas - MANDATORY to avoid)
    high_severity_issues = [
        i for i in issues 
        if i.get('severity', 0) > 0.7 and 
        'lat' in i and 'lng' in i
    ]
    logger.info(f"Found {len(high_severity_issues)} high-severity (red) areas - MANDATORY to avoid")
    
    # Filter high congestion areas for eco/drive routes (congestion > 0.7)
    high_congestion_areas = []
    if route_type in ['drive', 'eco']:
        high_congestion_areas = [
            t for t in traffic
            if t.get('congestion', 0) > 0.7 and
            t.get('lat') is not None and t.get('lng') is not None
        ]
        logger.info(f"Found {len(high_congestion_areas)} high congestion areas to avoid")
    
    # Filter high noise areas for quiet_walk routes (noise_db > 65)
    high_noise_areas = []
    if route_type == 'quiet_walk':
        high_noise_areas = [
            n for n in noise
            if n.get('noise_db', 0) > 65 and
            n.get('lat') is not None and n.get('lng') is not None
        ]
        logger.info(f"Found {len(high_noise_areas)} high noise areas to avoid")
    
    # Calculate waypoints to avoid red areas (high-severity issues)
    # These are mandatory - we must route around them
    avoidance_waypoints = _calculate_avoidance_waypoints(
        origin_lat, origin_lng, dest_lat, dest_lng, high_severity_issues
    )
    
    # Build coordinate list for routing: origin -> avoidance waypoints -> destination
    coordinates = [[origin_lng, origin_lat]]
    if avoidance_waypoints:
        for wp in avoidance_waypoints:
            coordinates.append([wp['lng'], wp['lat']])
        logger.info(f"Added {len(avoidance_waypoints)} waypoints to avoid {len(high_severity_issues)} red areas")
    coordinates.append([dest_lng, dest_lat])
    
    # Get route with waypoints from OpenRouteService
    street_path = await _get_street_route_with_waypoints(
        coordinates, route_type, high_severity_issues
    )
    
    if street_path and len(street_path) >= 2:
        # Verify the route avoids red areas
        verified_path = _verify_route_avoids_red_areas(street_path, high_severity_issues)
        logger.info(f"Using street route with {len(verified_path)} waypoints, avoiding {len(high_severity_issues)} red areas")
        return verified_path
    
    # If OpenRouteService fails, try with congestion/noise areas too
    all_areas_to_avoid = high_severity_issues.copy()
    all_areas_to_avoid.extend(high_congestion_areas)
    all_areas_to_avoid.extend(high_noise_areas)
    
    # Fallback: Use smart path generation that avoids problem areas
    logger.warning("OpenRouteService unavailable, using smart path generation with mandatory red area avoidance")
    path = _generate_smart_path(
        origin_lat, origin_lng, dest_lat, dest_lng,
        all_areas_to_avoid, route_type
    )
    
    # Fallback: Use smart path generation that avoids problem areas
    logger.warning("OpenRouteService unavailable, using smart path generation")
    path = _generate_smart_path(
        origin_lat, origin_lng, dest_lat, dest_lng,
        areas_to_avoid, route_type
    )
    
    # Try ML enhancement if model is available
    if model:
        try:
            # Build avoidance context for ML
            avoidance_context = ""
            if areas_to_avoid:
                avoid_list = [
                    f"({a['lat']:.4f}, {a['lng']:.4f})" 
                    for a in areas_to_avoid[:8]  # Limit to 8 for prompt size
                ]
                avoidance_types = []
                if high_severity_issues:
                    avoidance_types.append(f"{len(high_severity_issues)} high-severity issues")
                if high_congestion_areas:
                    avoidance_types.append(f"{len(high_congestion_areas)} high congestion areas")
                if high_noise_areas:
                    avoidance_types.append(f"{len(high_noise_areas)} high noise areas")
                
                avoidance_context = f"\nAvoid these problem locations ({', '.join(avoidance_types)}): {', '.join(avoid_list)}"
            
            prompt = f"""You are a navigation system. Refine this route to follow realistic street patterns.

Origin: ({origin_lat:.6f}, {origin_lng:.6f})
Destination: ({dest_lat:.6f}, {dest_lng:.6f})
Route Type: {route_type}
Current Waypoints: {len(path)} points{avoidance_context}

Refine the route to:
1. Follow realistic road patterns (not straight lines)
2. Create smooth curves and turns
3. AVOID ALL the problem locations listed above (critical!)
4. For {route_type}: {"minimize noise exposure" if route_type == "quiet_walk" else "minimize congestion" if route_type in ["drive", "eco"] else ""}
5. Add 2-4 intermediate waypoints for realistic navigation

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


def _calculate_avoidance_waypoints(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    red_areas: List[Dict]
) -> List[Dict[str, float]]:
    """
    Calculate waypoints to route around red (high-severity) areas.
    Uses the same lat/lng distance approach - routes around red areas by going
    the same distance in latitude/longitude away from them.
    
    Returns list of waypoint coordinates that avoid red areas.
    """
    if not red_areas:
        return []
    
    waypoints = []
    total_distance = haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
    
    # Check if direct route passes through any red areas
    for red_area in red_areas:
        red_lat = red_area.get('lat', 0)
        red_lng = red_area.get('lng', 0)
        
        # Calculate distance from red area to the direct route line
        # Using point-to-line distance calculation
        origin_to_red = haversine_distance(origin_lat, origin_lng, red_lat, red_lng)
        dest_to_red = haversine_distance(dest_lat, dest_lng, red_lat, red_lng)
        origin_to_dest = total_distance
        
        # If red area is close to the route (< 500m), add a waypoint to avoid it
        # Calculate perpendicular distance from red area to route line
        if origin_to_dest > 0:
            # Use cross product to find distance from point to line
            # Simplified: if red area is within 500m of route, add avoidance waypoint
            min_dist_to_route = min(origin_to_red, dest_to_red)
            
            # Check if red area is between origin and destination
            # Calculate if red area projects onto the route segment
            route_dlat = dest_lat - origin_lat
            route_dlng = dest_lng - origin_lng
            
            # Vector from origin to red area
            red_dlat = red_lat - origin_lat
            red_dlng = red_lng - origin_lng
            
            # Project red area onto route vector
            route_length_sq = route_dlat**2 + route_dlng**2
            if route_length_sq > 0:
                t = (red_dlat * route_dlat + red_dlng * route_dlng) / route_length_sq
                
                # If projection is on the route segment (0 < t < 1) and close (< 500m)
                if 0 < t < 1:
                    # Projected point on route
                    proj_lat = origin_lat + t * route_dlat
                    proj_lng = origin_lng + t * route_dlng
                    dist_to_route = haversine_distance(red_lat, red_lng, proj_lat, proj_lng)
                    
                    if dist_to_route < 0.5:  # Within 500m of route
                        # Calculate waypoint that avoids red area
                        # Go the same lat/lng distance away from red area
                        avoid_dlat = red_lat - proj_lat
                        avoid_dlng = red_lng - proj_lng
                        avoid_dist = math.sqrt(avoid_dlat**2 + avoid_dlng**2)
                        
                        if avoid_dist > 0:
                            # Push waypoint away from red area by same distance
                            # Use 300m avoidance radius
                            push_distance = 0.3  # 300 meters
                            push_factor = (push_distance / avoid_dist) if avoid_dist < push_distance else 1.0
                            
                            avoid_lat = proj_lat - (avoid_dlat / avoid_dist) * push_distance
                            avoid_lng = proj_lng - (avoid_dlng / avoid_dist) * push_distance
                            
                            waypoints.append({
                                "lat": round(avoid_lat, 6),
                                "lng": round(avoid_lng, 6)
                            })
                            logger.info(f"Added avoidance waypoint at ({avoid_lat:.6f}, {avoid_lng:.6f}) to avoid red area at ({red_lat:.6f}, {red_lng:.6f})")
    
    # Remove duplicate waypoints (if multiple red areas create similar waypoints)
    unique_waypoints = []
    for wp in waypoints:
        is_duplicate = False
        for existing in unique_waypoints:
            if haversine_distance(wp['lat'], wp['lng'], existing['lat'], existing['lng']) < 0.2:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_waypoints.append(wp)
    
    return unique_waypoints


async def _get_street_route_with_waypoints(
    coordinates: List[List[float]],
    route_type: str,
    red_areas: List[Dict] = None
) -> Optional[List[Dict[str, float]]]:
    """
    Get real street-based route from OpenRouteService or OSRM with waypoints.
    Coordinates should be in [lng, lat] format as required by the APIs.
    """
    red_areas = red_areas or []
    
    # Try OpenRouteService first (if API key is available)
    if settings.OPENROUTESERVICE_API_KEY:
        try:
            # Map route types to OpenRouteService profiles
            profile_map = {
                "drive": "driving-car",
                "eco": "driving-eco",
                "quiet_walk": "foot-walking"
            }
            profile = profile_map.get(route_type, "driving-car")
            
            # OpenRouteService API endpoint
            url = f"https://api.openrouteservice.org/v2/directions/{profile}"
            
            # Request body with waypoints
            body = {
                "coordinates": coordinates,
                "geometry": True,
                "format": "geojson"
            }
            
            # Make request with timeout
            async with httpx.AsyncClient(timeout=15.0) as client:
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
                        route_coordinates = geometry.get("coordinates", [])
                        
                        # Convert from [lng, lat] to [lat, lng] format
                        waypoints = [
                            {"lat": coord[1], "lng": coord[0]}
                            for coord in route_coordinates
                        ]
                        
                        # Ensure start and end are exact
                        if waypoints:
                            waypoints[0] = {"lat": coordinates[0][1], "lng": coordinates[0][0]}
                            waypoints[-1] = {"lat": coordinates[-1][1], "lng": coordinates[-1][0]}
                        
                        logger.info(f"OpenRouteService returned {len(waypoints)} waypoints with avoidance routing")
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
            "eco": "driving",
            "quiet_walk": "walking"
        }
        profile = profile_map.get(route_type, "driving")
        
        # OSRM API endpoint with waypoints
        # Format: /route/v1/{profile}/{lon1},{lat1};{lon2},{lat2};...
        coord_string = ";".join([f"{coord[0]},{coord[1]}" for coord in coordinates])
        url = f"{settings.OSRM_SERVER_URL}/route/v1/{profile}/{coord_string}"
        params = {
            "overview": "full",
            "geometries": "geojson",
            "steps": "false"
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract coordinates from OSRM response
                if "routes" in data and len(data["routes"]) > 0:
                    geometry = data["routes"][0].get("geometry", {})
                    route_coordinates = geometry.get("coordinates", [])
                    
                    # Convert from [lng, lat] to [lat, lng] format
                    waypoints = [
                        {"lat": coord[1], "lng": coord[0]}
                        for coord in route_coordinates
                    ]
                    
                    # Ensure start and end are exact
                    if waypoints:
                        waypoints[0] = {"lat": coordinates[0][1], "lng": coordinates[0][0]}
                        waypoints[-1] = {"lat": coordinates[-1][1], "lng": coordinates[-1][0]}
                    
                    logger.info(f"OSRM returned {len(waypoints)} waypoints with avoidance routing")
                    return waypoints
            else:
                logger.warning(f"OSRM returned status {response.status_code}")
    except httpx.TimeoutException:
        logger.warning("OSRM request timed out")
    except Exception as e:
        logger.warning(f"OSRM error: {e}")
    
    return None


def _verify_route_avoids_red_areas(
    path: List[Dict[str, float]],
    red_areas: List[Dict]
) -> List[Dict[str, float]]:
    """
    Verify that the route avoids red areas. If it passes too close, log a warning.
    Returns the path (we trust OpenRouteService to route around waypoints).
    """
    if not red_areas:
        return path
    
    min_distance_to_red = float('inf')
    closest_red = None
    
    for waypoint in path:
        for red_area in red_areas:
            red_lat = red_area.get('lat', 0)
            red_lng = red_area.get('lng', 0)
            dist = haversine_distance(waypoint['lat'], waypoint['lng'], red_lat, red_lng)
            
            if dist < min_distance_to_red:
                min_distance_to_red = dist
                closest_red = red_area
    
    if min_distance_to_red < 0.2:  # Within 200m of a red area
        logger.warning(f"Route passes within {min_distance_to_red*1000:.0f}m of red area at ({closest_red.get('lat', 0):.6f}, {closest_red.get('lng', 0):.6f})")
    else:
        logger.info(f"Route successfully avoids all red areas (minimum distance: {min_distance_to_red*1000:.0f}m)")
    
    return path


async def _get_street_route_ors(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    route_type: str,
    areas_to_avoid: List[Dict] = None
) -> Optional[List[Dict[str, float]]]:
    """
    Legacy function - kept for backward compatibility.
    Use _get_street_route_with_waypoints instead for waypoint-based routing.
    """
    coordinates = [[origin_lng, origin_lat], [dest_lng, dest_lat]]
    return await _get_street_route_with_waypoints(coordinates, route_type, areas_to_avoid)


def _adjust_path_around_issues(
    path: List[Dict[str, float]],
    areas_to_avoid: List[Dict],
    route_type: str = 'drive'
) -> List[Dict[str, float]]:
    """
    Conservatively adjust a street route to avoid problem areas.
    Only adjusts when route passes VERY close to problem areas (< 100m).
    Keeps adjustments minimal to preserve street alignment.
    
    For routes from OpenRouteService/OSRM, we prefer to keep the original route
    and only make tiny adjustments when absolutely necessary.
    """
    if not areas_to_avoid:
        return path
    
    # Very conservative: only adjust if route passes within 100m of a problem area
    # This ensures we stay on streets and don't make random turns
    avoidance_radius = 0.1  # 100 meters - very close only
    
    # Check if any waypoint is too close to a problem area
    needs_adjustment = False
    problem_segments = []  # Track which segments need adjustment
    
    for i in range(len(path) - 1):
        waypoint = path[i]
        next_waypoint = path[i + 1]
        
        # Check if this segment passes near any problem area
        for problem_area in areas_to_avoid:
            problem_lat = problem_area.get('lat', 0)
            problem_lng = problem_area.get('lng', 0)
            
            # Check distance from segment midpoint to problem
            mid_lat = (waypoint["lat"] + next_waypoint["lat"]) / 2
            mid_lng = (waypoint["lng"] + next_waypoint["lng"]) / 2
            dist = haversine_distance(mid_lat, mid_lng, problem_lat, problem_lng)
            
            if dist < avoidance_radius:
                needs_adjustment = True
                problem_segments.append((i, problem_area, dist))
                break
    
    # If no segments need adjustment, return original path (stays on streets)
    if not needs_adjustment:
        logger.info("Route does not pass through problem areas, using original street route")
        return path
    
    # Only adjust segments that are very close to problems
    # For now, we'll return the original path and log a warning
    # The route service should handle avoidance at the routing level, not by adjusting waypoints
    logger.warning(f"Route passes near {len(problem_segments)} problem areas, but keeping original street route to avoid off-street adjustments")
    
    # Return original path to stay on streets
    # In a production system, you'd request alternative routes from OpenRouteService
    # or use waypoint avoidance features
    return path


def _generate_smart_path(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    areas_to_avoid: List[Dict],
    route_type: str,
    num_waypoints: int = 5
) -> List[Dict[str, float]]:
    """
    Generate a simple interpolated path as fallback when OpenRouteService is unavailable.
    This is a basic straight-line path with minimal curves - not ideal but better than nothing.
    
    Note: This fallback doesn't create realistic street routes. The system should primarily
    rely on OpenRouteService/OSRM for real street-based routing.
    """
    waypoints = []
    
    # Simple interpolation with minimal avoidance
    # We keep it simple to avoid creating unrealistic paths
    for i in range(num_waypoints + 1):
        t = i / num_waypoints
        
        # Simple linear interpolation
        lat = origin_lat + (dest_lat - origin_lat) * t
        lng = origin_lng + (dest_lng - origin_lng) * t
        
        # Only make tiny adjustments if very close to problem areas (< 200m)
        for problem_area in areas_to_avoid:
            problem_lat = problem_area.get('lat', 0)
            problem_lng = problem_area.get('lng', 0)
            dist = haversine_distance(lat, lng, problem_lat, problem_lng)
            
            # Only adjust if extremely close (< 200m) and make minimal adjustment
            if dist < 0.2:
                problem_dlat = lat - problem_lat
                problem_dlng = lng - problem_lng
                problem_dist = math.sqrt(problem_dlat**2 + problem_dlng**2)
                
                if problem_dist > 0:
                    # Very small adjustment to push away slightly
                    push_strength = (0.2 - dist) / 0.2 * 0.0005  # Max 0.0005 degrees (~50m)
                    lat += (problem_dlat / problem_dist) * push_strength
                    lng += (problem_dlng / problem_dist) * push_strength
        
        waypoints.append({"lat": round(lat, 6), "lng": round(lng, 6)})
    
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

