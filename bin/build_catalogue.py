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
from joblib import Memory
import numpy as np

logging.basicConfig(level='INFO', format='%(levelname)7s %(message)s')
logger = logging.getLogger(__name__)

TransmissionCatalogueEntry = namedtuple('TransmissionCatalogueEntry', [
    'image_id',
    'x_coordinate',
    'y_coordinate',
    'inc_prescan',
    'flux_adu',
])

memory = Memory(cachedir='.tmp')


def image_has_prescan(fname):
    return fits.getdata(fname).shape == (2048, 2088)


@memory.cache
def source_detect(fname, n_pixels=3, threshold=7):
    with tempfile.NamedTemporaryFile(suffix='.fits') as tfile:
        cmd = ['imcore', fname, 'noconf', tfile.name, n_pixels, threshold,]
        sp.check_call(list(map(str, cmd)))
        tfile.seek(0)

        with fits.open(tfile.name) as infile:
            return infile[1].data


def filter_source_table(source_table):
    return source_table


def extract_from_file(fname):
    with fits.open(fname) as infile:
        header = infile[0].header

    image_id = header['image_id']

    source_table = source_detect(fname)
    filtered_source_table = filter_source_table(source_table)
    inc_prescan = image_has_prescan(fname)
    for row in filtered_source_table:
        yield TransmissionCatalogueEntry(
            image_id=int(image_id),
            x_coordinate=float(row['X_coordinate']),
            y_coordinate=float(row['Y_coordinate']),
            inc_prescan=inc_prescan,
            flux_adu=float(row['Aper_flux_3']))


@contextmanager
def connect_to_database(args):
    with pymysql.connect(user=args.db_user,
                         unix_socket=args.db_socket,
                         db=args.db_name) as cursor:
        yield cursor


def upload_info(extracted_data, cursor):

    query = '''insert into transmission_sources ({fields})
    values ({placeholders})'''

    for row in extracted_data:
        full_query = query.format(
            fields=','.join(row._fields),
            placeholders=','.join(['%s'] * len(row._fields)))
        cursor.execute(full_query, args=row)


def column_type(data):
    '''
    Returns the fits name for a column type
    '''
    dtype = data.dtype
    if dtype == np.float64:
        return 'D'
    elif dtype == np.int64:
        return 'K'
    elif dtype == bool:
        return 'L'
    else:
        raise TypeError("No fits type for %s specified" % dtype)


def render_fits_catalogue(data, fname):
    columns_data = {
        field_name: np.array([getattr(row, field_name) for row in data])
        for field_name in data[0]._fields
    }
    columns = {
        field_name: fits.Column(name=field_name,
                                format=column_type(columns_data[field_name]),
                                array=columns_data[field_name])
        for field_name in columns_data
    }

    header = {'image_id': data[0].image_id,}
    phdu = fits.PrimaryHDU(header=fits.Header(header.items()))
    tbl = fits.BinTableHDU.from_columns(columns.values())
    tbl.name = 'transmission_catalogue'
    hdulist = fits.HDUList([phdu, tbl])
    hdulist.writeto(fname, clobber=True)


def main(args):
    if args.verbose:
        logger.setLevel('DEBUG')
    logger.debug(args)

    file_info = list(extract_from_file(args.refimage))

    with connect_to_database(args) as cursor:
        upload_info(file_info, cursor)

    if args.fits_out is not None:
        render_fits_catalogue(file_info, args.fits_out)


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
    parser.add_argument('--fits-out', required=False)
    main(parser.parse_args())
