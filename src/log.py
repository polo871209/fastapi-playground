import logging

from logtail import LogtailHandler

from .config import env
handler = LogtailHandler(source_token=env.SOURCE_TOKEN)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.handlers = []
logger.addHandler(handler)
