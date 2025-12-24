"""
Authentication Service
Handles user sign-up, sign-in, and session management using Supabase Auth.
"""
from agent.db import get_db_client
from supabase import Client
from gotrue.errors import AuthApiError

class AuthService:
    """Manages user authentication."""

    def __init__(self):
        """Initialize the authentication service with a database client."""
        self.db: Client = get_db_client()

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
            response = self.db.auth.sign_up({
                "email": email,
                "password": password,
            })
            # The user is created in the 'auth.users' table by Supabase.
            # We also need to create a corresponding entry in our public 'users' table.
            if response.user:
                self.db.table('users').insert({'id': response.user.id, 'email': email}).execute()
            return response
        except AuthApiError as e:
            return {"error": e.message}
        except Exception as e:
            return {"error": str(e)}

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
            return response
        except AuthApiError as e:
            return {"error": e.message}
        except Exception as e:
            return {"error": str(e)}

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
