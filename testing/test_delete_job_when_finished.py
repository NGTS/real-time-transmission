import pytest
import pymysql

from ngts_transmission.watching import fetch_transmission_jobs


@pytest.yield_fixture
def cursor():
    connection = pymysql.connect(user='ops', db='ngts_ops')
    cursor = connection.cursor()
    try:
        yield cursor
    finally:
        connection.rollback()
        connection.close()


def test_job_deleted(job_db, cursor):
    job = list(fetch_transmission_jobs(cursor))[0]
    job.remove_from_database(cursor)

    assert list(fetch_transmission_jobs(cursor)) == []
