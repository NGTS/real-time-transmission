import pytest
import pymysql
import os
import datetime

build_connection = lambda: pymysql.connect(user='ops', db='ngts_ops')


@pytest.yield_fixture
def connection():
    connection = build_connection()
    yield connection
    connection.rollback()
    connection.close()


@pytest.fixture(scope='session')
def job_db_query():
    fname = os.path.join(os.path.dirname(__file__), 'job_db.sql')
    with open(fname) as infile:
        return infile.read().replace('\n', '')


@pytest.fixture(scope='session')
def job_db(job_db_query):
    connection = build_connection()
    cursor = connection.cursor()
    for line in job_db_query.split(';'):
        if line.strip():
            cursor.execute(line)
    # Make sure there is one entry always valid
    past = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    future = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    cursor.execute('''
        insert into job_queue (job_type, submitted, expires)
        values (%s, %s, %s)
        ''', ('transparency', past, future))
    row_id = cursor.lastrowid
    cursor.execute('''
        insert into job_args (job_id, arg_key, arg_value)
        values (%s, %s, %s)
        ''', (
        row_id, 'file',
        '/ngts/das03/action106267_observeField/IMAGE80520150920234004.fits'))
    connection.commit()
    connection.close()
