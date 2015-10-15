from contextlib import contextmanager
import bz2
from astropy.io import fits
import time

from ngts_transmission.logs import logger


@contextmanager
def open_fits(fname):
    if '.bz2' in fname:
        with bz2.BZ2File(fname) as uncompressed:
            with fits.open(uncompressed) as infile:
                yield infile
    else:
        with fits.open(fname) as infile:
            yield infile


@contextmanager
def time_context(message=None):
    start = time.time()
    yield
    end = time.time()
    if message is None:
        logger.debug('Time taken: %s seconds', end - start)
    else:
        logger.debug(message, end - start)
