# app/infrastructure/auth/token_blacklist.py
"""
Token blacklist to invalidate tokens before they expire.
Uses a simple in-memory store - for production, use Redis or a database.
"""

import time
from typing import Dict, Set
import threading


class TokenBlacklist:
    """
    Blacklist for revoked tokens implementing the Singleton pattern.
    For production, use Redis or a database-backed solution.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TokenBlacklist, cls).__new__(cls)
                cls._instance.blacklisted_tokens: Set[str] = set()
                cls._instance.user_logout_times: Dict[int, float] = {}
                cls._instance._last_cleanup = time.time()
            return cls._instance
    
    def add(self, token_jti: str) -> None:
        """
        Add a token to the blacklist.
        
        Args:
            token_jti: The JWT ID to blacklist
        """
        self.blacklisted_tokens.add(token_jti)
        self._cleanup()
    
    def logout_user(self, user_id: int) -> None:
        """
        Log out a user by recording the logout time.
        All tokens issued before this time should be considered invalid.
        
        Args:
            user_id: The user ID to log out
        """
        self.user_logout_times[user_id] = time.time()
    
    def is_blacklisted(self, token_jti: str) -> bool:
        """
        Check if a token is blacklisted.
        
        Args:
            token_jti: The JWT ID to check
            
        Returns:
            bool: True if blacklisted, False otherwise
        """
        return token_jti in self.blacklisted_tokens
    
    def is_user_logged_out(self, user_id: int, token_iat: float) -> bool:
        """
        Check if a token was issued before the user logged out.
        
        Args:
            user_id: The user ID
            token_iat: The token's issued-at timestamp
            
        Returns:
            bool: True if the token was issued before logout, False otherwise
        """
        logout_time = self.user_logout_times.get(user_id)
        if logout_time and token_iat < logout_time:
            return True
        return False
    
    def _cleanup(self) -> None:
        """
        Periodically clean up the blacklist to remove old entries.
        In a production implementation, this would be done by a background task.
        """
        now = time.time()
        # Only clean up at most once per hour to avoid overhead
        if now - self._last_cleanup < 3600:
            return
            
        # In a real implementation, you would remove expired tokens
        # based on their expiration time
        self._last_cleanup = now