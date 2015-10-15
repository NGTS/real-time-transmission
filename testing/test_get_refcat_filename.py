import pytest
import pymysql

from ngts_transmission.watching import ref_image_path


@pytest.fixture
def connection():
    return pymysql.connect(user='ops', db='ngts_ops')


@pytest.fixture
def cursor(connection):
    return connection.cursor()


def test_ref_image_path(cursor):
    image_id = 80220150418091345
    result = ref_image_path(image_id, cursor)
    expected = '/ngts/autoguider_ref/NG2000-4500_802_IMAGE80220150418091345.fits'
    assert result == expected


def test_invalid_ref_id(cursor):
    image_id = 10101
    with pytest.raises(KeyError) as err:
        result = ref_image_path(image_id, cursor)
        assert str(err) == 'Cannot find filename for image 10101'
