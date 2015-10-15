#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse

from ngts_transmission.catalogue import build_catalogue
from ngts_transmission.db import add_database_arguments
from ngts_transmission.logs import logger


def main(args):
    if args.verbose:
        logger.setLevel('DEBUG')
    logger.debug(args)

    build_catalogue(
        refimage=args.refimage,
        region_filename=args.refimage + '.reg',
        n_pixels=args.npix,
        threshold=args.threshold,
        fwhmfilt=args.fwhmfilt,
        isolation_radius=args.isolation_radius,
        aperture_radius=args.aperture_radius,
        db_host=args.db_host,
        db_user=args.db_user,
        db_name=args.db_name,
        db_socket=args.db_socket,
        fits_out=args.fits_out,)


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
