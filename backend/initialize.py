"""
Initialization script for the EVrouter backend.
This script initializes the database with sample data.
"""

import logging
import time
import sys
from app.db.neo4j import db
from app.db.init_db import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def main():
    """Main initialization function"""
    logger.info("Starting database initialization")
    
    # Wait for Neo4j to be ready
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Try to connect to Neo4j
            with db.get_session() as session:
                result = session.run("RETURN 1 as n")
                result.single()
                logger.info("Successfully connected to Neo4j")
                break
        except Exception as e:
            retry_count += 1
            logger.warning(f"Neo4j not ready yet. Retrying in 2 seconds... ({retry_count}/{max_retries})")
            time.sleep(2)
    
    if retry_count == max_retries:
        logger.error("Failed to connect to Neo4j after maximum retries")
        sys.exit(1)
    
    # Initialize the database
    try:
        init_db()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
