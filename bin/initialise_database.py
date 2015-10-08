#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse

from ngts_transmission.utils import logger
from ngts_transmission.db import (connect_to_database, add_database_arguments,
                                  database_schema)


def main(args):
    if args.verbose:
        logger.setLevel('DEBUG')
    logger.debug(args)

    schema = database_schema()

    tables = {}
    for table_name, column_defs in schema.items():
        column_text = (', '.join([
            ' '.join([k, v]) for (k, v) in column_defs.items()
        ]))
        query = 'create table {table_name} ({column_text})'.format(
            table_name=table_name,
            column_text=column_text)
        tables[table_name] = query

    with connect_to_database(args) as cursor:
        for table_name, query in tables.items():
            cursor.execute('drop table if exists {table_name}'.format(
                table_name=table_name))
            logger.debug('Executing query `%s`', query)
            cursor.execute(query)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    add_database_arguments(parser)
    main(parser.parse_args())
