"""Supabase service for database operations."""
from supabase import Client
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service class for Supabase database operations."""

    def __init__(self, client: Client):
        self.client = client

    async def get_issues(self, issue_type=None, status=None, min_severity=None, max_severity=None, limit=100):
        try:
            query = self.client.table("issues").select("*")
            if issue_type:
                query = query.eq("issue_type", issue_type)
            if status:
                query = query.eq("status", status)
            if min_severity is not None:
                query = query.gte("severity", min_severity)
            if max_severity is not None:
                query = query.lte("severity", max_severity)
            query = query.order("created_at", desc=True).limit(limit)
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching issues: {e}")
            raise

    async def get_issue_by_id(self, issue_id: str):
        try:
            response = self.client.table("issues").select("*").eq("id", issue_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching issue: {e}")
            raise

    async def create_issue(self, issue_data: dict):
        try:
            response = self.client.table("issues").insert(issue_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating issue: {e}")
            raise

    async def update_issue(self, issue_id: str, update_data: dict):
        try:
            response = self.client.table("issues").update(update_data).eq("id", issue_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating issue: {e}")
            raise

    async def delete_issue(self, issue_id: str):
        try:
            self.client.table("issues").delete().eq("id", issue_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting issue: {e}")
            raise

    async def get_mood_areas(self):
        try:
            response = self.client.table("mood_areas").select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching mood areas: {e}")
            raise

    async def get_traffic_segments(self):
        try:
            response = self.client.table("traffic_segments").select("*").order("ts", desc=True).limit(1000).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching traffic: {e}")
            raise

    async def get_noise_segments(self):
        try:
            response = self.client.table("noise_segments").select("*").order("ts", desc=True).limit(1000).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching noise: {e}")
            raise

    async def get_contractors(self, specialty=None):
        try:
            query = self.client.table("contractors").select("*").eq("has_city_contract", True)
            if specialty:
                query = query.eq("specialty", specialty)
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching contractors: {e}")
            raise

    async def get_contractor_by_id(self, contractor_id: str):
        try:
            response = self.client.table("contractors").select("*").eq("id", contractor_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching contractor by ID: {e}")
            raise

    async def create_work_order(self, data: dict):
        try:
            response = self.client.table("work_orders").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating work order: {e}")
            raise

    async def get_work_orders(self, status=None):
        try:
            query = self.client.table("work_orders").select("*, contractors(id, name, specialty, contact_email)")
            if status:
                query = query.eq("status", status)
            response = query.order("created_at", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching work orders: {e}")
            raise

    async def get_work_order_by_id(self, work_order_id: str):
        try:
            response = self.client.table("work_orders").select("*, contractors(*)").eq("id", work_order_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching work order: {e}")
            raise

    async def update_work_order(self, work_order_id: str, data: dict):
        try:
            response = self.client.table("work_orders").update(data).eq("id", work_order_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating work order: {e}")
            raise

    async def create_emergency_entry(self, data: dict):
        try:
            response = self.client.table("emergency_queue").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating emergency: {e}")
            raise

    async def get_emergency_queue(self, status=None):
        try:
            query = self.client.table("emergency_queue").select("*")
            if status:
                query = query.eq("status", status)
            response = query.order("created_at", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching emergency queue: {e}")
            raise

    async def get_emergency_by_id(self, emergency_id: str):
        try:
            response = self.client.table("emergency_queue").select("*").eq("id", emergency_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching emergency: {e}")
            raise

    async def update_emergency(self, emergency_id: str, data: dict):
        try:
            response = self.client.table("emergency_queue").update(data).eq("id", emergency_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating emergency: {e}")
            raise
