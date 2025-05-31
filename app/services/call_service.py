import os
import requests
import logging
from typing import Dict, Optional
from datetime import datetime
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class CallService:
    def __init__(self):
        self.api_key = os.environ.get('BLAND_AI_API_KEY')
        if not self.api_key:
            raise ValueError("BLAND_AI_API_KEY environment variable is not set")
            
        self.base_url = 'https://api.bland.ai/v1'
        self.webhook_url = os.environ.get('BLAND_AI_WEBHOOK_URL')  # Get from env
        if not self.webhook_url:
            raise ValueError("BLAND_AI_WEBHOOK_URL environment variable is not set")
            
        self.headers = {
            'Authorization': self.api_key
        }

    async def make_call(
        self, 
        phone_number: str, 
        name: str, 
        handle: str, 
        prompt: str, 
        creator_id: str, 
        language: str = "en",
        voice: str = "nat",
        max_duration: int = 12
    ) -> Dict:
        """Make a call using BlandAI"""
        try:
            data = {
                "phone_number": phone_number,
                "task": prompt,
                "model": "base",
                "language": language,
                "voice": voice,
                "max_duration": max_duration,
                "webhook": self.webhook_url,
                "record": True,
                "metadata": {
                    "creator_id": creator_id,
                    "name": name,
                    "handle": handle
                }
            }

            logger.info(f"Making call to {phone_number} in language: {language}")
            
            response = requests.post(
                f'{self.base_url}/calls',
                json=data,
                headers=self.headers
            )
            
            # Add more detailed error handling
            if response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            response.raise_for_status()
            response_data = response.json()
            
            call_id = response_data.get('call_id')
            logger.info(f"Successfully initiated call to {phone_number} with call_id: {call_id}")
            
            return {
                "status": "success",
                "call_id": call_id,
                "data": response_data
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error making call: {str(e)}")
            raise Exception(f"Failed to make call: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error making call: {str(e)}")
            raise

    async def analyze_call(self, call_id: str) -> Dict:
        """Analyze a completed call using BlandAI's analysis endpoint"""
        try:
            response = requests.post(
                f'{self.base_url}/calls/{call_id}/analyze',
                headers=self.headers
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error analyzing call: {str(e)}")
            raise

    async def get_call_status(self, call_id: str) -> str:
        """Get the current status of a call"""
        try:
            response = requests.get(
                f'{self.base_url}/calls/{call_id}',
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get('status', 'unknown')
        except Exception as e:
            logger.error(f"Error getting call status: {str(e)}")
            raise