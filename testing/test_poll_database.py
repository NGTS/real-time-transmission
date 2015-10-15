import mock
import pytest
import pymysql
import os
import datetime

from ngts_transmission.watching import fetch_transmission_jobs, Job


@pytest.fixture
def filename():
    return '/ngts/das03/action106267_observeField/IMAGE80520150920234004.fits'


@pytest.fixture
def jobs(filename):
    return iter([Job(job_id=None, filename=filename),])


def test_database_initialised(job_db, connection):
    cursor = connection.cursor()
    cursor.execute('select count(*) from job_args')
    nrows, = cursor.fetchone()
    assert nrows == 6


def test_query_for_jobs(job_db, connection, jobs):
    cursor = connection.cursor()
    db_jobs = fetch_transmission_jobs(cursor)
    assert list(db_jobs) == list(jobs)


def test_multiple_jobs(job_db, connection):
    file_root = os.path.join('/', 'ngts', 'das03', 'action106267_observeField')
    base = 80520150920234005
    filenames = [os.path.join(file_root, 'IMAGE{}.fits'.format(base + i))
                 for i in range(5)]
    cursor = connection.cursor()

    # Make sure there is one entry always valid
    past = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    future = datetime.datetime.utcnow() + datetime.timedelta(days=1)

    for filename in filenames:
        cursor.execute('''insert into job_queue (job_type, submitted, expires)
                       values (%s, %s, %s)''', ('transparency', past, future))
        row_id = cursor.lastrowid
        cursor.execute('''insert into job_args (job_id, arg_key, arg_value)
                       values (%s, %s, %s)''', (row_id, 'file', filename))

    db_jobs = list(fetch_transmission_jobs(cursor))
    assert len(db_jobs) == len(filenames) + 1
    connection.rollback()


def test_job_class():
    filename = 'test'
    j = Job(job_id=None, filename=filename)
    assert j.filename == filename


def test_job_real_filename():
    test_fname = 'test.fits'

    def side_effect(fname):
        return '.bz2' not in fname

    with mock.patch('ngts_transmission.watching.os.path.isfile',
                    side_effect=side_effect):
        job = Job(job_id=None, filename=test_fname)
        assert job.real_filename == 'test.fits'


def test_job_real_filename_compressed():
    test_fname = 'test.fits'

    def side_effect(fname):
        return '.bz2' in fname

    with mock.patch('ngts_transmission.watching.os.path.isfile',
                    side_effect=side_effect):
        job = Job(job_id=None, filename=test_fname)
        assert job.real_filename == 'test.fits.bz2'


def test_job_real_filename_doesnt_exist():
    test_fname = 'test.fits'

    with mock.patch('ngts_transmission.watching.os.path.isfile',
                    return_value=False):
        with pytest.raises(OSError) as err_msg:
            job = Job(job_id=None, filename=test_fname)
            job.real_filename

            expected_err = 'Cannot find any of the files: test.fits, test.fits.bz2'
            assert err_msg == expected_err
