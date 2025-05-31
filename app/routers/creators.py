from fastapi import APIRouter, HTTPException, Depends, Body
from ..schemas.creator import CreatorCreate, Activity, ActivityType, CallRequest, EmailRequest
from ..services.creator_service import CreatorService
from ..services.call_service import CallService
from ..services.email_service import EmailService
from ..dependencies import get_creator_service
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["creators"])  # Remove '/creators' prefix to avoid duplication

@router.get("/creators", response_model=list)
async def get_all_creators(creator_service: CreatorService = Depends(get_creator_service)):
    """Retrieve all creators with all fields."""
    try:
        creators = await creator_service.get_all_creators()
        return creators
    except Exception as e:
        logger.error(f"Error retrieving creators: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/creators/{creator_id}/activities")
async def create_activity(
    creator_id: str, 
    activity: Activity,
    creator_service: CreatorService = Depends(get_creator_service)
):
    try:
        activity_data = activity.dict()
        activity_data["creator_id"] = creator_id
        # Move body to metadata
        if "body" in activity_data:
            activity_data["metadata"] = {"body": activity_data.pop("body")}
        else:
            activity_data["metadata"] = {}
        activity_data["created_at"] = activity_data.get("created_at", datetime.now().isoformat())
        activity_data["updated_at"] = activity_data.get("updated_at", datetime.now().isoformat())
        activity_data["status"] = activity_data.get("status", "completed")
        
        activity_record = await creator_service.log_activity(activity_data)
        return {"status": "success", "data": activity_record}
    except Exception as e:
        logger.error(f"Error in create_activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/creators/{creator_id}/call")
async def make_call_to_creator(
    creator_id: str,
    call_request: CallRequest = Body(...),
    creator_service: CreatorService = Depends(get_creator_service),
    call_service: CallService = Depends()
):
    """
    Make an automated call to a creator with custom language and voice settings.
    """
    try:
        # Get creator's information
        creator = await creator_service.get_creator(creator_id)
        if not creator.get('phone_number'):
            raise HTTPException(status_code=400, detail="Creator has no phone number")

        # Make the call with custom prompt and language
        result = await call_service.make_call(
            phone_number=creator['phone_number'],
            name=creator['name'],
            handle=creator['handle'],
            prompt=call_request.prompt,
            language=call_request.language,
            voice=call_request.voice,
            max_duration=call_request.max_duration,
            creator_id=creator_id
        )

        # Log activity
        activity_data = {
            "creator_id": creator_id,
            "type": ActivityType.CALL_MADE,
            "status": "completed",
            "metadata": {
                "body": f"""Automated call initiated to {creator['name']} (@{creator['handle']}):\n• Language: {call_request.language}\n• Voice: {call_request.voice}\n• Duration: {call_request.max_duration} minutes\n• Prompt: {call_request.prompt[:100]}..."""
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        await creator_service.log_activity(activity_data)

        return {
            "status": "success",
            "data": result,
            "message": f"Call initiated in {call_request.language} with {call_request.voice} voice"
        }
    except Exception as e:
        logger.error(f"Error initiating call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/creators/{creator_id}/email")
async def send_email_to_creator(
    creator_id: str,
    email_request: EmailRequest,
    creator_service: CreatorService = Depends(get_creator_service),
    email_service: EmailService = Depends()
):
    """Send an email to a creator"""
    try:
        # Get creator information
        creator = await creator_service.get_creator(creator_id)
        if not creator.get('email'):
            raise HTTPException(status_code=400, detail="Creator has no email address")
        
        # Send the email (removed from_email argument)
        result = await email_service.send_email(
            to_email=creator['email'],
            subject=email_request.subject,
            body=email_request.body,
            cc=email_request.cc,
            bcc=email_request.bcc
        )
        
        # Log the email activity
        activity_data = {
            "creator_id": creator_id,
            "type": ActivityType.EMAIL_SENT,
            "status": "completed",
            "metadata": {
                "body": f"""Email sent to {creator['name']} (@{creator['handle']}):\nSubject: {email_request.subject}\nTo: {creator['email']}\nFrom: {result.get('from')}\nContent: {email_request.body[:500]}..."""
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        await creator_service.log_activity(activity_data)
        
        return {"status": "success", "data": result}
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 