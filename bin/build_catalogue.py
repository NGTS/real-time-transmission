#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse
import logging
from astropy.io import fits
import pymysql

logging.basicConfig(level='INFO', format='%(levelname)7s %(message)s')
logger = logging.getLogger(__name__)


def main(args):
    if args.verbose:
        logger.setLevel('DEBUG')
    logger.debug(args)


if __name__ == '__main__':
    description = '''
    Given an autoguider reference frame, extract a source catalogue, filter the
    object list and store in a file
    '''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('refimage')
    main(parser.parse_args())
