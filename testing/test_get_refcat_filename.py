import pytest
import pymysql

from ngts_transmission.watching import ref_image_path


def test_ref_image_path():
    image_id = 80220150418091345
    connection = pymysql.connect(user='ops', db='ngts_ops')
    result = ref_image_path(image_id, connection)
    expected = '/ngts/autoguider_ref/NG2000-4500_802_IMAGE80220150418091345.fits'
    assert result == expected


def test_invalid_ref_id():
    image_id = 10101
    connection = pymysql.connect(user='ops', db='ngts_ops')
    with pytest.raises(KeyError) as err:
        result = ref_image_path(image_id, connection)
        assert str(err) == 'Cannot find filename for image 10101'
