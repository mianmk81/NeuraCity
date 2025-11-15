"""API endpoints for issues management."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
from supabase import Client
from datetime import datetime

from app.api.schemas.issue import IssueResponse, IssueUpdate, IssueStatus
from app.core.dependencies import get_db
from app.services.supabase_service import SupabaseService
from app.services.image_service import validate_image, save_image, delete_image
from app.services.scoring_service import (
    calculate_severity,
    calculate_urgency,
    calculate_priority,
    determine_action_type
)
from app.services.action_engine import process_new_issue
from app.utils.validators import validate_gps_coordinates
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/issues", tags=["issues"])


@router.post("", response_model=IssueResponse, status_code=201)
async def create_issue(
    lat: float = Form(..., description="Latitude"),
    lng: float = Form(..., description="Longitude"),
    issue_type: str = Form(..., description="Type of issue"),
    description: Optional[str] = Form(None, description="Issue description"),
    image: UploadFile = File(..., description="Image evidence"),
    db: Client = Depends(get_db)
):
    """
    Create a new issue with image upload and automatic GPS location.
    
    Requires:
    - image: Image file (JPEG, PNG, WebP)
    - lat/lng: GPS coordinates
    - issue_type: accident, pothole, traffic_light, or other
    - description: Optional (required if issue_type is 'other')
    """
    try:
        validate_gps_coordinates(lat, lng)
        
        if issue_type == "other" and (not description or not description.strip()):
            raise HTTPException(
                status_code=400,
                detail="Description is required when issue_type is 'other'"
            )
        
        await validate_image(image)
        filename = await save_image(image)
        image_url = f"uploads/{filename}"
        
        db_service = SupabaseService(db)
        traffic_segments = await db_service.get_traffic_segments()
        
        severity = calculate_severity(issue_type, description)
        urgency = calculate_urgency(issue_type, traffic_segments, datetime.utcnow())
        priority = calculate_priority(severity, urgency)
        action_type = determine_action_type(issue_type)
        
        issue_data = {
            "lat": lat,
            "lng": lng,
            "issue_type": issue_type,
            "description": description,
            "image_url": image_url,
            "severity": severity,
            "urgency": urgency,
            "priority": priority,
            "action_type": action_type,
            "status": "open"
        }
        
        created_issue = await db_service.create_issue(issue_data)
        
        try:
            await process_new_issue(created_issue['id'], created_issue)
        except Exception as e:
            logger.error(f"Error in action engine: {e}")
        
        logger.info(f"Created issue {created_issue['id']} with priority {priority}")
        return created_issue
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating issue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[IssueResponse])
async def get_issues(
    issue_type: Optional[str] = None,
    status: Optional[str] = None,
    min_severity: Optional[float] = None,
    max_severity: Optional[float] = None,
    limit: int = 100,
    db: Client = Depends(get_db)
):
    """
    Get list of issues with optional filters.
    
    Query parameters:
    - issue_type: Filter by type (accident, pothole, traffic_light, other)
    - status: Filter by status (open, in_progress, resolved, closed)
    - min_severity: Minimum severity (0-1)
    - max_severity: Maximum severity (0-1)
    - limit: Maximum number of results (default 100)
    """
    try:
        db_service = SupabaseService(db)
        issues = await db_service.get_issues(
            issue_type=issue_type,
            status=status,
            min_severity=min_severity,
            max_severity=max_severity,
            limit=min(limit, 1000)
        )
        return issues
    except Exception as e:
        logger.error(f"Error fetching issues: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(
    issue_id: str,
    db: Client = Depends(get_db)
):
    """Get a single issue by ID."""
    try:
        db_service = SupabaseService(db)
        issue = await db_service.get_issue_by_id(issue_id)
        
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        return issue
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching issue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: str,
    update_data: IssueUpdate,
    db: Client = Depends(get_db)
):
    """Update an existing issue."""
    try:
        db_service = SupabaseService(db)
        
        existing = await db_service.get_issue_by_id(issue_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        update_dict = update_data.model_dump(exclude_unset=True)
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        updated = await db_service.update_issue(issue_id, update_dict)
        logger.info(f"Updated issue {issue_id}")
        return updated
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating issue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{issue_id}", status_code=204)
async def delete_issue_endpoint(
    issue_id: str,
    db: Client = Depends(get_db)
):
    """Delete an issue."""
    try:
        db_service = SupabaseService(db)
        
        issue = await db_service.get_issue_by_id(issue_id)
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        if issue.get('image_url'):
            filename = issue['image_url'].replace('uploads/', '')
            delete_image(filename)
        
        await db_service.delete_issue(issue_id)
        logger.info(f"Deleted issue {issue_id}")
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting issue: {e}")
        raise HTTPException(status_code=500, detail=str(e))
