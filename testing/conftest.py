import pytest
import pymysql
import os

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
    connection.commit()
    connection.close()
