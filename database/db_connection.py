import sys

import psycopg2
from psycopg2._psycopg import connection as _connect, cursor as _cursor  # нужны для автодополнения в IDE

from settings import postgres_user, postgres_password, postgres_dbname, postgres_host, postgres_port

try:
    connect: _connect = psycopg2.connect(user=postgres_user, password=postgres_password,
                                         dbname=postgres_dbname, host=postgres_host, port=postgres_port)
    cursor: _cursor = connect.cursor()  # аннотация типов у connection и cursor нужна для автодополнения в IDE
except psycopg2.OperationalError:
    sys.exit(f'Не смогли подключиться к базе PostgreSQL с названием {postgres_dbname}')


def create_tables_if_not_exists(connect, cursor):
    with open('create_db_tables.sql') as file:
        sql = file.read()
    cursor.execute(sql)
    connect.commit()


create_tables_if_not_exists(connect, cursor)
