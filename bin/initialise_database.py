#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse

from ngts_transmission import (logger, connect_to_database,
                               add_database_arguments)


def main(args):
    if args.verbose:
        logger.setLevel('DEBUG')
    logger.debug(args)

    table_name = 'transmission_sources'
    query = '''create table {table_name} (
        id integer primary key auto_increment,
        image_id bigint not null,
        x_coordinate float not null,
        y_coordinate float not null,
        inc_prescan tinyint default 1,
        flux_adu float not null
    )
    '''.format(table_name=table_name)

    with connect_to_database(args) as cursor:
        cursor.execute('drop table if exists {table_name}'.format(
            table_name=table_name))
        cursor.execute(query)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    add_database_arguments(parser)
    main(parser.parse_args())
