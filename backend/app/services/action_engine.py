"""Action engine for processing new issues and triggering AI actions."""
from app.services.supabase_service import SupabaseService
from app.services.gemini_service import generate_emergency_summary, generate_work_order_suggestion
from app.core.database import get_supabase_client
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


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
        suggestions = await generate_work_order_suggestion(issue_data)
        
        specialty = suggestions.get('specialty', 'general_contractor')
        contractors = await db_service.get_contractors(specialty=specialty)
        
        contractor_id = None
        if contractors:
            contractor_id = contractors[0]['id']
            logger.info(f"Selected contractor: {contractors[0].get('name')}")
        else:
            all_contractors = await db_service.get_contractors()
            if all_contractors:
                contractor_id = all_contractors[0]['id']
                logger.warning(f"No specialist found, using first available contractor")
        
        material_suggestion = f"{suggestions.get('materials', 'Standard materials')}. {suggestions.get('notes', '')}"
        
        work_order_data = {
            "issue_id": issue_id,
            "contractor_id": contractor_id,
            "material_suggestion": material_suggestion,
            "status": "pending_review"
        }
        
        await db_service.create_work_order(work_order_data)
        logger.info(f"Created work order for issue {issue_id}")
    except Exception as e:
        logger.error(f"Error creating work order: {e}")
        raise
