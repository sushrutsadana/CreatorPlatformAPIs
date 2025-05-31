import os
from mailjet_rest import Client
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = os.environ["MAILJET_API_KEY"]
        self.api_secret = os.environ["MAILJET_API_SECRET"]
        self.sender = os.environ["MAILJET_SENDER"]
        self.mailjet = Client(auth=(self.api_key, self.api_secret), version='v3.1')

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None
    ) -> dict:
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": self.sender,
                        "Name": "Your App"
                    },
                    "To": [{"Email": to_email}],
                    "Subject": subject,
                    "TextPart": body,
                }
            ]
        }
        if cc:
            data['Messages'][0]['Cc'] = [{"Email": cc}]
        if bcc:
            data['Messages'][0]['Bcc'] = [{"Email": bcc}]
        try:
            result = self.mailjet.send.create(data=data)
            logger.info(f"Mailjet response: {result.status_code} {result.json()}")
            return {"status": "success", "mailjet_status": result.status_code}
        except Exception as e:
            logger.error(f"Mailjet error: {str(e)}")
            return {"status": "error", "detail": str(e)} 