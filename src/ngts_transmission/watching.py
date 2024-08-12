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
import Pyro4

from ngts_transmission.logs import logger
from ngts_transmission.utils import open_fits, time_context, get_refcat_id, NoAutoguider
from ngts_transmission.transmission import TransmissionEntry
from ngts_transmission.catalogue import build_catalogue
from ngts_transmission.db import transaction

# Configuration
SLEEP_TIME = 10  # Seconds
NJOBS_PER_LOOP = 50
RADIUS_INNER = 4.
RADIUS_OUTER = 8.

# Limit the query to only 20 objects per 60 seconds
SEP = '|'
JOB_QUERY = '''
select
    job_id, group_concat(concat_ws('=', arg_key, arg_value) separator '{sep}') as args
from job_queue left join job_args using (job_id)
where expires > now()
and job_type = 'transparency'
group by job_id
order by submitted desc
limit {njobs}'''.format(sep=SEP, njobs=NJOBS_PER_LOOP)

REFCAT_QUERY = '''
select distinct ref_image_id
from transmission_sources
'''

REFFILENAME_QUERY = '''
select filename from autoguider_refimage where ref_image_id = %s
'''

AG_REFIMAGE_PATH = os.path.join('/', 'ngts', 'autoguider_ref')

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

    def update(self, connection):
        try:
            ref_image_id = get_refcat_id(self.real_filename)
        except NoAutoguider:
            # Return early but ensure the job is removed from the database by
            # not propogating the exception
            return

        with connection as cursor:
            does_refcat_exist = ref_catalogue_exists(cursor, ref_image_id)

        if does_refcat_exist:
            logger.info('Reference catalogue exists')
        else:
            logger.info('Reference catalogue missing, creating')
            ref_image_filename = ref_image_path(ref_image_id, connection)
            build_catalogue(ref_image_filename, connection)

        with connection as cursor:
            t = TransmissionEntry.from_file(self.real_filename, cursor,
                                            sky_radius_inner=RADIUS_INNER,
                                            sky_radius_outer=RADIUS_OUTER)
            t.upload_to_database(cursor)

    def remove_from_database(self, connection):
        logger.info('Removing {self} from the database'.format(self=self))
        with connection as cursor:
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
    # Prefetch the jobs to allow the cursor to perform another query
    jobs = cursor.fetchall()
    return [Job.from_row(row) for row in jobs]


def ref_catalogue_exists(cursor, ref_id):
    logger.info('Checking if ref image {ref_id} exists'.format(ref_id=ref_id))
    cursor.execute(REFCAT_QUERY)
    ref_ids = set([row[0] for row in cursor])
    return ref_id in ref_ids


def ref_image_path(ref_image_id, connection):
    with connection as cursor:
        cursor.execute(REFFILENAME_QUERY, (ref_image_id,))
        if cursor.rowcount == 0:
            raise KeyError('Cannot find filename for image {image_id}'.format(
                image_id=ref_image_id))
        row = cursor.fetchone()
    return os.path.join(AG_REFIMAGE_PATH, row[0])


def watcher_loop_step(connection):
    # Starts transaction for job_queue table, short lived so Paladin should not
    # have a write lock
    with transaction(connection) as cursor:
        transmission_jobs = fetch_transmission_jobs(cursor)

    njobs = len(transmission_jobs)
    logger.info('Found %s jobs', njobs)

    # Separate transaction for updating transmission database
    for i, transmission_job in enumerate(transmission_jobs):
        logger.info('Job %d/%d', i + 1, njobs)
        try:
            transmission_job.update(connection)
        except Exception as e:
            logger.exception('Exception occurred: %s', str(e))
        else:
            transmission_job.remove_from_database(connection)


def watcher(connection):
    logger.info('Starting watcher')
    logger.debug('Connecting to central hub')
    hub = Pyro4.Proxy('PYRONAME:central.hub')

    while True:
        try:
            logger.debug('Pinging hub')
            hub.report_in('transparency')
        except Exception as err:
            logger.exception('Failure communicating with hub process')
            raise

        with time_context():
            watcher_loop_step(connection)

        logger.debug('Sleeping for %s seconds', SLEEP_TIME)
        time.sleep(SLEEP_TIME)


def main():
    logger.setLevel('DEBUG')
    connection = pymysql.connect(host='ngts-par-ds', user='ops', db='ngts_ops')
    watcher(connection)
