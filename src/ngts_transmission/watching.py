'''
* Poll the database for "transmission" entries in the queue
* When there are some entries:
    * check for if there is a reference source list
    * if there is not:
        * find the reference image
        * extract the source catalogue
    * find the files on disk
    * extract the sources
'''

import pymysql
import os
from astropy.io import fits
import time

from ngts_transmission.utils import logger, open_fits
from ngts_transmission.transmission import TransmissionEntry
from ngts_transmission.catalogue import build_catalogue

SEP = '|'
JOB_QUERY = '''
select
    job_id, group_concat(concat_ws('=', arg_key, arg_value) separator '{sep}') as args
from job_queue left join job_args using (job_id)
where expires > now()
and job_type = 'transparency'
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

    def __init__(self, job_id, filename):
        self.job_id = job_id
        self.filename = filename

    @classmethod
    def from_row(cls, row):
        job_id, args = row
        args = args.split(SEP)
        mapping = dict([arg.split('=') for arg in args])
        return cls(job_id=job_id, filename=mapping['file'])

    def update(self, cursor):
        ref_image_id = get_refcat_id(self.filename)
        if not ref_catalogue_exists(cursor, ref_image_id):
            logger.info('Reference catalogue missing, creating')
            ref_image_filename = ref_image_path(ref_image_id, cursor)
            build_catalogue(ref_image_filename, cursor)
        else:
            logger.info('Reference catalogue exists')

        t = TransmissionEntry.from_file(self.real_filename, cursor,
                                        sky_radius_inner=RADIUS_INNER,
                                        sky_radius_outer=RADIUS_OUTER)
        t.upload_to_database(cursor)

    def remove_from_database(self, cursor):
        cursor.execute('delete from job_queue where job_id = %s',
                       (self.job_id,))

    @property
    def real_filename(self):
        '''
        If the file is compressed, return the compressed filename
        '''
        trial_names = [self.filename, '{filename}.bz2'.format(
            filename=self.filename)]
        for filename in trial_names:
            if os.path.isfile(filename):
                return filename
        raise OSError('Cannot find any of the files: {files}'.format(
            files=', '.join(trial_names)))

    def __eq__(self, other):
        return self.filename == other.filename

    def __str__(self):
        return '<TransmissionJob {self.filename}>'.format(self=self)

    def __repr__(self):
        return str(self)


def fetch_transmission_jobs(cursor):
    logger.info('Fetching transmission jobs')
    cursor.execute(JOB_QUERY)
    for row in cursor:
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


def watcher_loop_step(cursor):
    transmission_jobs = fetch_transmission_jobs(cursor)
    for transmission_job in transmission_jobs:
        transmission_job.update(cursor)
        transmission_job.remove_from_database(cursor)


def watcher(connection):
    logger.info('Starting watcher')
    while True:
        cursor = connection.cursor()
        try:
            watcher_loop_step(cursor)
        except Exception as err:
            logger.exception('Exception occurred: %s' % str(err))
            connection.rollback()
        else:
            connection.commit()

        time.sleep(30)


def main():
    connection = pymysql.connect(host='ngts-par-ds', user='ops', db='ngts_ops')
    watcher(connection)


if __name__ == '__main__':
    main()
