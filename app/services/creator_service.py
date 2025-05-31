from datetime import datetime
from ..schemas.creator import CreatorCreate, Activity, ActivityType
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class CreatorService:
    def __init__(self, supabase):
        self.supabase = supabase

    async def create_creator(self, creator: CreatorCreate) -> dict:
        try:
            # Create creator in Supabase
            creator_data = creator.dict()
            creator_data["created_at"] = datetime.now().isoformat()
            creator_data["updated_at"] = datetime.now().isoformat()
            
            result = self.supabase.table("creators").insert(creator_data).execute()
            creator_record = result.data[0]
            
            # Log creator creation activity
            activity_data = {
                "creator_id": creator_record["id"],
                "activity_type": ActivityType.CREATOR_CREATED,
                "body": f"Creator {creator.name} (@{creator.handle}) created in system",
                "activity_datetime": datetime.now().isoformat()
            }
            await self.log_activity(activity_data)
            
            return creator_record
        except Exception as e:
            logger.error(f"Error creating creator: {str(e)}")
            raise

    async def get_creator(self, creator_id: str) -> dict:
        """Get a specific creator by ID"""
        try:
            result = self.supabase.table("creators").select("*").eq("id", creator_id).execute()
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Creator with ID {creator_id} not found")
            return result.data[0]
        except Exception as e:
            logger.error(f"Error getting creator: {str(e)}")
            raise

    async def get_all_creators(self) -> list:
        """Get all creators with all fields"""
        try:
            result = self.supabase.table("creators").select("*").execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting all creators: {str(e)}")
            raise

    async def log_activity(self, activity_data: dict) -> dict:
        try:
            result = self.supabase.table("activities").insert(activity_data).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")
            raise

    async def update_creator_status(self, creator_id: str, new_status: str) -> dict:
        try:
            # Update creator status
            result = self.supabase.table("creators").update({
                "status": new_status,
                "updated_at": datetime.now().isoformat()
            }).eq("id", creator_id).execute()
            
            if not result.data:
                raise Exception(f"Creator with ID {creator_id} not found")
            
            # Log status change activity
            activity_data = {
                "creator_id": creator_id,
                "activity_type": ActivityType.STATUS_CHANGED,
                "body": f"Creator status changed to {new_status}",
                "activity_datetime": datetime.now().isoformat()
            }
            await self.log_activity(activity_data)
            
            return result.data[0]
        except Exception as e:
            logger.error(f"Error updating creator status: {str(e)}")
            raise 