"""
Community Risk Index Service

Calculates composite risk scores for geographic blocks based on multiple factors:
1. Crime score (historical crime incidents)
2. Blight score (property condition, abandonment)
3. Emergency response score (911 wait times)
4. Air quality score (pollution levels)
5. Heat exposure score (urban heat island effect)
6. Traffic speed score (dangerous high-speed areas)

Each factor is scored 0-1 where higher = more risk.
Composite score is a weighted average with spatial smoothing.
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# =====================================================
# CONFIGURATION CONSTANTS
# =====================================================

@dataclass
class RiskConfig:
    """Configuration for risk index calculations."""

    # Factor weights (must sum to 1.0)
    crime_weight: float = 0.25
    blight_weight: float = 0.15
    emergency_response_weight: float = 0.20
    air_quality_weight: float = 0.15
    heat_exposure_weight: float = 0.10
    traffic_speed_weight: float = 0.15

    # Normalization thresholds (max values)
    crime_max_incidents: int = 50
    blight_max_properties: int = 20
    emergency_max_minutes: int = 30
    air_quality_max_aqi: int = 200
    heat_exposure_max_celsius: float = 45.0
    traffic_speed_max_mph: int = 65

    # Spatial parameters
    spatial_radius_meters: float = 500.0
    spatial_decay_factor: float = 0.5

    def validate(self) -> bool:
        """Validate configuration parameters."""
        total_weight = (
            self.crime_weight +
            self.blight_weight +
            self.emergency_response_weight +
            self.air_quality_weight +
            self.heat_exposure_weight +
            self.traffic_speed_weight
        )
        if not (0.99 <= total_weight <= 1.01):  # Allow small floating-point error
            logger.warning(f"Weights sum to {total_weight}, should be 1.0")
            return False
        return True


# Default configuration
DEFAULT_CONFIG = RiskConfig()


# =====================================================
# INDIVIDUAL FACTOR SCORING FUNCTIONS
# =====================================================

def calculate_crime_score(
    incidents_per_month: int,
    severity_multiplier: float = 1.0,
    config: RiskConfig = DEFAULT_CONFIG
) -> float:
    """
    Calculate crime risk score based on incident frequency.

    Args:
        incidents_per_month: Number of crime incidents in past month
        severity_multiplier: Weight for crime severity (1.0=normal, 1.5=violent crimes)
        config: Risk configuration

    Returns:
        Crime score (0-1): 0 = no crime, 1 = max threshold exceeded

    Methodology:
        - Linear normalization up to max threshold
        - Caps at 1.0 for extremely high crime
        - Severity multiplier increases score for violent crimes
    """
    weighted_incidents = incidents_per_month * severity_multiplier
    score = min(1.0, weighted_incidents / config.crime_max_incidents)
    return round(score, 3)


def calculate_blight_score(
    abandoned_buildings: int,
    vacant_lots: int,
    code_violations: int,
    config: RiskConfig = DEFAULT_CONFIG
) -> float:
    """
    Calculate blight risk score based on property conditions.

    Args:
        abandoned_buildings: Count of abandoned/boarded buildings
        vacant_lots: Count of vacant/overgrown lots
        code_violations: Count of active code violations
        config: Risk configuration

    Returns:
        Blight score (0-1): 0 = pristine, 1 = severe abandonment

    Methodology:
        - Weighted sum: buildings (3x) > violations (2x) > lots (1x)
        - Abandoned buildings indicate higher risk than violations
        - Normalized against max properties threshold
    """
    weighted_sum = (
        abandoned_buildings * 3.0 +
        code_violations * 2.0 +
        vacant_lots * 1.0
    )
    score = min(1.0, weighted_sum / (config.blight_max_properties * 6.0))
    return round(score, 3)


def calculate_emergency_response_score(
    avg_response_time_minutes: float,
    percentile_90_time_minutes: float,
    config: RiskConfig = DEFAULT_CONFIG
) -> float:
    """
    Calculate emergency response risk score based on 911 wait times.

    Args:
        avg_response_time_minutes: Average response time
        percentile_90_time_minutes: 90th percentile response time
        config: Risk configuration

    Returns:
        Response score (0-1): 0 = fast response, 1 = dangerously slow

    Methodology:
        - Combines average (70%) and 90th percentile (30%)
        - 90th percentile captures worst-case scenarios
        - Non-linear scaling (square root) to emphasize severe delays
    """
    avg_score = avg_response_time_minutes / config.emergency_max_minutes
    p90_score = percentile_90_time_minutes / config.emergency_max_minutes

    # Weight average more but consider worst-case
    combined_score = (0.7 * avg_score) + (0.3 * p90_score)

    # Non-linear scaling: sqrt to emphasize extreme delays
    score = min(1.0, math.sqrt(combined_score))
    return round(score, 3)


def calculate_air_quality_score(
    aqi_value: int,
    pm25_concentration: Optional[float] = None,
    config: RiskConfig = DEFAULT_CONFIG
) -> float:
    """
    Calculate air quality risk score based on AQI and PM2.5.

    Args:
        aqi_value: Air Quality Index (0-500+)
        pm25_concentration: Optional PM2.5 in µg/m³
        config: Risk configuration

    Returns:
        Air quality score (0-1): 0 = clean air, 1 = hazardous

    Methodology:
        - Primary: AQI-based score (0-50=good, 150+=unhealthy)
        - Secondary: PM2.5 if available (WHO guideline: 25 µg/m³)
        - Non-linear scaling to match EPA health categories

    AQI Categories:
        0-50: Good (0-0.25)
        51-100: Moderate (0.25-0.5)
        101-150: Unhealthy for sensitive (0.5-0.75)
        151-200: Unhealthy (0.75-1.0)
        200+: Very unhealthy/Hazardous (1.0)
    """
    # AQI-based score with non-linear scaling
    if aqi_value <= 50:
        aqi_score = aqi_value / 200.0  # 0-0.25
    elif aqi_value <= 100:
        aqi_score = 0.25 + ((aqi_value - 50) / 200.0)  # 0.25-0.5
    elif aqi_value <= 150:
        aqi_score = 0.5 + ((aqi_value - 100) / 200.0)  # 0.5-0.75
    else:
        aqi_score = 0.75 + ((aqi_value - 150) / 200.0)  # 0.75-1.0+

    aqi_score = min(1.0, aqi_score)

    # If PM2.5 available, blend with AQI
    if pm25_concentration is not None:
        # WHO guideline: 25 µg/m³ annual mean
        pm25_score = min(1.0, pm25_concentration / 100.0)  # Cap at 100 µg/m³
        score = (0.7 * aqi_score) + (0.3 * pm25_score)
    else:
        score = aqi_score

    return round(score, 3)


def calculate_heat_exposure_score(
    avg_temperature_celsius: float,
    max_temperature_celsius: float,
    tree_canopy_percent: float,
    impervious_surface_percent: float,
    config: RiskConfig = DEFAULT_CONFIG
) -> float:
    """
    Calculate heat exposure risk score (urban heat island effect).

    Args:
        avg_temperature_celsius: Average daytime temperature
        max_temperature_celsius: Peak temperature
        tree_canopy_percent: Percentage of tree coverage (0-100)
        impervious_surface_percent: Percentage of concrete/asphalt (0-100)
        config: Risk configuration

    Returns:
        Heat exposure score (0-1): 0 = cool/shaded, 1 = extreme heat

    Methodology:
        - Temperature component (60%): Based on avg and max temps
        - Environment component (40%): Low canopy + high imperviousness = higher risk
        - Heat island effect: concrete/asphalt areas 2-5°C hotter than parks
    """
    # Temperature component (60% of score)
    avg_temp_score = min(1.0, (avg_temperature_celsius - 20) / (config.heat_exposure_max_celsius - 20))
    max_temp_score = min(1.0, (max_temperature_celsius - 25) / (config.heat_exposure_max_celsius - 25))
    temp_component = (0.6 * avg_temp_score) + (0.4 * max_temp_score)
    temp_component = max(0.0, temp_component)  # Don't go negative

    # Environmental component (40% of score)
    canopy_risk = 1.0 - (tree_canopy_percent / 100.0)  # Low canopy = high risk
    impervious_risk = impervious_surface_percent / 100.0  # High concrete = high risk
    env_component = (0.5 * canopy_risk) + (0.5 * impervious_risk)

    # Combine components
    score = (0.6 * temp_component) + (0.4 * env_component)
    return round(score, 3)


def calculate_traffic_speed_score(
    avg_speed_mph: float,
    percentile_85_speed_mph: float,
    pedestrian_volume: int,
    road_type: str = 'residential',
    config: RiskConfig = DEFAULT_CONFIG
) -> float:
    """
    Calculate traffic speed risk score (dangerous high-speed areas).

    Args:
        avg_speed_mph: Average vehicle speed
        percentile_85_speed_mph: 85th percentile speed
        pedestrian_volume: Daily pedestrian count
        road_type: Road classification (residential, arterial, highway)
        config: Risk configuration

    Returns:
        Traffic speed score (0-1): 0 = safe speeds, 1 = dangerous

    Methodology:
        - Speed threshold varies by road type
        - Higher speeds + higher pedestrian volume = higher risk
        - 85th percentile speed indicates speeding behavior

    Safe speed thresholds:
        residential: 25 mph
        arterial: 35 mph
        highway: 55 mph
    """
    # Speed thresholds by road type
    thresholds = {
        'residential': 25,
        'arterial': 35,
        'highway': 55
    }
    safe_threshold = thresholds.get(road_type, 25)

    # Speed component
    avg_speed_score = max(0.0, (avg_speed_mph - safe_threshold) / (config.traffic_speed_max_mph - safe_threshold))
    p85_speed_score = max(0.0, (percentile_85_speed_mph - safe_threshold - 10) / (config.traffic_speed_max_mph - safe_threshold))
    speed_component = min(1.0, (0.6 * avg_speed_score) + (0.4 * p85_speed_score))

    # Pedestrian volume multiplier (more pedestrians = higher risk at same speed)
    # Low volume: 0-50/day, Medium: 50-200, High: 200+
    if pedestrian_volume < 50:
        ped_multiplier = 1.0
    elif pedestrian_volume < 200:
        ped_multiplier = 1.3
    else:
        ped_multiplier = 1.6

    score = min(1.0, speed_component * ped_multiplier)
    return round(score, 3)


# =====================================================
# COMPOSITE SCORING
# =====================================================

def calculate_composite_risk_index(
    crime_score: float,
    blight_score: float,
    emergency_response_score: float,
    air_quality_score: float,
    heat_exposure_score: float,
    traffic_speed_score: float,
    config: RiskConfig = DEFAULT_CONFIG
) -> Dict[str, Any]:
    """
    Calculate composite risk index from individual factor scores.

    Args:
        crime_score: Crime risk (0-1)
        blight_score: Blight risk (0-1)
        emergency_response_score: Emergency response risk (0-1)
        air_quality_score: Air quality risk (0-1)
        heat_exposure_score: Heat exposure risk (0-1)
        traffic_speed_score: Traffic speed risk (0-1)
        config: Risk configuration

    Returns:
        Dict with composite_risk_index (0-1) and risk_category

    Risk Categories:
        low: < 0.3 (minimal intervention needed)
        moderate: 0.3 - 0.5 (monitoring recommended)
        high: 0.5 - 0.7 (active intervention needed)
        critical: > 0.7 (urgent intervention required)
    """
    if not config.validate():
        logger.warning("Config weights don't sum to 1.0, using equal weights")
        composite = (crime_score + blight_score + emergency_response_score +
                    air_quality_score + heat_exposure_score + traffic_speed_score) / 6.0
    else:
        composite = (
            crime_score * config.crime_weight +
            blight_score * config.blight_weight +
            emergency_response_score * config.emergency_response_weight +
            air_quality_score * config.air_quality_weight +
            heat_exposure_score * config.heat_exposure_weight +
            traffic_speed_score * config.traffic_speed_weight
        )

    composite = round(composite, 3)

    # Determine category
    if composite < 0.3:
        category = 'low'
    elif composite < 0.5:
        category = 'moderate'
    elif composite < 0.7:
        category = 'high'
    else:
        category = 'critical'

    return {
        'composite_risk_index': composite,
        'risk_category': category
    }


# =====================================================
# SPATIAL AGGREGATION
# =====================================================

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate great-circle distance between two points in meters.

    Args:
        lat1, lng1: First point coordinates
        lat2, lng2: Second point coordinates

    Returns:
        Distance in meters
    """
    R = 6371000  # Earth radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def apply_spatial_smoothing(
    target_lat: float,
    target_lng: float,
    target_risk: float,
    nearby_blocks: List[Dict[str, Any]],
    config: RiskConfig = DEFAULT_CONFIG
) -> float:
    """
    Apply spatial smoothing to account for nearby block influence.

    Args:
        target_lat, target_lng: Coordinates of target block
        target_risk: Calculated risk for target block
        nearby_blocks: List of dicts with 'lat', 'lng', 'composite_risk_index'
        config: Risk configuration

    Returns:
        Spatially-smoothed risk score

    Methodology:
        - Nearby high-risk blocks increase target block risk
        - Influence decays exponentially with distance
        - Prevents isolated "islands" of low risk in high-risk zones
    """
    if not nearby_blocks:
        return target_risk

    total_weight = 1.0  # Target block starts with weight 1.0
    weighted_risk = target_risk * 1.0

    for block in nearby_blocks:
        distance = haversine_distance(
            target_lat, target_lng,
            block['lat'], block['lng']
        )

        if distance <= config.spatial_radius_meters:
            # Exponential decay: weight = decay_factor ^ (distance / radius)
            weight = config.spatial_decay_factor ** (distance / config.spatial_radius_meters)
            weighted_risk += block['composite_risk_index'] * weight
            total_weight += weight

    smoothed_risk = weighted_risk / total_weight
    return round(smoothed_risk, 3)


