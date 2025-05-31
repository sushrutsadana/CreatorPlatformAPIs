from fastapi import Depends, HTTPException
from supabase import create_client
import os
import logging
from .services.creator_service import CreatorService
from .services.email_service import EmailService
from .services.call_service import CallService

logger = logging.getLogger(__name__)

def get_supabase():
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials")
            
        return create_client(
            supabase_url=supabase_url,
            supabase_key=supabase_key
        )
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database connection failed"
        )

def get_creator_service(supabase = Depends(get_supabase)):
    try:
        return CreatorService(supabase)
    except Exception as e:
        logger.error(f"Failed to initialize CreatorService: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Creator service initialization failed"
        )

def get_email_service():
    try:
        return EmailService()
    except Exception as e:
        logger.error(f"Failed to initialize EmailService: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Email service initialization failed"
        )

def get_call_service():
    try:
        return CallService()
    except Exception as e:
        logger.error(f"Failed to initialize CallService: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Call service initialization failed"
        )