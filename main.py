################################################################################
#                                                                              
#  "I understand there's a guy inside me who wants to lay in bed,              
#   smoke weed 🍃 all day, and watch cartoons and old movies.                     
#   My whole life is a series of stratagems to avoid, and outwit, that guy."  
#                                                                              
#   - Anthony Bourdain                                                                                                                         
#                                                                              
################################################################################
#
#
#
"""
main.py
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