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

import os

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


class Job(object):

    def __init__(self, filename):
        self.filename = filename

    @classmethod
    def from_row(cls, row):
        args = row.split(SEP)
        mapping = dict([arg.split('=') for arg in args])
        return cls(filename=mapping['file'])

    def __eq__(self, other):
        return self.filename == other.filename


def fetch_transmission_jobs(cursor):
    cursor.execute(JOB_QUERY)
    for row, in cursor:
        yield Job.from_row(row)


def ref_catalogue_exists(cursor, ref_id):
    cursor.execute(REFCAT_QUERY)
    ref_ids = set([row[0] for row in cursor])
    return ref_id in ref_ids


def get_refcat_id(filename):
    header = fits.getheader(filename)
    return header['agrefimg']


def ref_image_path(image_id, cursor):
    cursor.execute(REFFILENAME_QUERY, (image_id,))
    if cursor.rowcount == 0:
        raise KeyError('Cannot find filename for image {image_id}'.format(
            image_id=image_id))
    row = cursor.fetchone()
    return os.path.join(AG_REFIMAGE_PATH, row[0])
