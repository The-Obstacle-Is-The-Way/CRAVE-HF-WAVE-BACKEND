# File: app/infrastructure/auth/oauth_provider.py

"""
Placeholder for 3rd-party OAuth integrations (Google, Apple, etc.)
Currently empty. In the future, you could implement:
  1. Google OAuth 2.0 (client_id, client_secret, callback)
  2. Apple Sign-In
  3. Refresh tokens from the provider
And then unify that with your local user DB.
"""

class OAuthProvider:
    def __init__(self):
        pass
    
    def google_sign_in(self, authorization_code: str):
        """
        Exchange auth code for tokens, get user profile, etc.
        Return user data or create a local user if new.
        """
        raise NotImplementedError("Google sign-in not implemented yet.")
    
    # Add more methods for Apple, Facebook, etc. as needed