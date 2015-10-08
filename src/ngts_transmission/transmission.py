from collections import namedtuple
import photutils as ph
from astropy.io import fits
import numpy as np

from ngts_transmission.utils import logger, open_fits
from ngts_transmission.db import database_schema

schema = database_schema()['transmission_log']
TransmissionEntryBase = namedtuple('TransmissionEntryBase', schema.keys())


def mad(data, median=None):
    median = median if median is not None else np.median(data)
    return np.median(np.abs(data - median))


def std_from_mad(mad):
    '''
    Source: https://en.wikipedia.org/wiki/Median_absolute_deviation#Relation_to_standard_deviation
    '''
    return 1.4826 * mad


def standard_error(flux):
    # Only 1d arrays allowed
    assert len(flux.shape) == 1
    return std_from_mad(mad(flux)) / np.sqrt(flux.size)


def photometry_local(data, x, y, aperture_radius, sky_radius_inner,
                     sky_radius_outer):
    logger.debug('Sky annulus radii: %s -> %s', sky_radius_inner,
                 sky_radius_outer)
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


def query_for_ref_image_id(image_id, cursor):
    query = '''select ref_image_id from ngts_ops.autoguider_refimage
    join ngts_ops.raw_image_list using (field, camera_id)
    where image_id = %s'''

    cursor.execute(query, (image_id,))
    return cursor.fetchone()[0]


class Photometry(object):

    def __init__(self, x, y, radius, flux):
        self.x = x
        self.y = y
        self.radius = radius
        self.flux = flux

        self.__truediv__ = self.__div__

    @classmethod
    def from_database(cls, cursor, ref_image_id):
        query = '''select x_coordinate, y_coordinate, aperture_radius, flux_adu
            from transmission_sources
            where ref_image_id = %s'''

        cursor.execute(query, (ref_image_id,))
        rows = cursor.fetchall()
        arrays = list(map(np.array, zip(*rows)))
        return cls(*arrays)

    @classmethod
    def extract_from_file(cls, filename, ref_catalogue, sky_radius_inner,
                          sky_radius_outer):
        with open_fits(filename) as infile:
            image_data = infile[0].data

        source_flux = photometry_local(
            image_data, ref_catalogue.x, ref_catalogue.y,
            ref_catalogue.radius[0], sky_radius_inner, sky_radius_outer)
        return cls(ref_catalogue.x, ref_catalogue.y, ref_catalogue.radius,
                   source_flux)

    def flag(self):
        return 0.

    def __div__(self, other):
        assert np.all(
            np.isclose(self.x, other.x) & np.isclose(self.y, other.y))

        return self.__class__(
            self.x, self.y, self.radius, self.flux / other.flux)


def extract_photometry_results(filename, cursor, image_id, sky_radius_inner,
                               sky_radius_outer):
    '''placeholder for Max's code'''
    ref_image_id = query_for_ref_image_id(image_id, cursor)
    ref_catalogue = Photometry.from_database(cursor, ref_image_id)
    source_flux = Photometry.extract_from_file(
        filename, ref_catalogue, sky_radius_inner, sky_radius_outer)
    flux_ratio = source_flux / ref_catalogue

    return {
        'image_mean_flux': float(ref_catalogue.flux.mean()),
        'mean_flux_ratio': float(flux_ratio.flux.mean()),
        'median_flux_ratio': float(np.median(flux_ratio.flux)),
        # Standard error, using the MAD converted to std
        'flux_ratio_err': float(standard_error(flux_ratio.flux)),
        'flux_ratio_lq': float(np.percentile(flux_ratio.flux, 25)),
        'flux_ratio_uq': float(np.percentile(flux_ratio.flux, 75)),
        'flux_ratio_stdev': float(flux_ratio.flux.std()),
        'flag': flux_ratio.flag(),
    }


class TransmissionEntry(TransmissionEntryBase):

    @classmethod
    def from_file(cls, filename, cursor, sky_radius_inner, sky_radius_outer):
        logger.info('Extracting transmission from %s', filename)
        with open_fits(filename) as infile:
            header = infile[0].header
            image_id = header['image_id']

        photometry_results = extract_photometry_results(
            filename, cursor, image_id, sky_radius_inner, sky_radius_outer)
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
