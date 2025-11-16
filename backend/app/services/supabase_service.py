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

    # =====================================================
    # RISK INDEX OPERATIONS
    # =====================================================

    async def get_risk_blocks(self, risk_category=None, min_risk=None, max_risk=None, limit=1000):
        """Get risk blocks with optional filtering."""
        try:
            query = self.client.table("risk_blocks").select("*")
            if risk_category:
                query = query.eq("risk_category", risk_category)
            if min_risk is not None:
                query = query.gte("composite_risk_index", min_risk)
            if max_risk is not None:
                query = query.lte("composite_risk_index", max_risk)
            query = query.order("composite_risk_index", desc=True).limit(limit)
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching risk blocks: {e}")
            raise

    async def get_risk_block_by_id(self, block_id: str):
        """Get a specific risk block by block_id."""
        try:
            response = self.client.table("risk_blocks").select("*").eq("block_id", block_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching risk block: {e}")
            raise

    async def get_risk_blocks_in_bounds(self, lat_min: float, lat_max: float, lng_min: float, lng_max: float):
        """Get risk blocks within geographic bounds."""
        try:
            response = (self.client.table("risk_blocks")
                       .select("*")
                       .gte("lat", lat_min)
                       .lte("lat", lat_max)
                       .gte("lng", lng_min)
                       .lte("lng", lng_max)
                       .execute())
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching risk blocks in bounds: {e}")
            raise

    async def create_risk_block(self, block_data: dict):
        """Create a new risk block."""
        try:
            response = self.client.table("risk_blocks").insert(block_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating risk block: {e}")
            raise

    async def update_risk_block(self, block_id: str, update_data: dict):
        """Update an existing risk block."""
        try:
            response = self.client.table("risk_blocks").update(update_data).eq("block_id", block_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating risk block: {e}")
            raise

    async def batch_upsert_risk_blocks(self, blocks: list):
        """Batch insert or update risk blocks."""
        try:
            response = self.client.table("risk_blocks").upsert(blocks, on_conflict="block_id").execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error batch upserting risk blocks: {e}")
            raise

    async def get_risk_factors(self, block_id=None, factor_type=None, limit=1000):
        """Get risk factor measurements."""
        try:
            query = self.client.table("risk_factors").select("*")
            if block_id:
                query = query.eq("block_id", block_id)
            if factor_type:
                query = query.eq("factor_type", factor_type)
            query = query.order("measurement_date", desc=True).limit(limit)
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching risk factors: {e}")
            raise

    async def create_risk_factor(self, factor_data: dict):
        """Create a new risk factor measurement."""
        try:
            response = self.client.table("risk_factors").insert(factor_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating risk factor: {e}")
            raise

    async def batch_insert_risk_factors(self, factors: list):
        """Batch insert risk factor measurements."""
        try:
            response = self.client.table("risk_factors").insert(factors).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error batch inserting risk factors: {e}")
            raise

    async def get_risk_history(self, block_id: str, days=30):
        """Get historical risk data for a block."""
        try:
            response = (self.client.table("risk_history")
                       .select("*")
                       .eq("block_id", block_id)
                       .order("snapshot_date", desc=True)
                       .limit(days)
                       .execute())
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching risk history: {e}")
            raise

    async def create_risk_history_snapshot(self, snapshot_data: dict):
        """Create a historical risk snapshot."""
        try:
            response = self.client.table("risk_history").insert(snapshot_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating risk history snapshot: {e}")
            raise

    async def batch_insert_risk_history(self, snapshots: list):
        """Batch insert historical risk snapshots."""
        try:
            response = self.client.table("risk_history").insert(snapshots).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error batch inserting risk history: {e}")
            raise

    async def get_risk_config(self, config_name="default"):
        """Get risk calculation configuration."""
        try:
            response = self.client.table("risk_config").select("*").eq("config_name", config_name).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching risk config: {e}")
            raise

    async def update_risk_config(self, config_name: str, config_data: dict):
        """Update risk calculation configuration."""
        try:
            response = self.client.table("risk_config").update(config_data).eq("config_name", config_name).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating risk config: {e}")
            raise

    # =====================================================
    # USER AND GAMIFICATION OPERATIONS
    # =====================================================

    async def create_user(self, user_data: dict):
        """Create a new user."""
        try:
            response = self.client.table("users").insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    async def get_user_by_id(self, user_id: str):
        """Get user by ID."""
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            raise

    async def get_user_by_username(self, username: str):
        """Get user by username."""
        try:
            response = self.client.table("users").select("*").eq("username", username).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching user by username: {e}")
            raise

    async def get_user_by_email(self, email: str):
        """Get user by email."""
        try:
            response = self.client.table("users").select("*").eq("email", email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching user by email: {e}")
            raise

    async def update_user(self, user_id: str, update_data: dict):
        """Update user data."""
        try:
            response = self.client.table("users").update(update_data).eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise

    async def get_leaderboard(self, limit: int = 10, offset: int = 0):
        """Get leaderboard with pagination."""
        try:
            response = (
                self.client.table("users")
                .select("id, username, full_name, avatar_url, total_points, rank, issues_reported, issues_verified, created_at")
                .order("total_points", desc=True)
                .order("created_at")
                .range(offset, offset + limit - 1)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching leaderboard: {e}")
            raise

    async def get_total_user_count(self):
        """Get total number of users."""
        try:
            response = self.client.table("users").select("id", count="exact").execute()
            return response.count if hasattr(response, 'count') else 0
        except Exception as e:
            logger.error(f"Error counting users: {e}")
            raise

    async def get_all_users_for_ranking(self):
        """Get all users sorted for ranking calculation."""
        try:
            response = (
                self.client.table("users")
                .select("id, total_points, created_at")
                .order("total_points", desc=True)
                .order("created_at")
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching users for ranking: {e}")
            raise

    async def create_points_history(self, history_data: dict):
        """Create a points history record."""
        try:
            response = self.client.table("user_points_history").insert(history_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating points history: {e}")
            raise

    async def get_user_points_history(self, user_id: str, limit: int = 50):
        """Get user's points history."""
        try:
            response = (
                self.client.table("user_points_history")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching points history: {e}")
            raise

    # =====================================================
    # ACCIDENT HISTORY OPERATIONS
    # =====================================================

    async def count_accidents(self, filters: dict):
        """Count accidents with filters."""
        try:
            query = self.client.table("issues").select("id", count="exact").eq("issue_type", "accident")

            if filters.get("start_date"):
                query = query.gte("created_at", filters["start_date"].isoformat())
            if filters.get("end_date"):
                query = query.lte("created_at", filters["end_date"].isoformat())
            if filters.get("min_lat") is not None:
                query = query.gte("lat", filters["min_lat"])
            if filters.get("max_lat") is not None:
                query = query.lte("lat", filters["max_lat"])
            if filters.get("min_lng") is not None:
                query = query.gte("lng", filters["min_lng"])
            if filters.get("max_lng") is not None:
                query = query.lte("lng", filters["max_lng"])

            response = query.execute()
            return response.count if hasattr(response, 'count') else 0
        except Exception as e:
            logger.error(f"Error counting accidents: {e}")
            raise

    async def get_accidents_filtered(self, filters: dict, limit: int = 20, offset: int = 0):
        """Get accidents with filters and pagination."""
        try:
            query = (
                self.client.table("issues")
                .select("id, lat, lng, description, image_url, severity, urgency, priority, status, created_at")
                .eq("issue_type", "accident")
            )

            if filters.get("start_date"):
                query = query.gte("created_at", filters["start_date"].isoformat())
            if filters.get("end_date"):
                query = query.lte("created_at", filters["end_date"].isoformat())
            if filters.get("min_lat") is not None:
                query = query.gte("lat", filters["min_lat"])
            if filters.get("max_lat") is not None:
                query = query.lte("lat", filters["max_lat"])
            if filters.get("min_lng") is not None:
                query = query.gte("lng", filters["min_lng"])
            if filters.get("max_lng") is not None:
                query = query.lte("lng", filters["max_lng"])

            response = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching filtered accidents: {e}")
            raise

    async def get_accident_hotspots(self, min_accidents: int = 2, limit: int = 50):
        """Get accident hotspots (uses database view)."""
        try:
            response = (
                self.client.table("accident_hotspots")
                .select("*")
                .gte("accident_count", min_accidents)
                .limit(limit)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching accident hotspots: {e}")
            raise

    async def get_accident_stats(self, start_date=None, end_date=None):
        """Get accident statistics."""
        try:
            query = self.client.table("issues").select("severity, urgency, priority, status").eq("issue_type", "accident")

            if start_date:
                query = query.gte("created_at", start_date.isoformat())
            if end_date:
                query = query.lte("created_at", end_date.isoformat())

            response = query.execute()
            accidents = response.data if response.data else []

            severities = [a.get("severity", 0) for a in accidents if a.get("severity") is not None]
            urgencies = [a.get("urgency", 0) for a in accidents if a.get("urgency") is not None]

            return {
                "total": len(accidents),
                "avg_severity": sum(severities) / len(severities) if severities else 0.0,
                "avg_urgency": sum(urgencies) / len(urgencies) if urgencies else 0.0,
                "critical_count": sum(1 for a in accidents if a.get("priority") == "critical"),
                "high_count": sum(1 for a in accidents if a.get("priority") == "high"),
                "resolved_count": sum(1 for a in accidents if a.get("status") == "resolved"),
                "open_count": sum(1 for a in accidents if a.get("status") == "open")
            }
        except Exception as e:
            logger.error(f"Error getting accident stats: {e}")
            raise

    async def get_accidents_by_hour(self):
        """Get accidents grouped by hour of day."""
        try:
            response = self.client.table("issues").select("created_at").eq("issue_type", "accident").execute()
            accidents = response.data if response.data else []

            hour_counts = {}
            for accident in accidents:
                from datetime import datetime
                dt = datetime.fromisoformat(accident["created_at"].replace("Z", "+00:00"))
                hour = dt.hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1

            return [{"hour": h, "accident_count": c} for h, c in hour_counts.items()]
        except Exception as e:
            logger.error(f"Error getting accidents by hour: {e}")
            raise

    async def get_accident_trends(self, days: int = 30):
        """Get accident trends over time."""
        try:
            from datetime import datetime, timedelta

            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            response = (
                self.client.table("issues")
                .select("created_at")
                .eq("issue_type", "accident")
                .gte("created_at", start_date.isoformat())
                .execute()
            )
            accidents = response.data if response.data else []

            total = len(accidents)
            avg_per_day = total / days if days > 0 else 0

            return {
                "total": total,
                "avg_per_day": round(avg_per_day, 2),
                "daily_counts": [],
                "trend_direction": "stable"
            }
        except Exception as e:
            logger.error(f"Error getting accident trends: {e}")
            raise

    async def get_issues_in_bounds(self, min_lat: float, max_lat: float, min_lng: float, max_lng: float):
        """Get all issues within bounding box."""
        try:
            response = (
                self.client.table("issues")
                .select("*")
                .gte("lat", min_lat)
                .lte("lat", max_lat)
                .gte("lng", min_lng)
                .lte("lng", max_lng)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching issues in bounds: {e}")
            raise

    async def get_traffic_in_bounds(self, min_lat: float, max_lat: float, min_lng: float, max_lng: float):
        """Get traffic data within bounding box."""
        try:
            response = (
                self.client.table("traffic_segments")
                .select("congestion")
                .gte("lat", min_lat)
                .lte("lat", max_lat)
                .gte("lng", min_lng)
                .lte("lng", max_lng)
                .order("ts", desc=True)
                .limit(100)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching traffic in bounds: {e}")
            raise

    async def get_noise_in_bounds(self, min_lat: float, max_lat: float, min_lng: float, max_lng: float):
        """Get noise data within bounding box."""
        try:
            response = (
                self.client.table("noise_segments")
                .select("noise_db")
                .gte("lat", min_lat)
                .lte("lat", max_lat)
                .gte("lng", min_lng)
                .lte("lng", max_lng)
                .order("ts", desc=True)
                .limit(100)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching noise in bounds: {e}")
            raise

    async def upsert_risk_block(self, risk_data: dict):
        """Insert or update risk block data."""
        try:
            response = self.client.table("risk_blocks").upsert(risk_data, on_conflict="block_id").execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error upserting risk block: {e}")
            raise
