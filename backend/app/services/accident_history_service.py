"""
Accident History Service
Handles accident data aggregation, filtering, and hotspot identification.
"""
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AccidentHistoryService:
    """Service for accident history and analysis."""

    def __init__(self, db_service):
        """
        Initialize accident history service.

        Args:
            db_service: SupabaseService instance for database operations
        """
        self.db = db_service

    async def get_accident_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lng: Optional[float] = None,
        max_lng: Optional[float] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """
        Get historical accident data with optional filters.

        Args:
            start_date: Filter accidents after this date
            end_date: Filter accidents before this date
            min_lat: Minimum latitude for bounding box
            max_lat: Maximum latitude for bounding box
            min_lng: Minimum longitude for bounding box
            max_lng: Maximum longitude for bounding box
            page: Page number (1-indexed)
            page_size: Number of results per page

        Returns:
            Dictionary with total count and paginated accident list
        """
        try:
            # Build filters
            filters = {
                "issue_type": "accident",
                "start_date": start_date,
                "end_date": end_date,
                "min_lat": min_lat,
                "max_lat": max_lat,
                "min_lng": min_lng,
                "max_lng": max_lng
            }

            # Get total count
            total = await self.db.count_accidents(filters)

            # Get paginated results
            offset = (page - 1) * page_size
            accidents = await self.db.get_accidents_filtered(
                filters=filters,
                limit=page_size,
                offset=offset
            )

            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "accidents": accidents
            }

        except Exception as e:
            logger.error(f"Error getting accident history: {e}", exc_info=True)
            raise

    async def get_accident_hotspots(
        self,
        min_accidents: int = 2,
        limit: int = 50
    ) -> Dict:
        """
        Identify geographic areas with multiple accidents (hotspots).
        Groups accidents by approximate location (rounded to 3 decimal places).

        Args:
            min_accidents: Minimum number of accidents to qualify as hotspot
            limit: Maximum number of hotspots to return

        Returns:
            Dictionary with total count and list of hotspots
        """
        try:
            hotspots = await self.db.get_accident_hotspots(
                min_accidents=min_accidents,
                limit=limit
            )

            return {
                "total": len(hotspots),
                "hotspots": hotspots
            }

        except Exception as e:
            logger.error(f"Error getting accident hotspots: {e}", exc_info=True)
            raise

    async def get_accident_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get statistical summary of accidents.

        Args:
            start_date: Start date for statistics
            end_date: End date for statistics

        Returns:
            Dictionary with accident statistics
        """
        try:
            stats = await self.db.get_accident_stats(
                start_date=start_date,
                end_date=end_date
            )

            return {
                "total_accidents": stats.get("total", 0),
                "avg_severity": stats.get("avg_severity", 0.0),
                "avg_urgency": stats.get("avg_urgency", 0.0),
                "critical_count": stats.get("critical_count", 0),
                "high_count": stats.get("high_count", 0),
                "resolved_count": stats.get("resolved_count", 0),
                "open_count": stats.get("open_count", 0)
            }

        except Exception as e:
            logger.error(f"Error getting accident statistics: {e}", exc_info=True)
            raise

    async def identify_dangerous_time_periods(self) -> List[Dict]:
        """
        Identify time periods (hours of day) with most accidents.

        Returns:
            List of time periods with accident counts
        """
        try:
            time_stats = await self.db.get_accidents_by_hour()

            # Sort by accident count descending
            sorted_stats = sorted(
                time_stats,
                key=lambda x: x.get("accident_count", 0),
                reverse=True
            )

            return sorted_stats[:6]  # Return top 6 most dangerous hours

        except Exception as e:
            logger.error(f"Error identifying dangerous time periods: {e}", exc_info=True)
            raise

    async def get_accident_trends(
        self,
        days: int = 30
    ) -> Dict:
        """
        Get accident trends over time.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with daily accident counts and trends
        """
        try:
            trends = await self.db.get_accident_trends(days=days)

            return {
                "period_days": days,
                "daily_counts": trends.get("daily_counts", []),
                "total_in_period": trends.get("total", 0),
                "avg_per_day": trends.get("avg_per_day", 0.0),
                "trend_direction": trends.get("trend_direction", "stable")  # increasing, decreasing, stable
            }

        except Exception as e:
            logger.error(f"Error getting accident trends: {e}", exc_info=True)
            raise
