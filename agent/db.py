"""
Database client for Supabase
Handles connection and basic operations
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") # Use the service role key for server-side operations

# Initialize Supabase client
db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_db_client() -> Client:
    """
    Returns the initialized Supabase client
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL and Key must be set in environment variables")
    return db

def check_db_connection():
    """
    Check if connection to Supabase is successful
    """
    try:
        # Perform a simple query to test connection
        # This will change once we have tables
        response = db.from_('test_table').select('*').limit(1).execute()
        
        if response.get('error'):
            return False, f"Connection failed: {response['error']['message']}"
            
        return True, "Connection successful"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"
