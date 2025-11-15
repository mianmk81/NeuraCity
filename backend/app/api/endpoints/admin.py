"""API endpoints for admin operations."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from supabase import Client

from app.api.schemas.admin import (
    EmergencyResponse,
    EmergencyUpdate,
    WorkOrderResponse,
    WorkOrderUpdate
)
from app.core.dependencies import get_db
from app.services.supabase_service import SupabaseService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/emergency", response_model=List[EmergencyResponse])
async def get_emergency_queue(
    status: Optional[str] = None,
    db: Client = Depends(get_db)
):
    try:
        db_service = SupabaseService(db)
        emergencies = await db_service.get_emergency_queue(status=status)
        return emergencies
    except Exception as e:
        logger.error(f"Error fetching emergency queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/emergency/{emergency_id}", response_model=EmergencyResponse)
async def update_emergency(
    emergency_id: str,
    update_data: EmergencyUpdate,
    db: Client = Depends(get_db)
):
    try:
        db_service = SupabaseService(db)
        existing = await db_service.get_emergency_by_id(emergency_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Emergency entry not found")
        update_dict = {"status": update_data.status.value}
        updated = await db_service.update_emergency(emergency_id, update_dict)
        logger.info(f"Updated emergency {emergency_id}")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating emergency: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/work-orders", response_model=List[WorkOrderResponse])
async def get_work_orders(
    status: Optional[str] = None,
    db: Client = Depends(get_db)
):
    try:
        db_service = SupabaseService(db)
        work_orders = await db_service.get_work_orders(status=status)
        formatted_orders = []
        for wo in work_orders:
            contractor = wo.get('contractors')
            formatted = {
                "id": wo['id'],
                "issue_id": wo['issue_id'],
                "contractor_id": wo.get('contractor_id'),
                "contractor_name": contractor.get('name') if contractor else None,
                "contractor_specialty": contractor.get('specialty') if contractor else None,
                "material_suggestion": wo.get('material_suggestion'),
                "status": wo['status'],
                "created_at": wo['created_at']
            }
            formatted_orders.append(formatted)
        return formatted_orders
    except Exception as e:
        logger.error(f"Error fetching work orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/work-orders/{work_order_id}/approve", response_model=WorkOrderResponse)
async def approve_work_order(
    work_order_id: str,
    db: Client = Depends(get_db)
):
    try:
        db_service = SupabaseService(db)
        existing = await db_service.get_work_order_by_id(work_order_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Work order not found")
        updated = await db_service.update_work_order(work_order_id, {"status": "approved"})
        contractor = updated.get('contractors') if isinstance(updated, dict) else None
        formatted = {
            "id": updated['id'],
            "issue_id": updated['issue_id'],
            "contractor_id": updated.get('contractor_id'),
            "contractor_name": contractor.get('name') if contractor else None,
            "contractor_specialty": contractor.get('specialty') if contractor else None,
            "material_suggestion": updated.get('material_suggestion'),
            "status": updated['status'],
            "created_at": updated['created_at']
        }
        logger.info(f"Approved work order {work_order_id}")
        return formatted
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving work order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/work-orders/{work_order_id}", response_model=WorkOrderResponse)
async def update_work_order(
    work_order_id: str,
    update_data: WorkOrderUpdate,
    db: Client = Depends(get_db)
):
    try:
        db_service = SupabaseService(db)
        existing = await db_service.get_work_order_by_id(work_order_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Work order not found")
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            raise HTTPException(status_code=400, detail="No update data provided")
        if 'status' in update_dict:
            update_dict['status'] = update_dict['status'].value
        updated = await db_service.update_work_order(work_order_id, update_dict)
        contractor = updated.get('contractors') if isinstance(updated, dict) else None
        formatted = {
            "id": updated['id'],
            "issue_id": updated['issue_id'],
            "contractor_id": updated.get('contractor_id'),
            "contractor_name": contractor.get('name') if contractor else None,
            "contractor_specialty": contractor.get('specialty') if contractor else None,
            "material_suggestion": updated.get('material_suggestion'),
            "status": updated['status'],
            "created_at": updated['created_at']
        }
        logger.info(f"Updated work order {work_order_id}")
        return formatted
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating work order: {e}")
        raise HTTPException(status_code=500, detail=str(e))
