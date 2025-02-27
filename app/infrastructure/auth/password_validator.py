# app/infrastructure/auth/password_validator.py

"""
Password validation service implementing a strategy pattern for different validation rules.
"""

import re
from abc import ABC, abstractmethod
from typing import List, Optional


class PasswordRule(ABC):
    """
    Abstract base class for password validation rules.
    Strategy pattern: Each concrete rule implements a specific validation strategy.
    """
    
    @abstractmethod
    def validate(self, password: str) -> bool:
        """Validate the password against this rule."""
        pass
    
    @abstractmethod
    def get_error_message(self) -> str:
        """Get the error message for this rule."""
        pass


class LengthRule(PasswordRule):
    """Rule for minimum password length."""
    
    def __init__(self, min_length: int = 8):
        self.min_length = min_length
    
    def validate(self, password: str) -> bool:
        return len(password) >= self.min_length
    
    def get_error_message(self) -> str:
        return f"Password must be at least {self.min_length} characters long."


class UppercaseRule(PasswordRule):
    """Rule requiring at least one uppercase letter."""
    
    def validate(self, password: str) -> bool:
        return bool(re.search(r'[A-Z]', password))
    
    def get_error_message(self) -> str:
        return "Password must contain at least one uppercase letter."


class DigitRule(PasswordRule):
    """Rule requiring at least one digit."""
    
    def validate(self, password: str) -> bool:
        return bool(re.search(r'\d', password))
    
    def get_error_message(self) -> str:
        return "Password must contain at least one digit."


class SpecialCharRule(PasswordRule):
    """Rule requiring at least one special character."""
    
    def validate(self, password: str) -> bool:
        return bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    def get_error_message(self) -> str:
        return "Password must contain at least one special character."


class PasswordValidator:
    """
    Password validator that composes multiple validation rules.
    Composite pattern: Treats individual rules and collections of rules uniformly.
    """
    
    def __init__(self, rules: Optional[List[PasswordRule]] = None):
        """
        Initialize with optional custom rules or default rules.
        
        Args:
            rules: List of password validation rules
        """
        self.rules = rules or [
            LengthRule(8),
            UppercaseRule(),
            DigitRule(),
            SpecialCharRule()
        ]
    
    def validate(self, password: str) -> List[str]:
        """
        Validate a password against all rules.
        
        Args:
            password: The password to validate
            
        Returns:
            List of error messages for failed rules (empty if all passed)
        """
        errors = []
        for rule in self.rules:
            if not rule.validate(password):
                errors.append(rule.get_error_message())
        return errors