import pytest

from ngts_transmission.db import raw_create_table


def test_create_table():
    schema_def = {'test': {'id': 'integer primary key auto_increment',},}

    expected = 'create table test (id integer primary key auto_increment)'
    assert raw_create_table('test', schema_def) == expected


def test_handle_missing_key():
    schema_def = {'bad': {'id': 'integer primary key auto_increment',},}

    with pytest.raises(KeyError):
        raw_create_table('test', schema_def)
