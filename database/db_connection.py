import sys

import psycopg2
from psycopg2._psycopg import connection as _connect, cursor as _cursor  # нужны для автодополнения в IDE

from settings import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DBNAME, POSTGRES_HOST, POSTGRES_PORT

try:
    connect: _connect = psycopg2.connect(user=POSTGRES_USER, password=POSTGRES_PASSWORD,
                                         dbname=POSTGRES_DBNAME, host=POSTGRES_HOST, port=POSTGRES_PORT)
    cursor: _cursor = connect.cursor()  # аннотация типов у connection и cursor нужна для автодополнения в IDE
except psycopg2.OperationalError:
    sys.exit(f'Не смогли подключиться к базе PostgreSQL с названием {POSTGRES_DBNAME}')


def create_tables_if_not_exists(connect, cursor):
    with open('create_db_tables.sql') as file:
        sql = file.read()
    cursor.execute(sql)
    connect.commit()


create_tables_if_not_exists(connect, cursor)
