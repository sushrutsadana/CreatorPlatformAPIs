from fastapi import APIRouter, HTTPException, Depends, Body, Response
from ..schemas.creator import CreatorCreate, Activity, ActivityType, CallRequest, EmailRequest
from ..services.creator_service import CreatorService
from ..services.call_service import CallService
from ..services.email_service import EmailService
from ..services.generate_contract import generate_contract_for_creator, test_groq_connection
from ..dependencies import get_creator_service
import logging
import traceback

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
        activity_data["activity_datetime"] = activity_data["activity_datetime"].isoformat()
        
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
            "activity_type": ActivityType.CALL_MADE,
            "body": f"""Automated call initiated to {creator['name']} (@{creator['handle']}):
• Language: {call_request.language}
• Voice: {call_request.voice}
• Duration: {call_request.max_duration} minutes
• Prompt: {call_request.prompt[:100]}..."""
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
        
        # Send the email using the optional from_email
        result = await email_service.send_email(
            to_email=creator['email'],
            subject=email_request.subject,
            body=email_request.body,
            cc=email_request.cc,
            bcc=email_request.bcc,
            from_email=email_request.from_email
        )
        
        # Log the email activity
        activity_data = {
            "creator_id": creator_id,
            "activity_type": ActivityType.EMAIL_SENT,
            "body": f"""Email sent to {creator['name']} (@{creator['handle']}):
Subject: {email_request.subject}
To: {creator['email']}
From: {result.get('from')}
Content: {email_request.body[:500]}..."""
        }
        await creator_service.log_activity(activity_data)
        
        return {"status": "success", "data": result}
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/creators/{creator_id}/generate-contract")
async def generate_contract(creator_id: str, response: Response):
    """
    Generate a contract for a creator based on their email conversations.
    
    This endpoint retrieves all email conversations for the creator,
    then uses Groq's LLM to generate a formal contract based on the conversation content.
    """
    try:
        logger.info(f"Generate contract endpoint called with creator_id: {creator_id}")
        
        # Generate contract using the Groq-based service
        contract_text = await generate_contract_for_creator(creator_id)
        
        if not contract_text:
            logger.error(f"Empty contract text received for creator_id: {creator_id}")
            raise HTTPException(status_code=500, detail="Failed to generate contract text")
        
        logger.info(f"Contract generated successfully for creator_id: {creator_id}")
        
        # Return the contract text
        return {
            "status": "success",
            "creator_id": creator_id,
            "contract": contract_text
        }
        
    except HTTPException as he:
        logger.error(f"HTTP exception in generate_contract endpoint: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in generate_contract endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        response.status_code = 500
        return {"detail": f"Internal server error: {str(e)}"}

@router.get("/creators/test-groq")
def test_groq():
    """Test endpoint to verify Groq API connection"""
    try:
        result = test_groq_connection()
        return {"status": "success" if result else "failed", "groq_working": result}
    except Exception as e:
        logger.error(f"Groq test failed: {str(e)}")
        logger.error(traceback.format_exc())
        return {"status": "error", "error": str(e)} 