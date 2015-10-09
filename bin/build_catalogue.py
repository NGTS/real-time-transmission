#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse

from ngts_transmission.catalogue import (extract_from_file, upload_info,
                                         render_fits_catalogue)
from ngts_transmission.db import (connect_to_database_from_args,
                                  add_database_arguments)
from ngts_transmission.utils import logger


def main(args):
    if args.verbose:
        logger.setLevel('DEBUG')
    logger.debug(args)

    file_info = list(extract_from_file(
        args.refimage,
        region_filename=args.refimage + '.reg',
        n_pixels=args.npix,
        threshold=args.threshold,
        fwhmfilt=args.fwhmfilt,
        isolation_radius=args.isolation_radius,
        aperture_radius=args.aperture_radius,))

    with connect_to_database_from_args(args) as cursor:
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
    add_database_arguments(parser)
    parser.add_argument('-n', '--npix',
                        required=False,
                        default=2,
                        type=int,
                        help='Number of neighbouring pixels to be defined '
                        'as a source')
    parser.add_argument('-t', '--threshold',
                        required=False,
                        default=3,
                        type=float,
                        help='Significance sigma for source detect')
    parser.add_argument('-f', '--fwhmfilt',
                        required=False,
                        default=1.5,
                        type=float,
                        help='FWHM')
    parser.add_argument('-i', '--isolation-radius',
                        required=False,
                        default=6,
                        type=float,
                        help='Isolation distance (pix)')
    parser.add_argument('-r', '--aperture-radius',
                        required=False,
                        default=3.,
                        type=float,
                        help='Aperture radius (pix)')
    parser.add_argument('--fits-out', required=False)
    main(parser.parse_args())
