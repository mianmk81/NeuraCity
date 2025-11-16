"""
Gamification Service
Handles point calculation, awarding, and rank management.
"""
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Point values for different actions
POINTS_CONFIG = {
    "issue_reported": 50,
    "issue_verified": 30,
    "issue_resolved": 20,
    "bonus": 0  # Variable, specified when awarded
}


class GamificationService:
    """Service for gamification logic."""

    def __init__(self, db_service):
        """
        Initialize gamification service.

        Args:
            db_service: SupabaseService instance for database operations
        """
        self.db = db_service

    async def award_points(
        self,
        user_id: str,
        action_type: str,
        issue_id: Optional[str] = None,
        description: Optional[str] = None,
        custom_points: Optional[int] = None
    ) -> Dict:
        """
        Award points to a user for a specific action.

        Args:
            user_id: User ID to award points to
            action_type: Type of action (issue_reported, issue_verified, etc.)
            issue_id: Related issue ID (optional)
            description: Description of the action (optional)
            custom_points: Custom point value (for bonuses, optional)

        Returns:
            Updated user record with new point total
        """
        try:
            # Determine points to award
            if custom_points is not None:
                points = custom_points
            else:
                points = POINTS_CONFIG.get(action_type, 0)

            if points == 0 and action_type != "bonus":
                logger.warning(f"Unknown action_type: {action_type}, no points awarded")
                return None

            # Create points history record
            history_data = {
                "user_id": user_id,
                "points": points,
                "action_type": action_type,
                "issue_id": issue_id,
                "description": description or f"{action_type.replace('_', ' ').title()}"
            }
            await self.db.create_points_history(history_data)

            # Update user's total points and action counts
            user = await self.db.get_user_by_id(user_id)
            if not user:
                logger.error(f"User {user_id} not found when awarding points")
                return None

            update_data = {
                "total_points": user["total_points"] + points
            }

            # Increment specific counters
            if action_type == "issue_reported":
                update_data["issues_reported"] = user["issues_reported"] + 1
            elif action_type == "issue_verified":
                update_data["issues_verified"] = user["issues_verified"] + 1

            # Update user
            updated_user = await self.db.update_user(user_id, update_data)

            # Recalculate ranks for all users
            await self.recalculate_ranks()

            logger.info(f"Awarded {points} points to user {user_id} for {action_type}")
            return updated_user

        except Exception as e:
            logger.error(f"Error awarding points: {e}", exc_info=True)
            raise

    async def recalculate_ranks(self):
        """
        Recalculate ranks for all users based on total points.
        Users with higher points get lower rank numbers (1 = best).
        """
        try:
            # Get all users sorted by points (descending) and created_at (ascending for tiebreaker)
            users = await self.db.get_all_users_for_ranking()

            # Assign ranks
            for rank, user in enumerate(users, start=1):
                await self.db.update_user(user["id"], {"rank": rank})

            logger.info(f"Recalculated ranks for {len(users)} users")

        except Exception as e:
            logger.error(f"Error recalculating ranks: {e}", exc_info=True)
            raise

    def calculate_points_for_issue(
        self,
        issue_type: str,
        severity: float,
        urgency: float
    ) -> int:
        """
        Calculate bonus points for an issue based on its attributes.
        High severity/urgency issues award more points.

        Args:
            issue_type: Type of issue
            severity: Severity score (0-1)
            urgency: Urgency score (0-1)

        Returns:
            Bonus points to award (in addition to base report points)
        """
        base_points = POINTS_CONFIG["issue_reported"]

        # Calculate bonus based on severity and urgency
        avg_score = (severity + urgency) / 2

        # Award up to 50% bonus for high severity/urgency issues
        bonus_multiplier = avg_score * 0.5
        bonus_points = int(base_points * bonus_multiplier)

        # Additional bonus for critical issue types
        if issue_type == "accident":
            bonus_points += 10

        return base_points + bonus_points

    async def get_user_rank_percentile(self, user_id: str) -> Optional[float]:
        """
        Get user's rank percentile (0-100, where 100 is top performer).

        Args:
            user_id: User ID

        Returns:
            Percentile score or None if user not found
        """
        try:
            user = await self.db.get_user_by_id(user_id)
            if not user:
                return None

            total_users = await self.db.get_total_user_count()
            if total_users == 0:
                return 0.0

            # Calculate percentile (higher rank number = lower percentile)
            percentile = ((total_users - user["rank"] + 1) / total_users) * 100
            return round(percentile, 2)

        except Exception as e:
            logger.error(f"Error calculating percentile: {e}", exc_info=True)
            return None
