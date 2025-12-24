"""
Itinerary Storage Service
Allows users to save and retrieve itineraries.
Uses Redis for temporary sharing and a database for persistent storage.
"""
import json
import uuid
from typing import Optional, Dict
from agent.db import get_db_client
from agent.cache import get_cache_client

class ItineraryStorage:
    """Manage itinerary storage and retrieval"""

    def __init__(self):
        """
        Initialize storage clients.
        """
        self.cache = get_cache_client()
        self.db = get_db_client()

    def save_itinerary_to_db(self, itinerary_data: dict, name: str, user_id: Optional[str] = None) -> str:
        """
        Save itinerary to the persistent database.

        Args:
            itinerary_data: The itinerary data (JSON).
            name: A name for the itinerary.
            user_id: The ID of the user saving the itinerary (optional).

        Returns:
            The UUID of the saved itinerary.
        """
        try:
            # The 'data' key in the insert dictionary must match the column name in your 'itineraries' table.
            # The itinerary_data should be a dictionary that can be serialized to JSON.
            response = self.db.from_('itineraries').insert({
                'user_id': user_id,
                'name': name,
                'data': json.dumps(itinerary_data) # Ensure data is a JSON string for the JSONB column
            }).execute()

            if response.data:
                saved_id = response.data[0]['id']
                return saved_id
            else:
                # Supabase insert might not return data on success depending on configuration,
                # but if there's no error, it's likely saved.
                # However, if an ID is needed, this part is crucial.
                # Let's assume for now an error is raised on failure.
                raise Exception("Failed to save itinerary to database, no data returned.")
        except Exception as e:
            print(f"Error saving to Supabase: {e}")
            raise

    def load_itinerary_from_db(self, itinerary_id: str) -> Optional[Dict]:
        """
        Load an itinerary from the persistent database.

        Args:
            itinerary_id: The UUID of the itinerary to load.

        Returns:
            The itinerary data as a dictionary, or None if not found.
        """
        try:
            response = self.db.table('itineraries').select('data').eq('id', itinerary_id).single().execute()
            if response.data and 'data' in response.data:
                # The 'data' column is JSONB, which supabase-py should deserialize into a dict.
                # If it's a string, we parse it.
                db_data = response.data['data']
                if isinstance(db_data, str):
                    return json.loads(db_data)
                return db_data
            return None
        except Exception as e:
            print(f"Error loading from Supabase: {e}")
            return None

    def share_itinerary_to_cache(self, itinerary_data: dict, ttl_seconds: int = 86400) -> str:
        """
        Save itinerary to database for temporary sharing.
        Falls back to database if Redis cache is not available.

        Args:
            itinerary_data: Itinerary data to save.
            ttl_seconds: Time-to-live in seconds.

        Returns:
            A unique share ID.
        """
        import uuid
        from datetime import datetime, timedelta
        
        share_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        
        # Try Redis first if available
        if self.cache:
            try:
                self.cache.set(f"share:{share_id}", json.dumps(itinerary_data), ex=ttl_seconds)
                print(f"Shared itinerary cached in Redis: {share_id}")
                return share_id
            except Exception as e:
                print(f"Redis cache failed, falling back to database: {e}")
        
        # Fallback to database storage
        try:
            # Generate a shorter, more user-friendly share_id
            short_share_id = str(uuid.uuid4())[:8]
            
            self.db.from_('shared_itineraries').insert({
                'share_id': short_share_id,
                'data': json.dumps(itinerary_data),
                'expires_at': expires_at.isoformat()
            }).execute()
            
            print(f"Shared itinerary stored in database: {short_share_id}")
            return short_share_id
            
        except Exception as e:
            print(f"Database storage for sharing also failed: {e}")
            # Return share_id anyway, but sharing won't work
            return share_id

    def load_itinerary_from_cache(self, share_id: str) -> Optional[Dict]:
        """
        Load a shared itinerary from Redis cache or database.

        Args:
            share_id: The unique ID for the shared itinerary.

        Returns:
            The itinerary data as a dictionary, or None if not found.
        """
        # Try Redis first if available
        if self.cache:
            try:
                data = self.cache.get(f"share:{share_id}")
                if data:
                    return json.loads(data)
            except Exception as e:
                print(f"Redis cache read failed: {e}")
        
        # Try database
        try:
            from datetime import datetime
            
            response = self.db.from_('shared_itineraries').select('data').eq('share_id', share_id).single().execute()
            
            if response.data and 'data' in response.data:
                db_data = response.data['data']
                if isinstance(db_data, str):
                    return json.loads(db_data)
                return db_data
                
        except Exception as e:
            print(f"Database read for shared itinerary failed: {e}")
            
        return None
