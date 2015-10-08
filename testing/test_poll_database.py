import pymysql

from ngts_transmission import watching as w


def test_database_initialised(job_db, connection):
    cursor = connection.cursor()
    cursor.execute('select count(*) from job_args')
    nrows, = cursor.fetchone()
    assert nrows > 0


def test_query_for_jobs():
    jobs = w.fetch_transmission_jobs()
    filename = '/ngts/das03/action106267_observeField/IMAGE80520150920234004.fits'
    assert list(jobs) == [w.Job(filename=filename)]


def test_job_class():
    filename = 'test'
    j = w.Job(filename=filename)
    assert j.filename == filename