# =====================================================
# BATCH CALCULATION
# =====================================================

def calculate_risk_for_block(
    block_id: str,
    lat: float,
    lng: float,
    crime_data: Dict[str, Any],
    blight_data: Dict[str, Any],
    emergency_data: Dict[str, Any],
    air_quality_data: Dict[str, Any],
    heat_data: Dict[str, Any],
    traffic_data: Dict[str, Any],
    config: RiskConfig = DEFAULT_CONFIG
) -> Dict[str, Any]:
    """
    Calculate all risk scores for a single block.

    Args:
        block_id: Unique block identifier
        lat, lng: Block coordinates
        *_data: Dictionaries with raw data for each factor
        config: Risk configuration

    Returns:
        Complete risk profile for the block
    """
    # Calculate individual factor scores
    crime_score = calculate_crime_score(
        crime_data.get('incidents_per_month', 0),
        crime_data.get('severity_multiplier', 1.0),
        config
    )

    blight_score = calculate_blight_score(
        blight_data.get('abandoned_buildings', 0),
        blight_data.get('vacant_lots', 0),
        blight_data.get('code_violations', 0),
        config
    )

    emergency_score = calculate_emergency_response_score(
        emergency_data.get('avg_response_time_minutes', 0),
        emergency_data.get('percentile_90_time_minutes', 0),
        config
    )

    air_quality_score = calculate_air_quality_score(
        air_quality_data.get('aqi_value', 0),
        air_quality_data.get('pm25_concentration'),
        config
    )

    heat_score = calculate_heat_exposure_score(
        heat_data.get('avg_temperature_celsius', 20),
        heat_data.get('max_temperature_celsius', 25),
        heat_data.get('tree_canopy_percent', 30),
        heat_data.get('impervious_surface_percent', 50),
        config
    )

    traffic_score = calculate_traffic_speed_score(
        traffic_data.get('avg_speed_mph', 25),
        traffic_data.get('percentile_85_speed_mph', 30),
        traffic_data.get('pedestrian_volume', 50),
        traffic_data.get('road_type', 'residential'),
        config
    )

    # Calculate composite
    composite_result = calculate_composite_risk_index(
        crime_score,
        blight_score,
        emergency_score,
        air_quality_score,
        heat_score,
        traffic_score,
        config
    )

    return {
        'block_id': block_id,
        'lat': lat,
        'lng': lng,
        'crime_score': crime_score,
        'blight_score': blight_score,
        'emergency_response_score': emergency_score,
        'air_quality_score': air_quality_score,
        'heat_exposure_score': heat_score,
        'traffic_speed_score': traffic_score,
        'composite_risk_index': composite_result['composite_risk_index'],
        'risk_category': composite_result['risk_category'],
        'last_calculated_at': datetime.now()
    }


