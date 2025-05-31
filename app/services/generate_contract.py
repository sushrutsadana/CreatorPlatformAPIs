from typing import Optional, Dict, Any, List
import os
import httpx
from fastapi import HTTPException
import logging
from groq import Groq
from dotenv import load_dotenv
from app import db
import sys
import traceback
import json

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate and initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    logger.error("GROQ_API_KEY environment variable is not set")
    raise ValueError("GROQ_API_KEY environment variable is not set")

try:
    groq_client = Groq(api_key=groq_api_key)
    logger.info("Groq client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {str(e)}")
    raise

# Define the current Groq model to use
GROQ_MODEL = "llama3-70b-8192"  # Updated to a currently supported model

class ContractGenerationService:
    def __init__(self):
        try:
            # Use the global groq_client
            self.groq_client = groq_client
            logger.info("ContractGenerationService initialized successfully")
        except Exception as e:
            error_msg = f"Error initializing ContractGenerationService: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    async def get_conversation_data(self, creator_id: str) -> List[Dict[Any, Any]]:
        try:
            logger.info(f"Fetching conversations for creator_id: {creator_id}")
            
            # Log the creator_id to make sure it's correctly formatted
            logger.debug(f"Creator ID type: {type(creator_id)}, value: {creator_id}")
            
            # Check if creator_id is valid UUID format
            if not creator_id or len(creator_id) < 10:
                logger.error(f"Invalid creator_id format: {creator_id}")
                raise HTTPException(status_code=400, detail=f"Invalid creator_id format: {creator_id}")
            
            # Fetch all email conversations from activities table for the creator
            logger.debug(f"Executing Supabase query for activities where type='Email'")
            result = db.supabase_client.table('activities') \
                .select('*') \
                .eq('type', 'Email') \
                .order('created_at', desc=True) \
                .execute()
            
            # Log the result for debugging
            logger.debug(f"Supabase query result count: {len(result.data) if result.data else 0}")
            
            if not result.data:
                logger.warning(f"No conversations found for creator_id: {creator_id}")
                raise HTTPException(status_code=404, detail="No conversations found for this creator")
            
            # Filter and process the conversations
            conversations = []
            for activity in result.data:
                try:
                    metadata = activity.get('metadata', {})
                    logger.debug(f"Processing activity metadata: {json.dumps(metadata) if metadata else 'None'}")
                    
                    if metadata and isinstance(metadata, dict):
                        # Extract the conversation details
                        conversation = {
                            'timestamp': activity.get('created_at'),
                            'to': metadata.get('to'),
                            'body': metadata.get('body', ''),
                            'status': activity.get('status')
                        }
                        conversations.append(conversation)
                    else:
                        logger.warning(f"Skipping activity with invalid metadata: {activity.get('id')}")
                except Exception as e:
                    logger.error(f"Error processing activity: {str(e)}")
                    continue
            
            if not conversations:
                logger.warning(f"No valid email conversations found for creator_id: {creator_id}")
                raise HTTPException(status_code=404, detail="No valid email conversations found")
            
            logger.info(f"Found {len(conversations)} valid conversations for creator_id: {creator_id}")
            return conversations
        except HTTPException as e:
            logger.error(f"HTTP exception in get_conversation_data: {e.detail}")
            raise e
        except Exception as e:
            error_msg = f"Error fetching conversation data: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=error_msg)

    async def generate_contract_text(self, conversations: List[Dict[Any, Any]]) -> str:
        try:
            logger.info("Generating contract using Groq API")
            
            # Prepare the prompt for contract generation
            prompt = self._prepare_contract_prompt(conversations)
            
            # Log the conversations data for debugging
            logger.debug(f"Number of conversations for prompt: {len(conversations)}")
            
            # Use the Groq client directly
            logger.info(f"Sending request to Groq API using model: {GROQ_MODEL}")
            
            try:
                completion = self.groq_client.chat.completions.create(
                    model=GROQ_MODEL,  # Use the updated model
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a legal contract generator. Generate a professional and formal contract based on the email conversations between the agency and the creator. Extract key details like scope of work, compensation, and timelines from the conversations."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )
                
                logger.info("Received response from Groq API")
                contract_text = completion.choices[0].message.content
                
                if not contract_text:
                    logger.error("Empty contract text received from Groq API")
                    raise HTTPException(status_code=500, detail="Empty contract text received from Groq API")
                    
                logger.info("Successfully generated contract")
                logger.debug(f"Contract text length: {len(contract_text)} characters")
                return contract_text
            except Exception as groq_error:
                logger.error(f"Groq API error: {str(groq_error)}")
                raise HTTPException(status_code=500, detail=f"Groq API error: {str(groq_error)}")

        except HTTPException as he:
            logger.error(f"HTTP exception in generate_contract_text: {he.detail}")
            raise he
        except Exception as e:
            error_msg = f"Error generating contract: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=error_msg)

    def _prepare_contract_prompt(self, conversations: List[Dict[Any, Any]]) -> str:
        try:
            # Create a chronological summary of the conversations
            conversation_entries = []
            
            for conv in sorted(conversations, key=lambda x: x['timestamp']):
                try:
                    entry = (
                        f"Timestamp: {conv.get('timestamp', 'N/A')}\n"
                        f"To: {conv.get('to', 'N/A')}\n"
                        f"Status: {conv.get('status', 'N/A')}\n"
                        f"Message: {conv.get('body', 'N/A')}"
                    )
                    conversation_entries.append(entry)
                except Exception as e:
                    logger.error(f"Error formatting conversation entry: {str(e)}")
                    continue
            
            conversation_summary = "\n\n".join(conversation_entries)
            
            logger.debug(f"Prepared prompt with {len(conversation_entries)} conversation entries")
            
            return f"""
            Based on the following email conversations between the agency and the creator, generate a formal contract.
            
            CONVERSATION HISTORY:
            {conversation_summary}
            
            Please generate a formal contract that includes:
            1. Introduction and parties involved (extract names and roles from the conversations)
            2. Scope of work (based on discussed deliverables and expectations)
            3. Compensation details (extract any mentioned payments, rates, or financial terms)
            4. Timeline and deliverables (based on discussed dates and milestones)
            5. Terms and conditions (standard terms plus any specific terms mentioned)
            6. Termination clauses
            7. Signatures section
            
            Note: Ensure all key details mentioned in the conversations are reflected in the appropriate sections of the contract.
            """
        except Exception as e:
            logger.error(f"Error preparing contract prompt: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return "Error preparing contract prompt. Please check logs for details."

async def generate_contract_for_creator(creator_id: str) -> str:
    """
    Main function to generate contract for a creator based on all their email conversations
    """
    try:
        logger.info(f"Starting contract generation process for creator_id: {creator_id}")
        service = ContractGenerationService()
        
        # Step 1: Fetch all email conversations
        conversations = await service.get_conversation_data(creator_id)
        
        # Step 2: Generate contract using LLM based on all conversations
        contract_text = await service.generate_contract_text(conversations)
        
        logger.info(f"Completed contract generation for creator_id: {creator_id}")
        return contract_text
    except Exception as e:
        logger.error(f"Unhandled exception in generate_contract_for_creator: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Re-raise with detailed error message
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate contract: {str(e)}"
        )

def test_groq_connection():
    """Test function to verify Groq API connection"""
    try:
        logger.info("Testing Groq API connection...")
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,  # Use the updated model
            messages=[{"role": "user", "content": "Hello, respond with 'API working'"}],
            max_tokens=10
        )
        logger.info(f"Test successful: {response.choices[0].message.content}")
        return True
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False 