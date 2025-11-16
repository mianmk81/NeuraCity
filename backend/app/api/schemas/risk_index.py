"""Pydantic schemas for Risk Index API."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# =====================================================
# RISK BLOCK SCHEMAS
# =====================================================

class RiskBlockBase(BaseModel):
    """Base schema for risk blocks."""
    block_id: str = Field(..., description="Unique block identifier")
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")


class RiskBlockCreate(RiskBlockBase):
    """Schema for creating a new risk block."""
    crime_score: float = Field(0.0, ge=0.0, le=1.0, description="Crime risk score (0-1)")
    blight_score: float = Field(0.0, ge=0.0, le=1.0, description="Blight risk score (0-1)")
    emergency_response_score: float = Field(0.0, ge=0.0, le=1.0, description="Emergency response risk score (0-1)")
    air_quality_score: float = Field(0.0, ge=0.0, le=1.0, description="Air quality risk score (0-1)")
    heat_exposure_score: float = Field(0.0, ge=0.0, le=1.0, description="Heat exposure risk score (0-1)")
    traffic_speed_score: float = Field(0.0, ge=0.0, le=1.0, description="Traffic speed risk score (0-1)")
    composite_risk_index: float = Field(0.0, ge=0.0, le=1.0, description="Composite risk index (0-1)")
    risk_category: str = Field("low", description="Risk category (low, moderate, high, critical)")


class RiskBlockUpdate(BaseModel):
    """Schema for updating a risk block."""
    crime_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    blight_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    emergency_response_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    air_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    heat_exposure_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    traffic_speed_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    composite_risk_index: Optional[float] = Field(None, ge=0.0, le=1.0)
    risk_category: Optional[str] = Field(None, description="Risk category")


class RiskBlockResponse(RiskBlockBase):
    """Schema for risk block responses."""
    id: Optional[str] = Field(None, description="Database UUID")
    crime_score: float = Field(..., description="Crime risk score (0-1)")
    blight_score: float = Field(..., description="Blight risk score (0-1)")
    emergency_response_score: float = Field(..., description="Emergency response risk score (0-1)")
    air_quality_score: float = Field(..., description="Air quality risk score (0-1)")
    heat_exposure_score: float = Field(..., description="Heat exposure risk score (0-1)")
    traffic_speed_score: float = Field(..., description="Traffic speed risk score (0-1)")
    composite_risk_index: float = Field(..., description="Composite risk index (0-1)")
    risk_category: str = Field(..., description="Risk category")
    last_calculated_at: Optional[str] = Field(None, description="Last calculation timestamp")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Update timestamp")

    class Config:
        from_attributes = True


# =====================================================
# RISK FACTOR SCHEMAS
# =====================================================

class RiskFactorCreate(BaseModel):
    """Schema for creating a risk factor measurement."""
    block_id: str = Field(..., description="Block identifier")
    factor_type: str = Field(..., description="Factor type (crime, blight, emergency_response, etc.)")
    raw_value: float = Field(..., description="Raw measurement value")
    raw_unit: Optional[str] = Field(None, description="Unit of measurement")
    normalized_score: float = Field(..., ge=0.0, le=1.0, description="Normalized score (0-1)")
    data_source: str = Field("synthetic", description="Data source")


class RiskFactorResponse(BaseModel):
    """Schema for risk factor responses."""
    id: str = Field(..., description="Database UUID")
    block_id: str = Field(..., description="Block identifier")
    factor_type: str = Field(..., description="Factor type")
    raw_value: float = Field(..., description="Raw measurement value")
    raw_unit: Optional[str] = Field(None, description="Unit of measurement")
    normalized_score: float = Field(..., description="Normalized score (0-1)")
    data_source: str = Field(..., description="Data source")
    measurement_date: str = Field(..., description="Measurement timestamp")
    created_at: Optional[str] = Field(None, description="Creation timestamp")

    class Config:
        from_attributes = True


# =====================================================
# RISK HISTORY SCHEMAS
# =====================================================

class RiskHistoryResponse(BaseModel):
    """Schema for risk history responses."""
    id: str = Field(..., description="Database UUID")
    block_id: str = Field(..., description="Block identifier")
    composite_risk_index: float = Field(..., description="Composite risk index at snapshot")
    risk_category: str = Field(..., description="Risk category at snapshot")
    crime_score: Optional[float] = Field(None, description="Crime score at snapshot")
    blight_score: Optional[float] = Field(None, description="Blight score at snapshot")
    emergency_response_score: Optional[float] = Field(None, description="Emergency response score at snapshot")
    air_quality_score: Optional[float] = Field(None, description="Air quality score at snapshot")
    heat_exposure_score: Optional[float] = Field(None, description="Heat exposure score at snapshot")
    traffic_speed_score: Optional[float] = Field(None, description="Traffic speed score at snapshot")
    snapshot_date: str = Field(..., description="Snapshot timestamp")

    class Config:
        from_attributes = True


# =====================================================
# RISK CONFIG SCHEMAS
# =====================================================

class RiskConfigResponse(BaseModel):
    """Schema for risk configuration responses."""
    id: str = Field(..., description="Database UUID")
    config_name: str = Field(..., description="Configuration name")

    # Weights
    crime_weight: float = Field(..., description="Crime factor weight")
    blight_weight: float = Field(..., description="Blight factor weight")
    emergency_response_weight: float = Field(..., description="Emergency response factor weight")
    air_quality_weight: float = Field(..., description="Air quality factor weight")
    heat_exposure_weight: float = Field(..., description="Heat exposure factor weight")
    traffic_speed_weight: float = Field(..., description="Traffic speed factor weight")

    # Normalization thresholds
    crime_max_incidents: int = Field(..., description="Max crime incidents for normalization")
    blight_max_properties: int = Field(..., description="Max blight properties for normalization")
    emergency_max_minutes: int = Field(..., description="Max emergency response minutes")
    air_quality_max_aqi: int = Field(..., description="Max AQI value")
    heat_exposure_max_celsius: float = Field(..., description="Max temperature in Celsius")
    traffic_speed_max_mph: int = Field(..., description="Max traffic speed in mph")

    # Spatial parameters
    spatial_radius_meters: float = Field(..., description="Spatial influence radius")
    spatial_decay_factor: float = Field(..., description="Spatial decay factor (0-1)")

    is_active: bool = Field(..., description="Whether config is active")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Update timestamp")

    class Config:
        from_attributes = True


# =====================================================
# RECALCULATION SCHEMAS
# =====================================================

class CrimeData(BaseModel):
    """Crime data for recalculation."""
    incidents_per_month: int = Field(0, ge=0, description="Crime incidents per month")
    severity_multiplier: float = Field(1.0, ge=0.0, description="Severity multiplier (1.0=normal, 1.5=violent)")


class BlightData(BaseModel):
    """Blight data for recalculation."""
    abandoned_buildings: int = Field(0, ge=0, description="Number of abandoned buildings")
    vacant_lots: int = Field(0, ge=0, description="Number of vacant lots")
    code_violations: int = Field(0, ge=0, description="Number of code violations")


class EmergencyData(BaseModel):
    """Emergency response data for recalculation."""
    avg_response_time_minutes: float = Field(0.0, ge=0.0, description="Average response time in minutes")
    percentile_90_time_minutes: float = Field(0.0, ge=0.0, description="90th percentile response time")


class AirQualityData(BaseModel):
    """Air quality data for recalculation."""
    aqi_value: int = Field(0, ge=0, le=500, description="Air Quality Index (0-500)")
    pm25_concentration: Optional[float] = Field(None, ge=0.0, description="PM2.5 concentration in µg/m³")


class HeatData(BaseModel):
    """Heat exposure data for recalculation."""
    avg_temperature_celsius: float = Field(20.0, description="Average temperature in Celsius")
    max_temperature_celsius: float = Field(25.0, description="Maximum temperature in Celsius")
    tree_canopy_percent: float = Field(30.0, ge=0.0, le=100.0, description="Tree canopy coverage (%)")
    impervious_surface_percent: float = Field(50.0, ge=0.0, le=100.0, description="Impervious surface coverage (%)")


class TrafficData(BaseModel):
    """Traffic speed data for recalculation."""
    avg_speed_mph: float = Field(25.0, ge=0.0, description="Average speed in mph")
    percentile_85_speed_mph: float = Field(30.0, ge=0.0, description="85th percentile speed in mph")
    pedestrian_volume: int = Field(50, ge=0, description="Daily pedestrian count")
    road_type: str = Field("residential", description="Road type (residential, arterial, highway)")


class RecalculateRiskRequest(BaseModel):
    """Request schema for recalculating risk for a block."""
    block_id: str = Field(..., description="Block identifier")
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")

    # Raw data for each factor
    crime_data: Optional[CrimeData] = None
    blight_data: Optional[BlightData] = None
    emergency_data: Optional[EmergencyData] = None
    air_quality_data: Optional[AirQualityData] = None
    heat_data: Optional[HeatData] = None
    traffic_data: Optional[TrafficData] = None

    # Calculation options
    config_name: Optional[str] = Field("default", description="Configuration to use")
    apply_spatial_smoothing: bool = Field(False, description="Apply spatial smoothing")
    save_to_database: bool = Field(True, description="Save results to database")


class RecalculateRiskResponse(BaseModel):
    """Response schema for risk recalculation."""
    block_id: str = Field(..., description="Block identifier")
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")

    # Individual factor scores
    crime_score: float = Field(..., description="Crime risk score (0-1)")
    blight_score: float = Field(..., description="Blight risk score (0-1)")
    emergency_response_score: float = Field(..., description="Emergency response risk score (0-1)")
    air_quality_score: float = Field(..., description="Air quality risk score (0-1)")
    heat_exposure_score: float = Field(..., description="Heat exposure risk score (0-1)")
    traffic_speed_score: float = Field(..., description="Traffic speed risk score (0-1)")

    # Composite results
    composite_risk_index: float = Field(..., description="Composite risk index (0-1)")
    risk_category: str = Field(..., description="Risk category")
    last_calculated_at: Optional[datetime] = Field(None, description="Calculation timestamp")

    class Config:
        from_attributes = True
