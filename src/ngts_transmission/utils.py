from contextlib import contextmanager
import bz2
from astropy.io import fits
import time

from ngts_transmission.logs import logger


class NoAutoguider(Exception):

    def __init__(self):
        super(NoAutoguider, self).__init__('Image is not autoguided')


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


def get_refcat_id(filename):
    logger.debug('Extracting reference image id from {filename}'.format(
        filename=filename))
    with open_fits(filename) as infile:
        header = infile[0].header

    try:
        return header['agrefimg']
    except KeyError:
        logger.exception('''No autoguider reference image found in file %s.
                            Assuming this is ok and continuing.''', filename)
        raise NoAutoguider