# =====================================================
# NORMALIZATION UTILITIES
# =====================================================

def normalize_value(
    raw_value: float,
    min_value: float,
    max_value: float,
    invert: bool = False
) -> float:
    """
    Normalize a value to 0-1 scale.

    Args:
        raw_value: Value to normalize
        min_value: Minimum possible value
        max_value: Maximum possible value
        invert: If True, higher raw values = lower scores (e.g., tree canopy)

    Returns:
        Normalized score (0-1)
    """
    if max_value == min_value:
        return 0.5

    normalized = (raw_value - min_value) / (max_value - min_value)
    normalized = max(0.0, min(1.0, normalized))

    if invert:
        normalized = 1.0 - normalized

    return round(normalized, 3)


def percentile(values: List[float], p: int) -> float:
    """
    Calculate percentile of a list of values.

    Args:
        values: List of numeric values
        p: Percentile (0-100)

    Returns:
        Percentile value
    """
    if not values:
        return 0.0

    sorted_values = sorted(values)
    k = (len(sorted_values) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)

    if f == c:
        return sorted_values[int(k)]

    d0 = sorted_values[int(f)] * (c - k)
    d1 = sorted_values[int(c)] * (k - f)
    return d0 + d1


# =====================================================
# LOGGING AND VALIDATION
# =====================================================

