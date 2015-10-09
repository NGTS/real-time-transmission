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


@pytest.fixture
def refimage_file(fixtures_dir):
    return os.path.join(fixtures_dir, 'refimage.fits')


@pytest.fixture(scope='module')
def connection():
    return pymysql.connect(user='ops', db='ngts_ops')


@pytest.fixture
def clear_entries(connection):
    cursor = connection.cursor()
    cursor.execute('truncate table transmission_log')
    connection.commit()


@pytest.fixture
def clear_catalogue(connection):
    cursor = connection.cursor()
    cursor.execute('truncate table transmission_sources')
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


@mock.patch('ngts_transmission.watching.ref_image_path')
def test_integrate_without_refcat(ref_image_path, target_file, connection,
                                  clear_entries, clear_catalogue,
                                  refimage_file):
    ref_image_path.return_value = refimage_file
    cursor = connection.cursor()
    job = Job(filename=target_file)
    job.update(cursor)
    connection.commit()
    cursor.execute('select * from transmission_log where image_id = %s',
                   (80220150902064322,))
    assert cursor.rowcount == 1
