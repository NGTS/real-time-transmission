import mock
from pymysql.cursors import Cursor

from ngts_transmission.watching import ref_catalogue_exists


class TestRefCatalogueChecking(object):

    def setup(self):
        self.cursor = mock.MagicMock(name='cursor', spec=Cursor)
        self.ref_id = 10101

    def test_query_for_reference_ids(self):
        self.cursor.__iter__.return_value = [(self.ref_id,),]
        assert ref_catalogue_exists(self.cursor, self.ref_id) == True

    def test_query_no_ref_catalogue_exists(self):
        self.cursor.execute.return_value = []
        assert ref_catalogue_exists(self.cursor, self.ref_id) == False
