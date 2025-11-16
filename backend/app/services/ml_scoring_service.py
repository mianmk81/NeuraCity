"""
ML-based scoring service using Gemini AI for intelligent scoring.
Replaces hardcoded rules with AI-powered predictions.
"""
import google.generativeai as genai
from app.core.config import get_settings
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize Gemini
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    logger.info("ML Scoring Service (Gemini) initialized")
except Exception as e:
    logger.error(f"Failed to initialize Gemini for ML scoring: {e}")
    model = None


def _extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Safely extract and parse JSON from AI response text.
    Handles nested objects and provides robust error handling.

    Args:
        text: Response text that may contain JSON

    Returns:
        Parsed JSON dict or None if parsing fails
    """
    try:
        # Try to find JSON object using improved regex that handles nesting
        # Use DOTALL flag to match across newlines
        json_match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
        return None
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON from AI response: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error extracting JSON: {e}")
        return None


async def calculate_severity_ml(
    issue_type: str,
    description: Optional[str] = None,
    image_available: bool = True,
    location_context: Optional[str] = None
) -> float:
    """
    Use Gemini AI to calculate severity score based on all available context.
    
    Args:
        issue_type: Type of issue (accident, pothole, etc.)
        description: User description
        image_available: Whether image evidence was provided
        location_context: Optional context about location (e.g., "near school", "highway")
        
    Returns:
        float: Severity score between 0 and 1
    """
    if not model:
        # Fallback to simple rules if AI unavailable
        return _fallback_severity(issue_type)
    
    try:
        prompt = f"""You are an expert city infrastructure analyst. Analyze this issue report and provide a severity score.

Issue Type: {issue_type}
Description: {description or "No description provided"}
Image Evidence: {"Yes" if image_available else "No"}
Location Context: {location_context or "Not specified"}

Provide a severity score from 0.0 to 1.0 where:
- 0.0-0.3: Minor issue, low impact
- 0.3-0.5: Moderate issue, medium impact
- 0.5-0.7: Significant issue, high impact
- 0.7-0.9: Severe issue, very high impact
- 0.9-1.0: Critical issue, immediate danger

Consider:
- Safety risk to people
- Potential for injury
- Impact on traffic/infrastructure
- Urgency of the situation

Respond with ONLY a JSON object in this format:
{{"severity": 0.75, "reasoning": "Brief explanation"}}"""

        response = model.generate_content(prompt)
        text = response.text.strip()

        # Extract JSON from response
        result = _extract_json_from_text(text)
        if result and 'severity' in result:
            severity = float(result.get('severity', 0.5))
            severity = max(0.0, min(1.0, severity))  # Clamp between 0 and 1
            logger.info(f"ML Severity: {severity} - {result.get('reasoning', '')}")
            return round(severity, 2)
        else:
            logger.warning("Could not parse ML severity response, using fallback")
            return _fallback_severity(issue_type)
            
    except Exception as e:
        logger.error(f"Error in ML severity calculation: {e}")
        return _fallback_severity(issue_type)


async def calculate_urgency_ml(
    issue_type: str,
    description: Optional[str] = None,
    severity: float = 0.5,
    traffic_congestion: Optional[float] = None,
    time_of_day: Optional[datetime] = None,
    weather_condition: Optional[str] = None
) -> float:
    """
    Use Gemini AI to calculate urgency score based on contextual factors.
    
    Args:
        issue_type: Type of issue
        description: User description
        severity: Already calculated severity score
        traffic_congestion: Current traffic level (0-1)
        time_of_day: When issue was reported
        weather_condition: Current weather (optional)
        
    Returns:
        float: Urgency score between 0 and 1
    """
    if not model:
        return _fallback_urgency(issue_type, time_of_day)
    
    try:
        hour_str = time_of_day.strftime("%H:%M") if time_of_day else "Unknown"
        is_rush_hour = False
        if time_of_day:
            hour = time_of_day.hour
            is_rush_hour = (7 <= hour <= 9) or (17 <= hour <= 19)
        
        prompt = f"""You are an expert in emergency response prioritization. Calculate the urgency score for this issue.

