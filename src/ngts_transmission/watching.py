t''
* Poll the database for "transmission" entries in the queue
* When there are some entries:
    * check for if there is a reference source list
    * if there is not:
        * find the reference image
        * extract the source catalogue
    * find the files on disk
    * extract the sources
'''

import os
from astropy.io import fits

from ngts_transmission.utils import NullPool, logger, open_fits
from ngts_transmission.transmission import TransmissionEntry
from ngts_transmission.catalogue import build_catalogue

SEP = '|'
JOB_QUERY = '''
select group_concat(concat_ws('=', arg_key, arg_value) separator '{sep}') as args
from job_queue left join job_args using (job_id)
where expires > now()
group by job_id
'''.format(sep=SEP)

REFCAT_QUERY = '''
select distinct ref_image_id
from transmission_sources
'''

REFFILENAME_QUERY = '''
select filename from autoguider_refimage where ref_image_id = %s
'''

AG_REFIMAGE_PATH = os.path.join('/', 'ngts', 'autoguider_ref')

RADIUS_INNER = 4.
RADIUS_OUTER = 8.


class Job(object):

    def __init__(self, filename):
        self.filename = filename

    @classmethod
    def from_row(cls, row):
        args = row.split(SEP)
        mapping = dict([arg.split('=') for arg in args])
        return cls(filename=mapping['file'])

    def update(self, cursor):
        ref_image_id = get_refcat_id(self.filename)
        if not ref_catalogue_exists(cursor, ref_image_id):
            logger.info('Reference catalogue missing, creating')
            ref_image_filename = ref_image_path(ref_image_id, cursor)
            build_catalogue(ref_image_filename, cursor)
        else:
            logger.info('Reference catalogue exists')

        t = TransmissionEntry.from_file(self.filename, cursor,
                                        sky_radius_inner=RADIUS_INNER,
                                        sky_radius_outer=RADIUS_OUTER)
        t.upload_to_database(cursor)

    def __eq__(self, other):
        return self.filename == other.filename

    def __str__(self):
        return '<TransmissionJob {self.filename}>'.format(self=self)


def fetch_transmission_jobs(cursor):
    logger.info('Fetching transmission jobs')
    cursor.execute(JOB_QUERY)
    for row, in cursor:
        yield Job.from_row(row)


def ref_catalogue_exists(cursor, ref_id):
    logger.info('Checking if ref image {ref_id} exists'.format(ref_id=ref_id))
    cursor.execute(REFCAT_QUERY)
    ref_ids = set([row[0] for row in cursor])
    return ref_id in ref_ids


def get_refcat_id(filename):
    logger.debug('Extracting reference image id from {filename}'.format(
        filename=filename))
    with open_fits(filename) as infile:
        header = infile[0].header
    return header['agrefimg']


def ref_image_path(ref_image_id, cursor):
    cursor.execute(REFFILENAME_QUERY, (ref_image_id,))
    if cursor.rowcount == 0:
        raise KeyError('Cannot find filename for image {image_id}'.format(
            image_id=ref_image_id))
    row = cursor.fetchone()
    return os.path.join(AG_REFIMAGE_PATH, row[0])
