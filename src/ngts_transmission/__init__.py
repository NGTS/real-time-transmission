from contextlib import contextmanager
import logging
import pymysql
import json
import os
import bz2
from astropy.io import fits

logging.basicConfig(level='INFO', format='%(levelname)7s %(message)s')
logger = logging.getLogger(__name__)


@contextmanager
def open_fits(fname):
    if '.bz2' in fname:
        with bz2.BZ2File(fname) as uncompressed:
            with fits.open(uncompressed) as infile:
                yield infile
    else:
        with fits.open(fname) as infile:
            yield infile


@contextmanager
def connect_to_database(args):
    if args.db_host is not None:
        with pymysql.connect(user=args.db_user,
                             host=args.db_host,
                             db=args.db_name) as cursor:
            logger.debug('Connected to database')
            yield cursor
            logger.debug('Closing database connection')
    else:
        socket = args.db_socket if args.db_socket is not None else '/var/lib/mysql/mysql.sock'
        with pymysql.connect(user=args.db_user,
                             unix_socket=socket,
                             db=args.db_name) as cursor:
            logger.debug('Connected to database')
            yield cursor
            logger.debug('Closing database connection')


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
