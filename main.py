"""
Directory Structure (excerpt):
.
├── main.py                <-- This file
├── app
│   └── api
│       └── main.py        <-- API entry point
│       └── endpoints
│           ├── health.py
│           ├── user_queries.py
│           ├── craving_logs.py
│           ├── ai_endpoints.py
│           └── search_cravings.py
...

Description:
This is the root-level entry point for the CRAVE Trinity Backend.
It imports the FastAPI application from app/api/main.py and runs it using uvicorn.
"""

import uvicorn
from app.api.main import app

if __name__ == "__main__":
    # Run the app on 0.0.0.0:8000 with auto-reload enabled for development.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)