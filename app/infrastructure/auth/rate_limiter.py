# app/infrastructure/auth/rate_limiter.py

"""
Rate limiter for API endpoints to prevent brute force attacks.
Follows the Single Responsibility Principle by focusing solely on rate limiting.
"""

import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status

class RateLimiter:
    """
    Simple in-memory rate limiter implementing the Singleton pattern.
    In production, consider using Redis or another distributed cache.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RateLimiter, cls).__new__(cls)
            cls._instance.ip_cache: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, 0))
            cls._instance.username_cache: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, 0))
        return cls._instance
    
    def check_request(self, request: Request, username: str = None, max_requests: int = 5, window_seconds: int = 60) -> None:
        """
        Check if a request exceeds rate limits.
        
        Args:
            request: The FastAPI request object
            username: Optional username to track (for login attempts)
            max_requests: Maximum number of requests allowed in the time window
            window_seconds: Time window in seconds
            
        Raises:
            HTTPException: If rate limit is exceeded
        """
        client_ip = request.client.host
        current_time = time.time()
        
        # Check IP-based rate limit
        requests, timestamp = self.ip_cache[client_ip]
        
        # Reset counter if window has passed
        if current_time - timestamp > window_seconds:
            self.ip_cache[client_ip] = (1, current_time)
        else:
            # Increment counter and update timestamp
            requests += 1
            if requests > max_requests:
                # Apply exponential backoff for repeat offenders
                retry_after = min(window_seconds * (requests - max_requests), 3600)  # Max 1 hour
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                    headers={"Retry-After": str(retry_after)}
                )
            self.ip_cache[client_ip] = (requests, timestamp)
        
        # Apply stricter rate limiting for login attempts (username-based)
        if username:
            requests, timestamp = self.username_cache[username]
            
            if current_time - timestamp > window_seconds:
                self.username_cache[username] = (1, current_time)
            else:
                requests += 1
                if requests > max_requests:
                    # Be vague about the reason to prevent username enumeration
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Too many requests. Please try again later.",
                        headers={"Retry-After": str(window_seconds)}
                    )
                self.username_cache[username] = (requests, timestamp)