import mock
import pytest
from pymysql.cursors import Cursor

from ngts_transmission.watching import ref_catalogue_exists


@pytest.fixture
def cursor():
    return mock.MagicMock(name='cursor', spec=Cursor)


@pytest.fixture
def ref_id():
    return 10101


def test_query_for_reference_ids(cursor, ref_id):
    cursor.__iter__.return_value = [(ref_id,),]
    assert ref_catalogue_exists(cursor, ref_id) == True


def test_query_no_ref_catalogue_exists(cursor, ref_id):
    cursor.__iter__.return_value = []
    assert ref_catalogue_exists(cursor, ref_id) == False
