"""Gemini AI service for emergency summaries and work order suggestions."""
import google.generativeai as genai
from app.core.config import get_settings
import logging
from typing import Dict, Any, Optional, List
import time
from PIL import Image
import os

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize Gemini
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    # Use same model for vision tasks (gemini-pro supports vision)
    vision_model = genai.GenerativeModel(settings.GEMINI_MODEL)
    logger.info("Gemini API initialized")
except Exception as e:
    logger.error(f"Failed to initialize Gemini: {e}")
    model = None
    vision_model = None


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


async def analyze_issue_image(image_path: str, issue_type: str, description: str = "") -> Dict[str, Any]:
    """
    Analyze issue image using Gemini Vision to determine materials and severity.
    
    Args:
        image_path: Path to the image file
        issue_type: Type of issue (pothole, accident, etc.)
        description: Optional description
        
    Returns:
        dict: {'materials': List[str], 'specialty': str, 'notes': str, 'severity_assessment': str}
    """
    if not vision_model:
        return {
            "materials": ["Standard repair materials"],
            "specialty": "general_contractor",
            "notes": "Vision AI unavailable",
            "severity_assessment": "Unable to assess"
        }
    
    try:
        # Load and open image
        if not os.path.exists(image_path):
            logger.warning(f"Image not found: {image_path}")
            return await generate_work_order_suggestion({"issue_type": issue_type, "description": description})
        
        img = Image.open(image_path)
        
        prompt = f"""You are an infrastructure damage assessment expert. Analyze this image of a {issue_type}.

Description: {description or 'No description provided'}

Please provide a detailed assessment:

1. **MATERIALS NEEDED**: List specific materials and quantities for repair (be precise, e.g., "50 lbs cold patch asphalt", "2 bags Portland cement")

2. **CONTRACTOR SPECIALTY**: Choose ONE from: pothole_repair, electrical, traffic_signal, general_contractor

3. **SEVERITY**: Rate as: minor, moderate, severe, critical

4. **REPAIR NOTES**: Specific instructions for the contractor (2-3 sentences)

5. **SAFETY CONCERNS**: Any immediate safety hazards

Format your response EXACTLY as:
MATERIALS: [item1, item2, item3]
SPECIALTY: [specialty]
SEVERITY: [severity]
NOTES: [detailed notes]
SAFETY: [safety concerns or "None"]
"""

        response = vision_model.generate_content([prompt, img])
        text = response.text.strip()
        
        # Parse response
        materials = ["Standard repair materials"]
        specialty = "general_contractor"
        severity = "moderate"
        notes = "See issue details"
        safety = "None"
        
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('MATERIALS:'):
                materials_str = line.replace('MATERIALS:', '').strip()
                # Parse materials list
                materials = [m.strip() for m in materials_str.strip('[]').split(',') if m.strip()]
                if not materials:
                    materials = ["Standard materials"]
            elif line.startswith('SPECIALTY:'):
                specialty = line.replace('SPECIALTY:', '').strip().lower()
            elif line.startswith('SEVERITY:'):
                severity = line.replace('SEVERITY:', '').strip().lower()
            elif line.startswith('NOTES:'):
                notes = line.replace('NOTES:', '').strip()
            elif line.startswith('SAFETY:'):
                safety = line.replace('SAFETY:', '').strip()
        
        if specialty not in ['pothole_repair', 'electrical', 'traffic_signal', 'general_contractor']:
            specialty = 'general_contractor'
        
        if severity not in ['minor', 'moderate', 'severe', 'critical']:
            severity = 'moderate'
        
        logger.info(f"Analyzed image for {issue_type}: {severity} severity, {len(materials)} materials")
        return {
            "materials": materials,
            "specialty": specialty,
            "notes": notes,
            "severity_assessment": severity,
            "safety_concerns": safety
        }
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return await generate_work_order_suggestion({"issue_type": issue_type, "description": description})


