import os
import sys

from loguru import logger

from config import get_settings

settings = get_settings()

logger.remove()

message_format = "\
<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> \
<level>{level: <8}</level> \
<cyan>{name}</cyan>\
<cyan>:{line} </cyan>\
- <level>{message}</level>\
"
logger.level("AGENT", no=7, color="<magenta><bold>")

level = settings.log_level.upper()
filename = settings.log_filename
logger.add(sys.stderr, format=message_format, level=level)
logfile_path = os.path.join(settings.log_dir, filename)
logger.add(logfile_path, format=message_format, rotation="5MB", level=level)
