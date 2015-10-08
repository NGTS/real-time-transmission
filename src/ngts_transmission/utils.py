from contextlib import contextmanager
import bz2
from astropy.io import fits
import logging

logging.basicConfig(level='INFO', format='%(levelname)7s %(message)s')
logger = logging.getLogger(__name__)


@contextmanager
def open_fits(fname):
    if '.bz2' in fname:
        with bz2.BZ2File(fname) as uncompressed:
            with fits.open(uncompressed) as infile:
                yield infile
    else:
        with fits.open(fname) as infile:
            yield infile