async def generate_work_order_suggestion(issue: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate work order suggestions including materials and contractor specialty.
    Uses contextual questions based on issue type and description.
    
    Args:
        issue: Issue dict with type, description
        
    Returns:
        dict: {'materials': List[str], 'specialty': str, 'notes': str}
    """
    if not model:
        return {
            "materials": ["Standard repair materials"],
            "specialty": "general_contractor",
            "notes": "AI service unavailable"
        }
    
    try:
        issue_type = issue.get('issue_type', 'unknown').lower()
        description = issue.get('description', '')
        
        # Build contextual questions based on issue type
        contextual_questions = []
        
        if issue_type == 'pothole' or 'pothole' in issue_type:
            contextual_questions = [
                "What is the approximate size/diameter of the pothole?",
                "Is it on a main road or side street?",
                "Are there any exposed rebar or deep cracks?",
                "What is the surrounding road condition?"
            ]
        elif issue_type == 'traffic_light' or 'traffic_light' in issue_type or 'signal' in issue_type:
            contextual_questions = [
                "Is the light completely out or flashing?",
                "Which direction(s) are affected?",
                "Is it a single light or multiple lights?",
                "Are there any visible wiring issues?"
            ]
        elif issue_type == 'accident' or 'accident' in issue_type:
            contextual_questions = [
                "Are there any injuries?",
                "Is there vehicle damage blocking traffic?",
                "Are emergency services already on scene?",
                "What is the extent of property damage?"
            ]
        else:
            contextual_questions = [
                "What is the specific nature of the issue?",
                "What is the extent of the damage?",
                "Are there any safety concerns?",
                "What materials or expertise might be needed?"
            ]
        
        # Build enhanced prompt with contextual questions
        questions_text = "\n".join([f"- {q}" for q in contextual_questions])
        
        prompt = f"""You are an infrastructure repair expert. Analyze this issue and provide detailed work order information.

Issue Type: {issue_type}
Description: {description or 'No additional description provided'}

Based on the issue type, consider these questions:
{questions_text}

Please provide:
1. **MATERIALS NEEDED**: List specific materials with quantities (e.g., "50 lbs cold patch asphalt", "2 traffic signal bulbs", "10 sq ft concrete")
2. **CONTRACTOR SPECIALTY**: Choose ONE from: pothole_repair, electrical, traffic_signal, general_contractor
3. **REPAIR NOTES**: Detailed instructions for the contractor (2-3 sentences with specific steps)

Format your response EXACTLY as:
MATERIALS: [item1, item2, item3]
SPECIALTY: [specialty]
NOTES: [detailed notes]"""

        response = model.generate_content(prompt)
        text = response.text.strip()
        
        materials = ["Standard materials"]
        specialty = "general_contractor"
        notes = "See issue details"
        
        # Enhanced parsing with better error handling
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('MATERIALS:'):
                materials_str = line.replace('MATERIALS:', '').strip()
                # Handle both [item1, item2] and item1, item2 formats
                if materials_str.startswith('[') and materials_str.endswith(']'):
                    materials_str = materials_str[1:-1]
                materials = [m.strip().strip('"').strip("'") for m in materials_str.split(',') if m.strip()]
                if not materials:
                    materials = [f"Materials for {issue_type} repair"]
            elif line.startswith('SPECIALTY:'):
                specialty = line.replace('SPECIALTY:', '').strip().lower()
            elif line.startswith('NOTES:'):
                notes = line.replace('NOTES:', '').strip()
        
        # Validate specialty
        if specialty not in ['pothole_repair', 'electrical', 'traffic_signal', 'general_contractor']:
            # Auto-detect based on issue type
            if 'pothole' in issue_type:
                specialty = 'pothole_repair'
            elif 'traffic' in issue_type or 'signal' in issue_type or 'light' in issue_type:
                specialty = 'traffic_signal'
            elif 'electrical' in issue_type or 'power' in issue_type:
                specialty = 'electrical'
            else:
                specialty = 'general_contractor'
        
        # Ensure materials list is not empty
        if not materials or materials == ["Standard materials"]:
            if issue_type == 'pothole' or 'pothole' in issue_type:
                materials = ["Cold patch asphalt (50-100 lbs)", "Road base material", "Compaction equipment"]
            elif issue_type == 'traffic_light' or 'traffic_light' in issue_type:
                materials = ["Traffic signal bulbs", "Electrical wiring", "Signal controller components"]
            else:
                materials = [f"Materials for {issue_type} repair"]
        
        logger.info(f"Generated work order suggestion for {issue_type}: {len(materials)} materials, {specialty} specialty")
        return {"materials": materials, "specialty": specialty, "notes": notes}
    except Exception as e:
        logger.error(f"Error generating work order: {e}", exc_info=True)
        # Better fallback based on issue type
        issue_type = issue.get('issue_type', 'unknown').lower()
        if 'pothole' in issue_type:
            materials = ["Cold patch asphalt", "Road base material"]
            specialty = "pothole_repair"
        elif 'traffic' in issue_type or 'signal' in issue_type or 'light' in issue_type:
            materials = ["Traffic signal bulbs", "Electrical components"]
            specialty = "traffic_signal"
        elif 'electrical' in issue_type:
            materials = ["Electrical wiring", "Circuit components"]
            specialty = "electrical"
        else:
            materials = [f"Materials for {issue_type} repair"]
            specialty = "general_contractor"
        
        return {
            "materials": materials,
            "specialty": specialty,
            "notes": f"Standard repair for {issue_type}. Please review issue details for specific requirements."
        }


async def get_available_contractors(specialty: str = None) -> List[Dict[str, Any]]:
    """
    Get list of available contractors, optionally filtered by specialty.
    This is a placeholder - in production, this would query a database.
    """
    contractors = [
        {"id": "1", "name": "Atlanta Paving Solutions", "specialty": "pothole_repair", "rating": 4.8},
        {"id": "2", "name": "QuickFix Roads Inc.", "specialty": "pothole_repair", "rating": 4.5},
        {"id": "3", "name": "Metro Electrical Services", "specialty": "electrical", "rating": 4.7},
        {"id": "4", "name": "Signal Tech Experts", "specialty": "traffic_signal", "rating": 4.9},
        {"id": "5", "name": "City Wide Contractors", "specialty": "general_contractor", "rating": 4.3},
    ]
    
    if specialty:
        return [c for c in contractors if c["specialty"] == specialty]
    return contractors
