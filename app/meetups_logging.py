import logging
import logging.config

from config.logging import LOGGING

# Create logger
logging.config.dictConfig(LOGGING)
logger = logging.getLogger("fastapi")
