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
import numpy as np
from scipy.spatial import KDTree

logging.basicConfig(level='INFO', format='%(levelname)7s %(message)s')
logger = logging.getLogger(__name__)

TransmissionCatalogueEntry = namedtuple('TransmissionCatalogueEntry', [
    'image_id',
    'x_coordinate',
    'y_coordinate',
    'inc_prescan',
    'flux_adu',
])


def image_has_prescan(fname):
    return fits.getdata(fname).shape == (2048, 2088)


def source_detect(fname, n_pixels=3, threshold=7):
    logger.info('Running source detect')
    logger.debug('n_pixels: %s, threshold: %s', n_pixels, threshold)
    with tempfile.NamedTemporaryFile(suffix='.fits') as tfile:
        cmd = ['imcore', fname, 'noconf', tfile.name, n_pixels, threshold,]
        sp.check_call(list(map(str, cmd)))
        tfile.seek(0)

        with fits.open(tfile.name) as infile:
            return infile[1].data


def isolated_index(x, y, radius=6.):
    tree = KDTree(np.vstack([x, y]).T)
    index = np.zeros_like(x, dtype=bool)
    for i in np.arange(x.size):
        within = tree.query_ball_point((x[i], y[i]), radius)
        # There should be only one star (the target) within `radius` pixels
        if len(within) == 1:
            index[i] = True

    return index


def filter_source_table(source_table):
    logger.info('Filtering source list')
    # Build up an index
    index = np.ones(len(source_table), dtype=bool)

    # Include only stars in the centre
    edge_margin = 512
    overscan_width = 20
    image_size = 2048
    index &= (source_table['X_coordinate'] > (overscan_width + edge_margin))
    index &= (source_table['X_coordinate'] < (image_size - edge_margin))
    index &= (source_table['Y_coordinate'] > edge_margin)
    index &= (source_table['Y_coordinate'] < (image_size - edge_margin))

    # Now only a specific flux range. Assume the stellar flux goes into
    # `psf_size` pixels so the value can be higher than 2**16-1
    psf_size = 2.
    flux_lims = (flux_lim_low, flux_lim_high) = (1E3 * psf_size,
                                                 45E3 * psf_size)
    index &= (source_table['Aper_flux_3'] >= flux_lim_low)
    index &= (source_table['Aper_flux_3'] <= flux_lim_high)

    # Only include isolated stars
    index &= isolated_index(source_table['X_coordinate'],
                            source_table['Y_coordinate'])

    # Return the final catalogue
    return source_table[index]


class RegionFile(object):

    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        self.fptr = open(self.filename, 'w')
        self.write_header()
        return self

    def __exit__(self, *args):
        self.fptr.close()

    @staticmethod
    def circle(x, y, colour, radius=3.):
        return 'circle({x},{y},{radius}) # color={colour}\n'.format(
            x=x,
            y=y,
            colour=colour,
            radius=radius)

    def add_regions(self, catalogue, colour):
        logger.debug('Adding %s regions', colour)
        for row in catalogue:
            self.fptr.write(
                self.circle(
                    row['X_coordinate'], row['Y_coordinate'],
                    colour=colour))

    def write_header(self):
        header = '''# Region file format: DS9 version 4.1
global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1
image'''

        self.fptr.write(header + '\n')


def extract_from_file(fname, region_filename):
    logger.info('Extracting catalogue from %s', fname)
    with fits.open(fname) as infile:
        header = infile[0].header

    image_id = header['image_id']
    source_table = source_detect(fname)
    logger.info('Found %s sources', len(source_table))
    filtered_source_table = filter_source_table(source_table)
    logger.info('Keeping %s sources', len(filtered_source_table))

    with RegionFile(region_filename) as rfile:
        rfile.add_regions(filtered_source_table, colour='green')
        rfile.add_regions(source_table, colour='red')

    inc_prescan = image_has_prescan(fname)
    logger.debug('Image has prescan: %s', inc_prescan)
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
        logger.debug('Connected to database')
        yield cursor
        logger.debug('Closing database connection')


def upload_info(extracted_data, cursor):

    query = '''insert into transmission_sources ({fields})
    values ({placeholders})'''

    def format_query(query_str):
        return ' '.join([line.strip() for line in query_str.split('\n')])

    for row in extracted_data:
        full_query = query.format(
            fields=','.join(row._fields),
            placeholders=','.join(['%s'] * len(row._fields)))
        logger.debug('Inserting %s: %s', format_query(full_query), list(row))
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
    logger.info('Rendering fits file to %s', fname)
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

    file_info = list(extract_from_file(args.refimage, args.refimage + '.reg'))

    with connect_to_database(args) as cursor:
        upload_info(file_info, cursor)

    if args.fits_out is not None:
        render_fits_catalogue(file_info, args.fits_out)


if __name__ == '__main__':
    description = '''
    Given an autoguider reference frame, extract a source catalogue, filter the
    object list and store in a file
    '''

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('refimage')
    parser.add_argument('--db-socket',
                        required=False,
                        default='/var/lib/mysql/mysql.sock',
                        help='Socket to connect to')
    parser.add_argument('--db-user',
                        required=False,
                        default='ops',
                        help='Database user')
    parser.add_argument('--db-name',
                        required=False,
                        default='ngts_ops',
                        help='Database')
    parser.add_argument('--fits-out', required=False)
    main(parser.parse_args())