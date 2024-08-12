from contextlib import contextmanager
import pymysql
from pymysql.connections import Connection
import json
import os

from ngts_transmission.logs import logger



class DebugConnection(Connection):
    logger = logger

    def _log(self, *args, **kwargs):
        if self.logger:
            self.logger.debug(*args, **kwargs)

    def __enter__(self):
        self._log('Starting transaction')
        return super(DebugConnection, self).__enter__()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._log('Trying to commit transaction')
        if exc_type is not None:
            self._log('Commit failed, rolling back')
        else:
            self._log('Commit ok')
        return super(DebugConnection, self).__exit__(exc_type, exc_value, exc_traceback)

    def __repr__(self):
        return 'DEBUG %r' % repr(super(DebugConnection, self))

# Monkey patch the connection object to add logging
pymysql.connections.Connection = DebugConnection


@contextmanager
def connect_to_database_from_args(args):
    socket = args.db_socket if args.db_socket is not None else '/var/lib/mysql/mysql.sock'
    with connect_to_database(user=args.db_user,
                             host=args.db_host,
                             db=args.db_name,
                             unix_socket=socket) as cursor:
        yield cursor


@contextmanager
def connect_to_database(user, host, db, unix_socket):
    if host is not None:
        with pymysql.connect(user=user, host=host, db=db) as cursor:
            logger.debug('Connected to database')
            yield cursor
            logger.debug('Closing database connection')
    else:
        with pymysql.connect(user=user,
                             unix_socket=unix_socket,
                             db=db) as cursor:
            logger.debug('Connected to database')
            yield cursor
            logger.debug('Closing database connection')


@contextmanager
def transaction(connection):
    with connection as cursor:
        yield cursor
        logger.debug('Committing')


def add_database_arguments(parser):
    parser.add_argument('--db-socket',
                        required=False,
                        help='Socket to connect to')
    parser.add_argument('--db-host', required=False, help='Host to connect to')
    parser.add_argument('--db-user',
                        required=False,
                        default='ops',
                        help='Database user')
    parser.add_argument('--db-name',
                        required=False,
                        default='ngts_ops',
                        help='Database')
    return parser


def database_schema():
    path = os.path.join(os.path.dirname(__file__), 'columns.json')
    with open(path) as infile:
        return json.load(infile)


def raw_create_table(name, column_map):
    column_defs = column_map[name]
    column_text = (', '.join([
        ' '.join([k, v]) for (k, v) in column_defs.items()
    ]))
    return 'create table {table_name} ({column_text})'.format(
        table_name=name,
        column_text=column_text)
