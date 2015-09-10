#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse
from collections import namedtuple
from ngts_transmission import (logger, connect_to_database,
                               add_database_arguments)

TransmissionEntryBase = namedtuple('TransmissionEntryBase', [
    'image_id', 'mean_flux', 'flux_offset', 'flag'
])


class TransmissionEntry(TransmissionEntryBase):
    pass


def main(args):
    if args.verbose:
        logger.setLevel('DEBUG')
    logger.debug(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    add_database_arguments(parser)
    parser.add_argument('-v', '--verbose', action='store_true')
    main(parser.parse_args())
