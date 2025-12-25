from agent.db import get_db_client, CustomSupabaseClient
from postgrest import APIResponse as PostgrestAPIResponse

class UserProfileService:
    """Manages user profiles and preferences."""

    def __init__(self):
        """Initialize the user profile service with a database client."""
        self.db: CustomSupabaseClient = get_db_client()

    def get_user_preferences(self, user_id: str) -> dict:
        """
        Retrieves user preferences from the database.

        Args:
            user_id: The ID of the user.

        Returns:
            A dictionary containing user preferences or an error message.
        """
        try:
            response: PostgrestAPIResponse = self.db.from_('user_preferences').select('preferences').eq('user_id', user_id).execute()
            if response.data:
                return {"status": "success", "preferences": response.data[0]['preferences']}
            return {"status": "error", "reason": "User preferences not found."}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    def update_user_preferences(self, user_id: str, new_preferences: dict) -> dict:
        """
        Updates user preferences in the database.

        Args:
            user_id: The ID of the user.
            new_preferences: A dictionary containing the new preferences.

        Returns:
            A dictionary indicating success or failure.
        """
        try:
            # Check if preferences exist for the user
            existing_prefs_response: PostgrestAPIResponse = self.db.from_('user_preferences').select('id').eq('user_id', user_id).execute()

            if existing_prefs_response.data:
                # Update existing preferences
                response: PostgrestAPIResponse = self.db.from_('user_preferences').update({'preferences': new_preferences}).eq('user_id', user_id).execute()
            else:
                # Insert new preferences
                response: PostgrestAPIResponse = self.db.from_('user_preferences').insert({'user_id': user_id, 'preferences': new_preferences}).execute()

            if response.data:
                return {"status": "success", "message": "User preferences updated successfully."}
            return {"status": "error", "reason": "Failed to update user preferences."}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
