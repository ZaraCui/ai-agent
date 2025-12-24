"""
Database client for Supabase
Handles connection and basic operations by composing clients from gotrue and postgrest.
"""
import os
from dotenv import load_dotenv
from gotrue import SyncGoTrueClient
from postgrest import SyncPostgrestClient

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

class CustomSupabaseClient:
    """A custom Supabase client that combines auth and database functionalities."""
    def __init__(self, url: str, key: str):
        if not url or not key:
            raise ValueError("Supabase URL and Key cannot be None")
        self.url = url
        self.key = key
        
        headers = {"apiKey": self.key, "Authorization": f"Bearer {self.key}"}
        
        self.auth = SyncGoTrueClient(
            url=f"{self.url}/auth/v1",
            headers=headers,
            auto_refresh_token=True,
        )

        # The PostgrestClient needs a different `Authorization` header format for service key usage
        db_headers = {"apiKey": self.key, "Authorization": f"Bearer {self.key}"}
        self.postgrest = SyncPostgrestClient(
            base_url=f"{self.url}/rest/v1", 
            headers=db_headers
        )

    def from_(self, table: str):
        """Select a table."""
        return self.postgrest.from_(table)

# Initialize Supabase client
db: CustomSupabaseClient = None

def get_db_client() -> CustomSupabaseClient:
    """
    Returns the initialized Supabase client
    """
    global db
    if not db:
        # Load environment variables if not already loaded
        load_dotenv()
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY")
        
        if not url or not key:
            raise ValueError(f"Supabase environment variables not found. URL: {url}, KEY: {'***' if key else None}")
        
        db = CustomSupabaseClient(url, key)
    return db

def check_db_connection():
    """
    Check if connection to Supabase is successful
    """
    try:
        if db:
            # A more robust check could be added here if needed,
            # for example, fetching a small piece of data.
            return True, "Client initialized successfully."
        else:
            return False, "Client initialization failed. Check environment variables."
    except Exception as e:
        return False, f"Connection failed: {str(e)}"
