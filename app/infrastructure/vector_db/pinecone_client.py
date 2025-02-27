# app/infrastructure/vector_db/pinecone_client.py
"""
Client for interacting with Pinecone Vector Database.

This module provides functions to initialize the Pinecone client and
get a reference to the specified index.
"""

from pinecone import Pinecone, ServerlessSpec, PodSpec
from app.config.settings import settings
import os
import logging

logger = logging.getLogger(__name__)

def init_pinecone():
    """
    Initialize the Pinecone client with API key from settings.
    
    Returns:
        Pinecone: Initialized Pinecone client
    """
    try:
        # Get API key from settings, which uses environment variables
        api_key = settings.PINECONE_API_KEY
        
        if not api_key:
            logger.warning("No Pinecone API key found. Vector searches will not work.")
            return None
            
        # Initialize Pinecone client
        pc = Pinecone(api_key=api_key)
        logger.info("Pinecone client initialized successfully")
        return pc
    except Exception as e:
        logger.error(f"Error initializing Pinecone client: {e}")
        # Continue execution even if Pinecone fails
        return None

# Initialize Pinecone client
pc = init_pinecone()

def get_pinecone_index(index_name=None):
    """
    Get a reference to the specified Pinecone index.
    
    Args:
        index_name (str, optional): Name of the index to use.
            Defaults to value from settings.
            
    Returns:
        Index: Pinecone index object
    """
    if pc is None:
        logger.warning("Cannot get index: Pinecone client is not initialized")
        return None
        
    try:
        # Use provided index name or get from settings
        idx_name = index_name or settings.PINECONE_INDEX_NAME
        
        # List existing indexes
        existing_indexes = [index.name for index in pc.list_indexes()]
        
        # Check if the index exists
        if idx_name not in existing_indexes:
            logger.info(f"Creating new Pinecone index: {idx_name}")
            # Create the index - using serverless for better scalability
            pc.create_index(
                name=idx_name,
                dimension=1536,  # OpenAI embeddings dimension
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        
        # Return the index
        return pc.Index(idx_name)
    except Exception as e:
        logger.error(f"Error getting Pinecone index: {e}")
        return None