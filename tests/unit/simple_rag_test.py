#!/usr/bin/env python3
"""
Simple script to test the RAG system without additional dependencies.
"""

import json
import urllib.request
import urllib.error
import urllib.parse
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "https://crave-trinity-backend-production.up.railway.app"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyYW5kb211c2VyMTIzQHJhbmRvbTEyMy5jb20iLCJ1c2VyX2lkIjoxNCwiZXhwIjoxNzQwNjc0MDU3LCJpYXQiOjE3NDA2NzA0NTcsImp0aSI6ImJmYzdmM2MyLTdiNTItNGJmNC04MTYzLTk4MTJmM2U1NzkxZiIsInR5cGUiOiJhY2Nlc3MifQ.g96RH40RE3zuQYcP2lTaIxvpXtHXodGWgR5xtQou4x0"  # Fixed token string

def make_request(url, method="GET", data=None, headers=None):
    """Make an HTTP request and return the response."""
    if headers is None:
        headers = {}
    
    headers["Authorization"] = f"Bearer {TOKEN}"
    
    if data is not None:
        data = json.dumps(data).encode('utf-8')
        headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            return {
                "status": response.status,
                "body": json.loads(response_data) if response_data else {}
            }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: {error_body}")
        return {
            "status": e.code,
            "error": error_body
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "status": 500,
            "error": str(e)
        }

def test_personas():
    """Test listing available personas."""
    print("\n--- Testing Available Personas ---")
    
    url = f"{BASE_URL}/api/ai/personas"
    response = make_request(url)
    
    print(f"Status: {response.get('status')}")
    if response.get("status") == 200:
        personas = response.get("body", {}).get("personas", [])
        print(f"Available personas: {personas}")
        return personas
    else:
        print(f"Error: {response.get('error', 'Unknown error')}")
        return []

def test_ai_patterns():
    """Test AI pattern detection."""
    print("\n--- Testing AI Pattern Detection ---")
    
    # Use your user ID here - updated to 14 from the token
    user_id = 14
    
    url = f"{BASE_URL}/api/ai/patterns?user_id={user_id}"
    response = make_request(url)
    
    print(f"Status: {response.get('status')}")
    if response.get("status") == 200:
        patterns = response.get("body", {}).get("patterns", {})
        print(f"Detected patterns: {json.dumps(patterns, indent=2)}")
    else:
        print(f"Error: {response.get('error', 'Unknown error')}")

def list_cravings():
    """List cravings for the user."""
    print("\n--- Listing Cravings ---")
    
    user_id = 14
    # Note the correct path with duplicated "cravings/cravings"
    url = f"{BASE_URL}/api/cravings/cravings?user_id={user_id}"
    
    response = make_request(url)
    
    print(f"Status: {response.get('status')}")
    if response.get("status") == 200:
        cravings = response.get("body", {})
        print(f"Cravings: {json.dumps(cravings, indent=2)}")
        return cravings
    else:
        print(f"Error: {response.get('error', 'Unknown error')}")
        return None

def create_test_craving():
    """Create a test craving to have some data."""
    print("\n--- Creating Test Craving ---")
    
    # Fix the URL path - note the duplicated "cravings/cravings"
    url = f"{BASE_URL}/api/cravings/cravings"
    user_id = 14
    
    data = {
        "user_id": user_id,
        "description": f"Test chocolate craving at {datetime.now().strftime('%H:%M')}",
        "intensity": 8
    }
    
    response = make_request(url, method="POST", data=data)
    
    print(f"Status: {response.get('status')}")
    if response.get("status") == 200 or response.get("status") == 201:
        craving = response.get("body", {})
        print(f"Created craving: {json.dumps(craving, indent=2)}")
        return craving
    else:
        print(f"Error: {response.get('error', 'Unknown error')}")
        return None

def test_rag_query(query, persona=None):
    """Test a RAG query."""
    print(f"\n--- Testing RAG Query: '{query}' ---")
    
    url = f"{BASE_URL}/api/ai/rag/insights"
    data = {
        "query": query,
        "top_k": 3
    }
    
    if persona:
        data["persona"] = persona
    
    start_time = time.time()
    response = make_request(url, method="POST", data=data)
    elapsed = time.time() - start_time
    
    print(f"Status: {response.get('status')}")
    print(f"Time: {elapsed:.2f} seconds")
    
    if response.get("status") == 200:
        answer = response.get("body", {}).get("answer", "")
        print("\nAnswer:")
        print(f"{answer}\n")
        return answer
    else:
        print(f"Error: {response.get('error', 'Unknown error')}")
        return None

def main():
    """Run the test script."""
    print("=== CRAVE Trinity RAG Test ===")
    print(f"Base URL: {BASE_URL}")
    print(f"Using token: {TOKEN[:10]}...")
    
    # List existing cravings first
    list_cravings()
    
    # Create some test data
    create_test_craving()
    
    # Test personas
    personas = test_personas()
    
    # Test AI patterns
    test_ai_patterns()
    
    # Test RAG queries
    test_rag_query("Why do I crave chocolate?")
    
    # Test with a more specific query
    test_rag_query("What time of day do I usually have cravings?")
    
    # Test with personas if available
    if personas and len(personas) > 0:
        test_rag_query("How can I handle my cravings?", personas[0])

if __name__ == "__main__":
    main()
