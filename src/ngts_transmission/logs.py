import logging
from logging.handlers import RotatingFileHandler
from socket import gethostname

if 'aux' in gethostname():
    log_filename = '/usr/local/cron/logs/transmission.log'
else:
    log_filename = '/tmp/transmission.log'

# Maximum file size: 10MB
maxBytes = 10 * 1024 * 1024

logger = logging.getLogger('ngtransmission')
logger.setLevel(logging.DEBUG)

fh = RotatingFileHandler(log_filename,
                         mode='a',
                         maxBytes=maxBytes,
                         backupCount=5)
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s] %(levelname)7s %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)
