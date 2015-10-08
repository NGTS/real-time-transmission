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

SEP = '|'
QUERY = '''
select group_concat(concat_ws('=', arg_key, arg_value) separator '{sep}') as args
from job_queue left join job_args using (job_id)
where expires > now()
group by job_id
'''.format(sep=SEP)


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
    cursor.execute(QUERY)
    for row, in cursor:
        yield Job.from_row(row)
