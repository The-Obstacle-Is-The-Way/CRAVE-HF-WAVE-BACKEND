"""
app/api/dependencies.py
-------------------------
Defines core dependencies and initialization routines for the CRAVE Trinity API.

This module sets up the database connection using SQLAlchemy and exposes
a helper function (`init_db`) to test connectivity or run initialization logic.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Read the database URL from the environment, with a fallback for local development.
DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql://postgres:password@db:5432/crave_db")

# Create the SQLAlchemy engine.
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Initialize the database connection.
    
    This function attempts to connect to the database and can be extended
    to include migration or seeding logic. A successful connection confirms
    that the database is up and running.
    """
    try:
        with engine.connect() as connection:
            # Execute a simple query to validate the connection.
            connection.execute("SELECT 1")
        print("Database connection established successfully.")
    except Exception as e:
        print("Error establishing database connection:", e)