Issue Type: {issue_type}
Description: {description or "No description"}
Severity Score: {severity}
Time: {hour_str} {"(RUSH HOUR)" if is_rush_hour else ""}
Traffic Congestion: {traffic_congestion if traffic_congestion is not None else "Unknown"}
Weather: {weather_condition or "Normal"}

Provide an urgency score from 0.0 to 1.0 where:
- 0.0-0.3: Can wait days/weeks
- 0.3-0.5: Should be addressed within days
- 0.5-0.7: Should be addressed within hours
- 0.7-0.9: Should be addressed within 1 hour
- 0.9-1.0: Requires immediate response (minutes)

Consider:
- Time sensitivity
- Risk of situation worsening
- Impact on public safety NOW
- Traffic patterns and congestion
- Weather conditions

Respond with ONLY a JSON object:
{{"urgency": 0.85, "reasoning": "Brief explanation"}}"""

        response = model.generate_content(prompt)
        text = response.text.strip()

        result = _extract_json_from_text(text)
        if result and 'urgency' in result:
            urgency = float(result.get('urgency', 0.5))
            urgency = max(0.0, min(1.0, urgency))
            logger.info(f"ML Urgency: {urgency} - {result.get('reasoning', '')}")
            return round(urgency, 2)
        else:
            logger.warning("Could not parse ML urgency response, using fallback")
            return _fallback_urgency(issue_type, time_of_day)
            
    except Exception as e:
        logger.error(f"Error in ML urgency calculation: {e}")
        return _fallback_urgency(issue_type, time_of_day)


async def calculate_priority_ml(
    severity: float, 
    urgency: float,
    issue_type: Optional[str] = None,
    description: Optional[str] = None,
    location_context: Optional[str] = None
) -> str:
    """
    Use Gemini AI to intelligently determine priority level.
    Considers all context, not just numeric thresholds.
    
    Args:
        severity: ML-calculated severity
        urgency: ML-calculated urgency
        issue_type: Type of issue
        description: Issue description
        location_context: Location details
        
    Returns:
        str: Priority level (low, medium, high, critical)
    """
    if not model:
        return _fallback_priority(severity, urgency)
    
    try:
        prompt = f"""You are a city operations priority manager. Determine the priority level for this issue.

Severity Score: {severity} (0-1, where 1 is most severe)
Urgency Score: {urgency} (0-1, where 1 is most urgent)
Issue Type: {issue_type or "Not specified"}
Description: {description or "No description"}
Location: {location_context or "Standard location"}

Classify into ONE priority level:
- "low": Minor issues, can wait weeks/months
- "medium": Moderate issues, address within days
- "high": Significant issues, needs attention within hours
- "critical": Severe/urgent, requires immediate response

Consider:
- Public safety impact
- Potential for situation to worsen
- Number of people affected
- Time sensitivity
- Infrastructure criticality

