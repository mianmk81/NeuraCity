"""Action engine for processing new issues and triggering AI actions."""
from app.services.supabase_service import SupabaseService
from app.services.gemini_service import generate_emergency_summary, generate_work_order_suggestion, analyze_issue_image
from app.core.database import get_supabase_client
from app.core.config import get_settings
import logging
from typing import Dict, Any
import os

logger = logging.getLogger(__name__)
settings = get_settings()


async def process_new_issue(issue_id: str, issue_data: Dict[str, Any]):
    """
    Process a newly created issue and trigger appropriate AI actions.
    
    Args:
        issue_id: UUID of the issue
        issue_data: Complete issue data
    """
    action_type = issue_data.get('action_type')
    issue_type = issue_data.get('issue_type')
    
    logger.info(f"Processing issue {issue_id} with action type: {action_type}")
    
    try:
        client = get_supabase_client()
        db_service = SupabaseService(client)
        
        if action_type == "emergency":
            await create_emergency_entry(db_service, issue_id, issue_data)
        elif action_type == "work_order":
            await create_work_order_entry(db_service, issue_id, issue_data)
        else:
            logger.info(f"Issue {issue_id} set to monitor mode, no action needed")
    
    except Exception as e:
        logger.error(f"Error processing issue {issue_id}: {e}")
        raise


async def create_emergency_entry(db_service: SupabaseService, issue_id: str, issue_data: Dict[str, Any]):
    """Create emergency queue entry with AI-generated summary."""
    try:
        summary = await generate_emergency_summary(issue_data)
        
        emergency_data = {
            "issue_id": issue_id,
            "summary": summary,
            "status": "pending"
        }
        
        await db_service.create_emergency_entry(emergency_data)
        logger.info(f"Created emergency entry for issue {issue_id}")
    except Exception as e:
        logger.error(f"Error creating emergency entry: {e}")
        raise


async def create_work_order_entry(db_service: SupabaseService, issue_id: str, issue_data: Dict[str, Any]):
    """Create work order with AI-suggested materials and contractor."""
    try:
        # Try vision analysis if image is available
        image_url = issue_data.get('image_url')
        if image_url:
            # Convert relative URL to absolute path
            image_path = image_url if os.path.isabs(image_url) else os.path.join(settings.UPLOAD_DIR, os.path.basename(image_url))
            if os.path.exists(image_path):
                logger.info(f"Analyzing image with Gemini Vision: {image_path}")
                suggestions = await analyze_issue_image(
                    image_path=image_path,
                    issue_type=issue_data.get('issue_type', 'unknown'),
                    description=issue_data.get('description', '')
                )
            else:
                logger.warning(f"Image path not found: {image_path}, falling back to text-based analysis")
                suggestions = await generate_work_order_suggestion(issue_data)
        else:
            logger.info("No image available, using text-based analysis")
            suggestions = await generate_work_order_suggestion(issue_data)
        
        specialty = suggestions.get('specialty', 'general_contractor')
        contractors = await db_service.get_contractors(specialty=specialty)
        
        # Leave contractor_id as None initially for manual selection
        contractor_id = None
        logger.info(f"Work order requires specialty: {specialty}")
        
        # Format materials as a list if it's already a list, otherwise convert
        materials = suggestions.get('materials', ['Standard materials'])
        if isinstance(materials, str):
            materials = [materials]
        
        # Create comprehensive material suggestion string
        material_lines = []
        material_lines.append("**MATERIALS NEEDED:**")
        for i, material in enumerate(materials, 1):
            material_lines.append(f"{i}. {material}")
        
        if suggestions.get('severity_assessment'):
            material_lines.append(f"\n**SEVERITY:** {suggestions['severity_assessment'].upper()}")
        
        if suggestions.get('safety_concerns'):
            material_lines.append(f"\n**SAFETY:** {suggestions['safety_concerns']}")
        
        material_lines.append(f"\n**NOTES:** {suggestions.get('notes', 'See issue details')}")
        
        material_suggestion = "\n".join(material_lines)
        
        work_order_data = {
            "issue_id": issue_id,
            "contractor_id": contractor_id,  # None for manual selection
            "material_suggestion": material_suggestion,
            "status": "pending_review"
        }
        
        await db_service.create_work_order(work_order_data)
        logger.info(f"Created work order for issue {issue_id} (contractor to be assigned)")
    except Exception as e:
        logger.error(f"Error creating work order: {e}")
        raise
