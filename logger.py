import logging
import os

# Get the logging level from the environment variable, default to INFO
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

# Configure logging
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),  # Default to INFO if LOG_LEVEL is invalid
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Export the logger instance
logger = logging.getLogger()