"""Gemini AI service for emergency summaries and work order suggestions."""
import google.generativeai as genai
from app.core.config import get_settings
import logging
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize Gemini
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    logger.info("Gemini API initialized")
except Exception as e:
    logger.error(f"Failed to initialize Gemini: {e}")
    model = None


async def generate_emergency_summary(issue: Dict[str, Any]) -> str:
    """
    Generate dispatcher-ready emergency summary for accidents.
    
    Args:
        issue: Issue dict with type, location, description
        
    Returns:
        str: Emergency summary
    """
    if not model:
        return "Emergency summary unavailable - AI service not configured."
    
    try:
        prompt = f"""Generate a brief, dispatcher-ready emergency summary for the following accident report:

Location: {issue.get('lat', 'unknown')}, {issue.get('lng', 'unknown')}
Type: {issue.get('issue_type', 'accident')}
Description: {issue.get('description', 'No description provided')}

Provide a concise summary (2-3 sentences) that includes:
1. What happened
2. Severity assessment
3. Recommended emergency response

Keep it professional and actionable for emergency dispatchers."""

        response = model.generate_content(prompt)
        summary = response.text.strip()
        logger.info("Generated emergency summary")
        return summary
    except Exception as e:
        logger.error(f"Error generating emergency summary: {e}")
        return f"Error generating summary. Issue type: {issue.get('issue_type')}. Location: ({issue.get('lat')}, {issue.get('lng')})"


async def generate_work_order_suggestion(issue: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate work order suggestions including materials and contractor specialty.
    
    Args:
        issue: Issue dict with type, description
        
    Returns:
        dict: {'materials': str, 'specialty': str, 'notes': str}
    """
    if not model:
        return {
            "materials": "Standard repair materials",
            "specialty": "general_contractor",
            "notes": "AI service unavailable"
        }
    
    try:
        prompt = f"""Generate work order details for the following infrastructure issue:

Issue Type: {issue.get('issue_type', 'unknown')}
Description: {issue.get('description', 'No description')}

Provide:
1. Required materials (comma-separated list)
2. Required contractor specialty (one of: pothole_repair, electrical, traffic_signal, general_contractor)
3. Brief notes for the contractor (1 sentence)

Format your response as:
MATERIALS: [list]
SPECIALTY: [specialty]
NOTES: [notes]"""

        response = model.generate_content(prompt)
        text = response.text.strip()
        
        materials = "Standard materials"
        specialty = "general_contractor"
        notes = "See issue details"
        
        for line in text.split('\n'):
            if line.startswith('MATERIALS:'):
                materials = line.replace('MATERIALS:', '').strip()
            elif line.startswith('SPECIALTY:'):
                specialty = line.replace('SPECIALTY:', '').strip().lower()
            elif line.startswith('NOTES:'):
                notes = line.replace('NOTES:', '').strip()
        
        if specialty not in ['pothole_repair', 'electrical', 'traffic_signal', 'general_contractor']:
            specialty = 'general_contractor'
        
        logger.info(f"Generated work order suggestion for {issue.get('issue_type')}")
        return {"materials": materials, "specialty": specialty, "notes": notes}
    except Exception as e:
        logger.error(f"Error generating work order: {e}")
        return {
            "materials": f"Materials for {issue.get('issue_type')} repair",
            "specialty": "general_contractor",
            "notes": "Error generating suggestions"
        }
