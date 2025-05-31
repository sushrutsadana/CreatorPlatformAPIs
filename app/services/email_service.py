import logging
from typing import Optional

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        logger.info("EmailService initialized in mock mode")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None
    ) -> dict:
        """
        Mock email sending - just logs the attempt
        """
        logger.info(f"Would send email to {to_email} with subject: {subject}")
        return {
            "status": "success",
            "message": "Email logged (mock mode)"
        } 