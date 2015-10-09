import pytest
import os
import mock
import pymysql
from pymysql.cursors import Cursor

from ngts_transmission.watching import Job


@pytest.fixture
def fixtures_dir():
    return 'data'


@pytest.fixture
def target_file(fixtures_dir):
    return os.path.join(fixtures_dir, 'science_image.fits')


@pytest.fixture(scope='module')
def connection():
    return pymysql.connect(user='ops', db='ngts_ops')


@pytest.fixture(scope='module')
def clear_entries(connection):
    cursor = connection.cursor()
    cursor.execute('truncate table transmission_log')
    connection.commit()


@pytest.fixture
def cursor(connection):
    return connection.cursor()


def test_integrate(target_file, connection, clear_entries):
    cursor = connection.cursor()
    job = Job(filename=target_file)
    job.update(cursor)
    connection.commit()
    cursor.execute('select * from transmission_log where image_id = %s',
                   (80220150902064322,))
    assert cursor.rowcount == 1
