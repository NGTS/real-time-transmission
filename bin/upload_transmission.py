#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse
from collections import namedtuple
from ngts_transmission import (logger, connect_to_database,
                               add_database_arguments, database_schema)
import photutils as ph
from astropy.io import fits
import numpy as np

schema = database_schema()['transmission_log']
TransmissionEntryBase = namedtuple('TransmissionEntryBase', schema.keys())


def mad(data, median=None):
    median = median if median is not None else np.median(data)
    return np.median(np.abs(data - median))


def photometry_local(data, x, y, aperture_radius, sky_radius_inner=6,
                     sky_radius_outer=8):
    apertures = ph.CircularAperture((x, y), r=aperture_radius)
    annulus_apertures = ph.CircularAnnulus((x, y),
                                           r_in=sky_radius_inner,
                                           r_out=sky_radius_outer)
    rawflux_table = ph.aperture_photometry(data, apertures)
    bkgflux_table = ph.aperture_photometry(data, annulus_apertures)
    bkg_mean = bkgflux_table['aperture_sum'] / annulus_apertures.area()
    bkg_sum = bkg_mean * apertures.area()
    final_sum = rawflux_table['aperture_sum'] - bkg_sum
    return np.array(final_sum)


class TransmissionEntry(TransmissionEntryBase):

    @classmethod
    def from_file(cls, filename):
        logger.info('Extracting transmission from %s', filename)
        with fits.open(filename) as infile:
            header = infile[0].header
            image_id = header['image_id']

        photometry_results = extract_photometry_results(filename)
        photometry_results['image_id'] = image_id

        return cls(**photometry_results)

    def upload_to_database(self, cursor):
        keys = self._fields
        values = [getattr(self, key) for key in keys]
        query = '''insert into transmission_log ({keys})
        values ({placeholder})'''.format(
            keys=', '.join(keys),
            placeholder=', '.join(['%s'] * len(keys)))
        logger.debug('Executing query: `%s` : [%s]', query,
                     ', '.join(map(str, values)))
        cursor.execute(query, values)


def main(args):
    if args.verbose:
        logger.setLevel('DEBUG')
    logger.debug(args)

    entry = TransmissionEntry.from_file(args.filename)
    with connect_to_database(args) as cursor:
        entry.upload_to_database(cursor)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    add_database_arguments(parser)
    parser.add_argument('-v', '--verbose', action='store_true')
    main(parser.parse_args())
