#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse

from ngts_transmission.logs import logger
from ngts_transmission.db import (connect_to_database_from_args, add_database_arguments,
                                  database_schema, raw_create_table)


def main(args):
    if args.verbose:
        logger.setLevel('DEBUG')
    logger.debug(args)

    schema = database_schema()

    tables = {}
    for table_name in schema:
        query = raw_create_table(table_name, schema)
        tables[table_name] = query

    with connect_to_database_from_args(args) as cursor:
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