Respond with ONLY a JSON object:
{{"priority": "high", "reasoning": "Brief explanation"}}"""

        response = model.generate_content(prompt)
        text = response.text.strip()

        result = _extract_json_from_text(text)
        if result and 'priority' in result:
            priority = result.get('priority', 'medium').lower()

            if priority in ['low', 'medium', 'high', 'critical']:
                logger.info(f"ML Priority: {priority} - {result.get('reasoning', '')}")
                return priority
            else:
                logger.warning(f"Invalid priority from ML: {priority}, using fallback")
                return _fallback_priority(severity, urgency)
        else:
            return _fallback_priority(severity, urgency)
            
    except Exception as e:
        logger.error(f"Error in ML priority calculation: {e}")
        return _fallback_priority(severity, urgency)


async def determine_action_type_ml(
    issue_type: str,
    description: Optional[str] = None,
    severity: float = 0.5,
    urgency: float = 0.5
) -> str:
    """
    Use Gemini AI to determine what action should be taken.
    Automatically marks accidents as emergency.
    
    Args:
        issue_type: Type of issue
        description: User description
        severity: ML-calculated severity
        urgency: ML-calculated urgency
        
    Returns:
        str: Action type (emergency, work_order, monitor)
    """
    # Automatically mark accidents as emergency
    issue_type_lower = issue_type.lower()
    if 'accident' in issue_type_lower or 'crash' in issue_type_lower or 'collision' in issue_type_lower:
        logger.info(f"Accident detected ({issue_type}), automatically setting action_type to emergency")
        return "emergency"
    
    if not model:
        return _fallback_action_type(issue_type)
    
    try:
        prompt = f"""You are a city operations AI assistant. Determine what action should be taken for this issue.

Issue Type: {issue_type}
Description: {description or "No description"}
Severity: {severity} (0-1 scale)
Urgency: {urgency} (0-1 scale)

IMPORTANT: If this is an accident, crash, or collision, it MUST be classified as "emergency".

Choose ONE action type:
- "emergency": Requires immediate emergency response (accidents, injuries, immediate danger, life-threatening situations)
- "work_order": Requires scheduled repair/maintenance (potholes, broken equipment, non-urgent repairs)
- "monitor": Track for now, may need future action (minor issues, complaints, non-critical)

Consider:
- Is there immediate danger to life or safety? → emergency
- Is it an accident or crash? → emergency
- Does it require physical repair work? → work_order
- Is it reportable but not actionable yet? → monitor

Respond with ONLY a JSON object:
{{"action_type": "emergency", "reasoning": "Brief explanation"}}"""

        response = model.generate_content(prompt)
        text = response.text.strip()

        result = _extract_json_from_text(text)
        if result and 'action_type' in result:
            action_type = result.get('action_type', 'monitor').lower()

            # Double-check for accidents
            if 'accident' in issue_type_lower or 'crash' in issue_type_lower:
                action_type = 'emergency'

            # Validate
            if action_type in ['emergency', 'work_order', 'monitor']:
                logger.info(f"ML Action: {action_type} - {result.get('reasoning', '')}")
                return action_type
            else:
                logger.warning(f"Invalid action type from ML: {action_type}, using fallback")
                return _fallback_action_type(issue_type)
        else:
            return _fallback_action_type(issue_type)
            
    except Exception as e:
        logger.error(f"Error in ML action type determination: {e}")
        # Fallback: check if accident
        if 'accident' in issue_type_lower:
            return 'emergency'
        return _fallback_action_type(issue_type)


# Fallback functions (original hardcoded logic)
def _fallback_severity(issue_type: str) -> float:
    """Fallback to rule-based severity if ML fails."""
    base_severity = {
        "accident": 0.9,
        "pothole": 0.5,
        "traffic_light": 0.7,
        "other": 0.3
    }
    return base_severity.get(issue_type, 0.3)


def _fallback_urgency(issue_type: str, time_of_day: Optional[datetime] = None) -> float:
    """Fallback to rule-based urgency if ML fails."""
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
    
    return round(urgency, 2)


def _fallback_action_type(issue_type: str) -> str:
    """Fallback to rule-based action type if ML fails."""
    action_map = {
        "accident": "emergency",
        "pothole": "work_order",
        "traffic_light": "work_order",
        "other": "monitor"
    }
    return action_map.get(issue_type, "monitor")


def _fallback_priority(severity: float, urgency: float) -> str:
    """Fallback to threshold-based priority if ML fails."""
    weighted_score = (severity * 0.4) + (urgency * 0.6)
    
    if weighted_score >= 0.85:
        return "critical"
    elif weighted_score >= 0.65:
        return "high"
    elif weighted_score >= 0.40:
        return "medium"
    else:
        return "low"


