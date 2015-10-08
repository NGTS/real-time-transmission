import pytest
import pymysql

from ngts_transmission import watching as w


@pytest.fixture
def filename():
    return '/ngts/das03/action106267_observeField/IMAGE80520150920234004.fits'


@pytest.fixture
def jobs(filename):
    return iter([w.Job(filename=filename),])


def test_database_initialised(job_db, connection):
    cursor = connection.cursor()
    cursor.execute('select count(*) from job_args')
    nrows, = cursor.fetchone()
    assert nrows == 6


def test_query_for_jobs(job_db, connection, jobs):
    cursor = connection.cursor()
    db_jobs = w.fetch_transmission_jobs(cursor)
    assert list(db_jobs) == list(jobs)


def test_job_class():
    filename = 'test'
    j = w.Job(filename=filename)
    assert j.filename == filename
