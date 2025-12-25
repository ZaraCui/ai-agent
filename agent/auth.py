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
            # Sign up with email confirmation disabled for development
            response = self.db.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                "email_confirm": True
                }
            })
            
            # Create a corresponding entry in our public 'users' table
            if response.user:
                try:
                    # Check if user already exists in our users table
                    existing = self.db.from_('users').select('id').eq('id', response.user.id).execute()
                    if not existing.data:
                        self.db.from_('users').insert({
                            'id': response.user.id, 
                            'email': email
                        }).execute()
                        print(f"Created user record for {email}")
                    else:
                        print(f"User record already exists for {email}")
                except Exception as insert_error:
                    print(f"Warning: Failed to insert user into users table: {insert_error}")
            
            return {"status": "success", "data": response}
        except AuthApiError as e:
            error_msg = str(e.message) if hasattr(e, 'message') else str(e)
            print(f"Auth API Error during signup: {error_msg}")
            
            # Handle common signup errors
            if "User already registered" in error_msg or "already registered" in error_msg:
                return {"status": "error", "reason": "An account with this email already exists. Please try signing in instead."}
            elif "Password should be at least" in error_msg:
                return {"status": "error", "reason": "Password must be at least 6 characters long."}
            elif "Invalid email" in error_msg:
                return {"status": "error", "reason": "Please enter a valid email address."}
            else:
                return {"status": "error", "reason": f"Sign up failed: {error_msg}"}
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
            
            # Log successful sign in
            print(f"User signed in successfully: {email}")
            return {"status": "success", "data": response}
            
        except AuthApiError as e:
            error_msg = str(e.message) if hasattr(e, 'message') else str(e)
            print(f"Auth API Error during signin: {error_msg}")
            
            # Handle common login errors with user-friendly messages
            if "Invalid login credentials" in error_msg:
                return {"status": "error", "reason": "Invalid email or password. Please check your credentials and try again."}
            elif "Email not confirmed" in error_msg:
                return {"status": "error", "reason": "Please check your email and confirm your account before signing in."}
            elif "Too many requests" in error_msg:
                return {"status": "error", "reason": "Too many login attempts. Please wait a moment before trying again."}
            else:
                return {"status": "error", "reason": f"Sign in failed: {error_msg}"}
        except Exception as e:
            print(f"Unexpected error during signin: {str(e)}")
            return {"status": "error", "reason": f"An unexpected error occurred: {str(e)}"}

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