def validate_risk_data(block_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate risk calculation input data.

    Args:
        block_data: Complete block data dictionary

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check required fields
    required_fields = ['block_id', 'lat', 'lng']
    for field in required_fields:
        if field not in block_data:
            errors.append(f"Missing required field: {field}")

    # Validate coordinates
    if 'lat' in block_data:
        if not -90 <= block_data['lat'] <= 90:
            errors.append(f"Invalid latitude: {block_data['lat']}")

    if 'lng' in block_data:
        if not -180 <= block_data['lng'] <= 180:
            errors.append(f"Invalid longitude: {block_data['lng']}")

    # Validate scores if present
    score_fields = [
        'crime_score', 'blight_score', 'emergency_response_score',
        'air_quality_score', 'heat_exposure_score', 'traffic_speed_score',
        'composite_risk_index'
    ]

    for field in score_fields:
        if field in block_data:
            value = block_data[field]
            if not 0 <= value <= 1:
                errors.append(f"Invalid {field}: {value} (must be 0-1)")

    return (len(errors) == 0, errors)


# =====================================================
# RISK INDEX SERVICE CLASS
# =====================================================

class RiskIndexService:
    """Service class for risk index operations with database integration."""
    
    def __init__(self, db_service):
        """
        Initialize RiskIndexService.
        
        Args:
            db_service: SupabaseService instance
        """
        self.db = db_service
    
    async def get_risk_blocks_in_bounds(
        self,
        min_lat: float,
        max_lat: float,
        min_lng: float,
        max_lng: float,
        min_risk: Optional[float] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get risk blocks within geographic bounds with optional filtering.
        
        Args:
            min_lat: Minimum latitude
            max_lat: Maximum latitude
            min_lng: Minimum longitude
            max_lng: Maximum longitude
            min_risk: Optional minimum risk score filter
            limit: Maximum number of results
            
        Returns:
            List of risk block dictionaries
        """
        blocks = await self.db.get_risk_blocks_in_bounds(min_lat, max_lat, min_lng, max_lng)
        
        # Apply min_risk filter if provided
        if min_risk is not None:
            blocks = [b for b in blocks if b.get('composite_risk_index', 0) >= min_risk]
        
        # Apply limit
        if limit and len(blocks) > limit:
            blocks = blocks[:limit]
        
        return blocks
    
    async def get_risk_block_details(self, block_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed risk breakdown for a specific block.
        
        Args:
            block_id: Block identifier
            
        Returns:
            Risk block dictionary with full details, or None if not found
        """
        return await self.db.get_risk_block_by_id(block_id)
    
    async def update_risk_blocks_in_area(
        self,
        min_lat: float,
        max_lat: float,
        min_lng: float,
        max_lng: float,
        block_size: float = 0.01
    ) -> int:
        """
        Update risk blocks in an area by recalculating risk scores.
        
        This method would trigger recalculation of risk scores for all blocks
        in the specified area. For now, it returns the count of blocks that
        would be updated.
        
        Args:
            min_lat: Minimum latitude of area
            max_lat: Maximum latitude of area
            min_lng: Minimum longitude of area
            max_lng: Maximum longitude of area
            block_size: Size of each block in degrees (default 0.01 ~ 1km)
            
        Returns:
            Number of blocks updated
        """
        # Get existing blocks in the area
        blocks = await self.db.get_risk_blocks_in_bounds(min_lat, max_lat, min_lng, max_lng)
        
        # TODO: Implement actual risk recalculation logic here
        # This would involve:
        # 1. Fetching raw data (issues, accidents, traffic) for each block
        # 2. Calculating risk scores using calculate_risk_for_block()
        # 3. Updating database with new scores
        
        logger.info(f"Would update {len(blocks)} risk blocks in area")
        return len(blocks)


if __name__ == "__main__":
    # Example usage
    print("NeuraCity Community Risk Index Service")
    print("=" * 50)

    # Example calculation
    example_block = calculate_risk_for_block(
        block_id='BLK_40.712_-74.006',
        lat=40.712,
        lng=-74.006,
        crime_data={'incidents_per_month': 15, 'severity_multiplier': 1.2},
        blight_data={'abandoned_buildings': 2, 'vacant_lots': 3, 'code_violations': 5},
        emergency_data={'avg_response_time_minutes': 8.5, 'percentile_90_time_minutes': 12.0},
        air_quality_data={'aqi_value': 75, 'pm25_concentration': 20.0},
        heat_data={'avg_temperature_celsius': 28, 'max_temperature_celsius': 35,
                   'tree_canopy_percent': 15, 'impervious_surface_percent': 75},
        traffic_data={'avg_speed_mph': 35, 'percentile_85_speed_mph': 42,
                     'pedestrian_volume': 150, 'road_type': 'arterial'}
    )

    print(f"\nExample Block: {example_block['block_id']}")
    print(f"Location: ({example_block['lat']}, {example_block['lng']})")
    print(f"\nFactor Scores:")
    print(f"  Crime: {example_block['crime_score']}")
    print(f"  Blight: {example_block['blight_score']}")
    print(f"  Emergency Response: {example_block['emergency_response_score']}")
    print(f"  Air Quality: {example_block['air_quality_score']}")
    print(f"  Heat Exposure: {example_block['heat_exposure_score']}")
    print(f"  Traffic Speed: {example_block['traffic_speed_score']}")
    print(f"\nComposite Risk Index: {example_block['composite_risk_index']}")
    print(f"Risk Category: {example_block['risk_category'].upper()}")
