import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

logger.info(f"Attempting to connect to Supabase at URL: {url}")

supabase_client: Client = create_client(url, key)

logger.info("Successfully connected to Supabase")

# Export the client
__all__ = ['supabase_client'] 