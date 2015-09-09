#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse
import logging
from astropy.io import fits
import pymysql
from contextlib import contextmanager
from collections import namedtuple
import tempfile
import subprocess as sp

logging.basicConfig(level='INFO', format='%(levelname)7s %(message)s')
logger = logging.getLogger(__name__)

TransmissionCatalogueEntry = namedtuple('TransmissionCatalogueEntry', [
    'image_id', 'x', 'y', 'inc_prescan', 'flux'
])


def image_has_prescan(fname):
    return fits.getdata(fname).shape == (2048, 2088)


def source_detect(fname, n_pixels=3, threshold=7):
    with tempfile.NamedTemporaryFile(suffix='.fits') as tfile:
        cmd = ['imcore', fname, 'noconf', tfile.name, n_pixels, threshold,]
        sp.check_call(list(map(str, cmd)))
        tfile.seek(0)

        with fits.open(tfile.name) as infile:
            return infile[1].data


def extract_from_file(fname):
    pass


@contextmanager
def connect_to_database(args):
    with pymysql.connect(user=args.db_user,
                         unix_socket=args.db_socket,
                         db=args.db_name) as cursor:
        yield cursor


def upload_info(extracted_data, cursor):
    pass


def main(args):
    if args.verbose:
        logger.setLevel('DEBUG')
    logger.debug(args)

    file_info = extract_from_file(args.refimage)
    with connect_to_database(args) as cursor:
        upload_info(file_info, cursor)


if __name__ == '__main__':
    description = '''
    Given an autoguider reference frame, extract a source catalogue, filter the
    object list and store in a file
    '''

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('refimage')
    parser.add_argument('--db-socket',
                        required=False,
                        default='/var/lib/mysql/mysql.sock')
    parser.add_argument('--db-user', required=False, default='ops')
    parser.add_argument('--db-name', required=False, default='ngts_ops')
    main(parser.parse_args())
