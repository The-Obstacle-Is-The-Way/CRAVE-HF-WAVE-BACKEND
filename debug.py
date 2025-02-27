# debug.py
# Add this file to your repository to debug environment variables
import os
import sys

def print_env_vars():
    """Print all environment variables for debugging."""
    print("==== ENVIRONMENT VARIABLES ====")
    for key, value in sorted(os.environ.items()):
        # Mask sensitive information
        if any(secret in key.lower() for secret in ['key', 'password', 'secret', 'token']):
            masked_value = value[:4] + '****' if value else 'None'
            print(f"{key}: {masked_value}")
        else:
            print(f"{key}: {value}")
    print("===============================")

if __name__ == "__main__":
    print_env_vars()
