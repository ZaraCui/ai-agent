import os
import requests
from typing import Dict, Any, Optional, List
from agent.cache import cache, cache_key_for_places
from agent.logging_config import setup_logging

logger = setup_logging(__name__, log_file='logs/places_api.log')

class PlacesApiService:
    """Service to interact with the Google Places API."""

    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            logger.error("GOOGLE_PLACES_API_KEY environment variable not set.")
            raise ValueError("Google Places API Key not configured.")
        self.base_url = "https://maps.googleapis.com/maps/api/place/"

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Helper to make a request to the Google Places API."""
        params['key'] = self.api_key
        url = f"{self.base_url}{endpoint}/json"
        
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {endpoint}: {e.response.status_code} - {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred for {endpoint}: {e}")
            return None

    def search_place_id(self, query: str, fields: List[str] = ['place_id']) -> Optional[str]:
        """
        Searches for a place and returns its place_id.
        """
        cache_key = cache_key_for_places(f"search_id_{query}")
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.debug(f"Cache hit for place ID search: {query}")
            return cached_result

        params = {
            "query": query,
            "fields": ",".join(fields)
        }
        response_data = self._make_request("findplacefromtext", params)

        if response_data and response_data.get('status') == 'OK' and response_data.get('candidates'):
            place_id = response_data['candidates'][0]['place_id']
            cache.set(cache_key, place_id, ttl=86400) # Cache for 24 hours
            return place_id
        elif response_data and response_data.get('status') == 'ZERO_RESULTS':
            logger.info(f"No place found for query: {query}")
        elif response_data:
            logger.warning(f"Places API search failed for query '{query}': {response_data.get('status')}")
        return None

    def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches detailed information for a given place_id.
        """
        cache_key = cache_key_for_places(f"details_{place_id}")
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.debug(f"Cache hit for place details: {place_id}")
            return cached_result

        fields = [
            "name", "formatted_address", "geometry", "opening_hours",
            "rating", "user_ratings_total", "photos", "types", "website"
        ]
        params = {
            "place_id": place_id,
            "fields": ",".join(fields)
        }
        response_data = self._make_request("details", params)

        if response_data and response_data.get('status') == 'OK' and response_data.get('result'):
            place_details = response_data['result']
            cache.set(cache_key, place_details, ttl=43200) # Cache for 12 hours
            return place_details
        elif response_data:
            logger.warning(f"Places API details failed for place_id '{place_id}': {response_data.get('status')}")
        return None

    def get_place_photo_url(self, photo_reference: str, max_width: int = 400) -> Optional[str]:
        """
        Constructs a URL for a place photo.
        """
        if not photo_reference:
            return None
            
        params = {
            "maxwidth": max_width,
            "photoreference": photo_reference,
            "key": self.api_key
        }
        # Photo requests don't return JSON, they redirect to the image itself.
        # We just need to construct the URL.
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}photo?{query_string}"
