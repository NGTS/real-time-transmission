#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse

from ngts_transmission.logs import logger
from ngts_transmission.db import (add_database_arguments,
                                  connect_to_database_from_args)
from ngts_transmission.transmission import TransmissionEntry


def main(args):
    if args.verbose:
        logger.setLevel('DEBUG')
    logger.debug(args)

    with connect_to_database_from_args(args) as cursor:
        entry = TransmissionEntry.from_file(args.filename, cursor,
                                            sky_radius_inner=args.radius_inner,
                                            sky_radius_outer=args.radius_outer)
        entry.upload_to_database(cursor)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('--radius-inner',
                        required=False,
                        default=4.,
                        type=float,
                        help='Inner sky annulus radius')
    parser.add_argument('--radius-outer',
                        required=False,
                        default=8.,
                        type=float,
                        help='Outer sky annulus radius')
    add_database_arguments(parser)
    parser.add_argument('-v', '--verbose', action='store_true')
    main(parser.parse_args())
