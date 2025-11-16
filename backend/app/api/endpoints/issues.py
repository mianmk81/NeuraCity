"""API endpoints for issues management."""
import logging
from datetime import datetime
from typing import List, Optional

from app.api.schemas.issue import IssueResponse, IssueStatus, IssueUpdate
from app.core.dependencies import get_db
from app.services.action_engine import process_new_issue
from app.services.geocoding_service import (batch_reverse_geocode,
                                            reverse_geocode)
from app.services.image_service import delete_image, save_image, validate_image
from app.services.ml_scoring_service import (calculate_priority_ml,
                                             calculate_severity_ml,
                                             calculate_urgency_ml,
                                             determine_action_type_ml)
from app.services.supabase_service import SupabaseService
from app.utils.validators import validate_gps_coordinates
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from supabase import Client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/issues", tags=["issues"])


@router.post("", response_model=IssueResponse, status_code=201)
async def create_issue(
    lat: float = Form(..., description="Latitude"),
    lng: float = Form(..., description="Longitude"),
    issue_type: str = Form(..., description="Type of issue"),
    description: Optional[str] = Form(None, description="Issue description"),
    image: UploadFile = File(..., description="Image evidence"),
    user_id: Optional[str] = Form(None, description="User ID for gamification (optional)"),
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
        
        # Calculate avg traffic congestion
        avg_congestion = None
        if traffic_segments:
            avg_congestion = sum(t.get('congestion', 0) for t in traffic_segments) / len(traffic_segments)
        
        # Use ML for all scoring
        severity = await calculate_severity_ml(
            issue_type=issue_type,
            description=description,
            image_available=True
        )
        urgency = await calculate_urgency_ml(
            issue_type=issue_type,
            description=description,
            severity=severity,
            traffic_congestion=avg_congestion,
            time_of_day=datetime.utcnow()
        )
        priority = await calculate_priority_ml(
            severity=severity,
            urgency=urgency,
            issue_type=issue_type,
            description=description
        )
        action_type = await determine_action_type_ml(
            issue_type=issue_type,
            description=description,
            severity=severity,
            urgency=urgency
        )
        
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
            "status": "open",
            "user_id": user_id
        }

        created_issue = await db_service.create_issue(issue_data)

        # Add reverse geocoding to get location name
        try:
            location_name = await reverse_geocode(lat, lng)
            if location_name:
                created_issue['location_name'] = location_name
        except Exception as e:
            logger.warning(f"Geocoding failed for issue {created_issue['id']}: {e}")
            created_issue['location_name'] = None

        # Process with action engine (emergency queue or work order creation)
        action_engine_failed = False
        try:
            await process_new_issue(created_issue['id'], created_issue)
        except Exception as e:
            action_engine_failed = True
            logger.error(f"Error in action engine for issue {created_issue['id']}: {e}", exc_info=True)
            # Note: Issue is created successfully, but automated action (work order/emergency) failed
            # This could be retried manually by admin

        if action_engine_failed and action_type in ['emergency', 'work_order']:
            logger.warning(f"Issue {created_issue['id']} created but action engine failed for action_type={action_type}")

        # Award points to user if user_id provided (gamification)
        if user_id:
            try:
                from app.services.gamification_service import \
                    GamificationService
                gamification_service = GamificationService(db_service)

                await gamification_service.award_points(
                    user_id=user_id,
                    action_type="issue_reported",
                    issue_id=created_issue['id'],
                    description=f"Reported {issue_type} issue"
                )
                logger.info(f"Awarded points to user {user_id} for reporting issue {created_issue['id']}")
            except Exception as e:
                # Don't fail the request if gamification fails
                logger.warning(f"Failed to award points for issue {created_issue['id']}: {e}")

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
    limit: int = 50,
    db: Client = Depends(get_db)
):
    """
    Get list of issues with optional filters.

    Query parameters:
    - issue_type: Filter by type (accident, pothole, traffic_light, other)
    - status: Filter by status (open, in_progress, resolved, closed)
    - min_severity: Minimum severity (0-1)
    - max_severity: Maximum severity (0-1)
    - limit: Maximum number of results (default 50, max 100)
    """
    try:
        db_service = SupabaseService(db)
        issues = await db_service.get_issues(
            issue_type=issue_type,
            status=status,
            min_severity=min_severity,
            max_severity=max_severity,
            limit=min(limit, 100)
        )

        # OPTIMIZATION: Use location_name from Supabase if available, otherwise geocode
        # Priority: 1) Database value, 2) File cache, 3) API geocoding
        issues_needing_geocoding = []
        coord_to_issues = {}  # Map coord key -> list of issue indices
        
        for idx, issue in enumerate(issues):
            # If location_name already exists in Supabase, use it (fastest - no geocoding needed!)
            if issue.get('location_name'):
                continue  # Skip - already has location name from database
            
            # Only geocode if missing from database
            coord_key = (round(issue['lat'], 4), round(issue['lng'], 4))
            if coord_key not in coord_to_issues:
                coord_to_issues[coord_key] = []
            coord_to_issues[coord_key].append(idx)
            issues_needing_geocoding.append((issue['lat'], issue['lng']))
        
        # Only geocode unique coordinates that are missing location_name
        # File cache is checked automatically in reverse_geocode for fast lookups
        if issues_needing_geocoding:
            unique_coords = {}  # Map rounded coord key -> (lat, lng) tuple
            for lat, lng in issues_needing_geocoding:
                coord_key = (round(lat, 4), round(lng, 4))
                if coord_key not in unique_coords:
                    unique_coords[coord_key] = (lat, lng)
            
            try:
                location_map = await batch_reverse_geocode(list(unique_coords.values()))
                
                # Apply location names to issues that needed geocoding
                for coord_key, issue_indices in coord_to_issues.items():
                    lat, lng = unique_coords[coord_key]
                    location_name = location_map.get((lat, lng))
                    
                    for idx in issue_indices:
                        issues[idx]['location_name'] = location_name
            except Exception as e:
                logger.warning(f"Batch geocoding failed: {e}")
                # Fallback: set None for issues that needed geocoding
                for idx in sum(coord_to_issues.values(), []):
                    issues[idx]['location_name'] = None
        
        # Ensure all issues have location_name field (set to None if missing and geocoding failed)
        for issue in issues:
            if 'location_name' not in issue:
                issue['location_name'] = None

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

        # Add location name (use from Supabase if available, otherwise geocode)
        if not issue.get('location_name'):
            try:
                location_name = await reverse_geocode(issue['lat'], issue['lng'])
                issue['location_name'] = location_name
            except Exception as e:
                logger.debug(f"Geocoding failed: {e}")
                issue['location_name'] = None
        # If location_name already exists in Supabase, it's already in the issue dict

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
