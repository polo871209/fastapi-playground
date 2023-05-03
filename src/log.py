import logging

from logtail import LogtailHandler

from .config import env

# Set up Logtail handler with the token
logtail_handler = LogtailHandler(source_token=env.SOURCE_TOKEN)
logtail_handler.setLevel(logging.INFO)

# Uvicorn's logger
uvicorn_log = logging.getLogger('gunicorn')
uvicorn_log.addHandler(logtail_handler)

# Uvicorn's access logger
uvicorn_access_log = logging.getLogger('gunicorn.access')
uvicorn_access_log.addHandler(logtail_handler)

# Custom logger
logger = logging.getLogger(__name__)
logger.addHandler(logtail_handler)

# Configure the logging level
uvicorn_log.setLevel(logging.INFO)
uvicorn_access_log.setLevel(logging.INFO)
logger.setLevel(logging.INFO)
