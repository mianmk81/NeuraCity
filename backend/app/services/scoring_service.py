"""Scoring service for calculating severity, urgency, and priority."""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def calculate_severity(issue_type: str, description: Optional[str] = None) -> float:
    """
    Calculate severity score (0-1) based on issue type and description.
    
    Returns:
        float: Severity score between 0 and 1
    """
    base_severity = {
        "accident": 0.9,
        "pothole": 0.5,
        "traffic_light": 0.7,
        "other": 0.3
    }
    
    severity = base_severity.get(issue_type, 0.3)
    
    if description:
        desc_lower = description.lower()
        if any(word in desc_lower for word in ["severe", "major", "dangerous", "urgent", "critical"]):
            severity = min(1.0, severity + 0.1)
        if any(word in desc_lower for word in ["injury", "injured", "hurt", "bleeding"]):
            severity = min(1.0, severity + 0.15)
        if any(word in desc_lower for word in ["blocked", "impassable"]):
            severity = min(1.0, severity + 0.1)
    
    return round(severity, 2)


def calculate_urgency(
    issue_type: str,
    traffic_data: Optional[list] = None,
    time_of_day: Optional[datetime] = None
) -> float:
    """
    Calculate urgency score (0-1) based on issue type, traffic, and time.
    
    Returns:
        float: Urgency score between 0 and 1
    """
    base_urgency = {
        "accident": 0.95,
        "pothole": 0.4,
        "traffic_light": 0.75,
        "other": 0.3
    }
    
    urgency = base_urgency.get(issue_type, 0.3)
    
    if time_of_day:
        hour = time_of_day.hour
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            urgency = min(1.0, urgency + 0.1)
    
    if traffic_data and len(traffic_data) > 0:
        avg_congestion = sum(t.get('congestion', 0) for t in traffic_data) / len(traffic_data)
        if avg_congestion > 0.7:
            urgency = min(1.0, urgency + 0.1)
    
    return round(urgency, 2)


def calculate_priority(severity: float, urgency: float) -> str:
    """
    Calculate priority level based on severity and urgency.
    
    Returns:
        str: Priority level (low, medium, high, critical)
    """
    combined = (severity + urgency) / 2
    
    if combined >= 0.8:
        return "critical"
    elif combined >= 0.6:
        return "high"
    elif combined >= 0.4:
        return "medium"
    else:
        return "low"


def determine_action_type(issue_type: str) -> str:
    """
    Determine action type based on issue type.
    
    Returns:
        str: Action type (emergency, work_order, monitor)
    """
    action_map = {
        "accident": "emergency",
        "pothole": "work_order",
        "traffic_light": "work_order",
        "other": "monitor"
    }
    
    return action_map.get(issue_type, "monitor")
