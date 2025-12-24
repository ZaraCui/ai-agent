"""
Authentication Service
Handles user sign-up, sign-in, and session management using Supabase Auth.
"""
from agent.db import get_db_client, CustomSupabaseClient
from gotrue.errors import AuthApiError

class AuthService:
    """Manages user authentication."""

    def __init__(self):
        """Initialize the authentication service with a database client."""
        self.db: CustomSupabaseClient = get_db_client()

    def sign_up(self, email: str, password: str) -> dict:
        """
        Signs up a new user.

        Args:
            email: The user's email address.
            password: The user's chosen password.

        Returns:
            A dictionary containing the user data and session, or an error.
        """
        try:
            # For development, we can disable email confirmation
            response = self.db.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "email_confirm": False  # Disable email confirmation for development
                }
            })
            # The user is created in the 'auth.users' table by Supabase.
            # We also need to create a corresponding entry in our public 'users' table.
            if response.user:
                try:
                    self.db.from_('users').insert({'id': response.user.id, 'email': email}).execute()
                except Exception as insert_error:
                    # User table insertion failed, but signup was successful
                    print(f"Warning: Failed to insert user into users table: {insert_error}")
            
            return {"status": "success", "data": response}
        except AuthApiError as e:
            # Handle specific Supabase auth errors
            error_msg = e.message
            if "Error sending confirmation email" in error_msg:
                # For development, we can suggest that email confirmation is disabled
                return {"status": "success", "data": response if 'response' in locals() else None, 
                        "warning": "Account created but email confirmation failed. You can still sign in."}
            return {"status": "error", "reason": error_msg}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    def sign_in(self, email: str, password: str) -> dict:
        """
        Signs in an existing user.

        Args:
            email: The user's email address.
            password: The user's password.

        Returns:
            A dictionary containing the user's session data, or an error.
        """
        try:
            response = self.db.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {"status": "success", "data": response}
        except AuthApiError as e:
            return {"status": "error", "reason": e.message}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    def get_user_from_token(self, jwt: str):
        """
        Retrieves user information from a JWT.

        Args:
            jwt: The JSON Web Token from the request header.

        Returns:
            The user object, or an error.
        """
        try:
            response = self.db.auth.get_user(jwt)
            return response
        except AuthApiError as e:
            return {"error": e.message}
        except Exception as e:
            return {"error": str(e)}
