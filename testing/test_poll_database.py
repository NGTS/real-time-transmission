import pymysql

from ngts_transmission import watching as w


def test_database_initialised(job_db, connection):
    cursor = connection.cursor()
    cursor.execute('select count(*) from job_args')
    nrows, = cursor.fetchone()
    assert nrows > 0


def test_job_class():
    filename = 'test'
    j = w.Job(filename=filename)
    assert j.filename == filename
