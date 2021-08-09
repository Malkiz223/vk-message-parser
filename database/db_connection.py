import sys

import psycopg2
from psycopg2._psycopg import connection as _connect, cursor as _cursor  # нужны для автодополнения в IDE


def connect_to_postgres():
    try:
        from settings import postgres_user, postgres_password, postgres_dbname, postgres_host, postgres_port
        connect: _connect = psycopg2.connect(user=postgres_user, password=postgres_password,
                                             dbname=postgres_dbname, host=postgres_host, port=postgres_port)
        cursor: _cursor = connect.cursor()  # аннотация типов у connection и cursor нужна для автодополнения в IDE
        return connect, cursor
    except ImportError:
        sys.exit('Ошибка импорта настроек PostgreSQL из файла settings.py')
    except psycopg2.OperationalError:
        sys.exit(f'Не смогли подключиться к базе PostgreSQL с названием {postgres_dbname}')


def create_tables_if_not_exists(connect, cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS users ('
                   '    vk_id INT PRIMARY KEY,'
                   '    vk_url_nickname VARCHAR(50) UNIQUE NOT NULL,'
                   '    vk_first_name VARCHAR(50) NOT NULL,'
                   '    vk_last_name VARCHAR(50) NOT NULL'
                   ');'
                   'CREATE TABLE IF NOT EXISTS messages ('
                   '    message_id INT PRIMARY KEY,'
                   '    date_gmt TIMESTAMP NOT NULL,'
                   '    from_id INT NOT NULL,'
                   '    chat_id INT NOT NULL,'
                   '    conversation_message_id INT,'
                   '    text TEXT,'
                   '    FOREIGN KEY (from_id) REFERENCES users (vk_id)'
                   ');'
                   'CREATE TABLE IF NOT EXISTS photos ('
                   '    message_id INT NOT NULL,'
                   '    image_url TEXT NOT NULL,'
                   '    FOREIGN KEY (message_id) REFERENCES messages (message_id)'
                   ');'
                   'CREATE TABLE IF NOT EXISTS stickers ('
                   '    message_id INT NOT NULL UNIQUE,'
                   '    product_id INT NOT NULL,'
                   '    sticker_id INT NOT NULL,'
                   '    image_url VARCHAR(50) NOT NULL,'
                   '    FOREIGN KEY (message_id) REFERENCES messages (message_id)'
                   ');'
                   'CREATE TABLE IF NOT EXISTS links ('
                   '    message_id INT NOT NULL,'
                   '    title TEXT,'
                   '    url TEXT NOT NULL,'
                   '    FOREIGN KEY (message_id) REFERENCES messages (message_id)'
                   ');'
                   'CREATE TABLE IF NOT EXISTS videos ('
                   '    message_id INT NOT NULL,'
                   '    description TEXT,'
                   '    duration INT NOT NULL,'
                   '    image_url TEXT,'
                   '    FOREIGN KEY (message_id) REFERENCES messages (message_id)'
                   ');'
                   'CREATE TABLE IF NOT EXISTS docs ('
                   '    message_id INT NOT NULL,'
                   '    title VARCHAR(255),'
                   '    extension VARCHAR(255),'
                   '    url TEXT,'
                   '    FOREIGN KEY (message_id) REFERENCES messages (message_id)'
                   ');'
                   'CREATE TABLE IF NOT EXISTS audios ('
                   '    message_id INT NOT NULL,'
                   '    artist VARCHAR(255) NOT NULL,'
                   '    title VARCHAR(255) NOT NULL,'
                   '    duration INT NOT NULL,'
                   '    url TEXT,'
                   '    FOREIGN KEY (message_id) REFERENCES messages (message_id)'
                   ');'
                   'CREATE TABLE IF NOT EXISTS audio_messages ('
                   '    message_id INT NOT NULL UNIQUE,'
                   '    duration INT NOT NULL,'
                   '    link_ogg VARCHAR(255) NOT NULL UNIQUE,'
                   '    link_mp3 VARCHAR(255) NOT NULL UNIQUE,'
                   '    transcript TEXT,'
                   '    FOREIGN KEY (message_id) REFERENCES messages (message_id)'
                   ');'
                   'CREATE TABLE IF NOT EXISTS calls ('
                   '    message_id INT NOT NULL UNIQUE,'
                   '    initiator_id INT NOT NULL,'
                   '    state VARCHAR(60) NOT NULL,'
                   '    video BOOLEAN NOT NULL,'
                   '    FOREIGN KEY (message_id) REFERENCES messages (message_id),'
                   '    FOREIGN KEY (initiator_id) REFERENCES users (vk_id)'
                   ');'
                   'CREATE TABLE IF NOT EXISTS gifts ('
                   '    message_id INT NOT NULL UNIQUE,'
                   '    gift_id INT NOT NULL,'
                   '    image_url VARCHAR(255) NOT NULL,'
                   '    stickers_product_id INT,'
                   '    FOREIGN KEY (message_id) REFERENCES messages (message_id)'
                   ');'
                   'CREATE TABLE IF NOT EXISTS walls ('
                   '    message_id INT NOT NULL UNIQUE,'
                   '    from_id INT NOT NULL,'
                   '    post_date_gmt TIMESTAMP,'
                   '    post_type VARCHAR(20),'
                   '    text TEXT,'
                   '    FOREIGN KEY (message_id) REFERENCES messages (message_id)'
                   ');'
                   'CREATE TABLE IF NOT EXISTS graffiti ('
                   '    message_id INT NOT NULL UNIQUE,'
                   '    image_url VARCHAR(255),'
                   '    FOREIGN KEY (message_id) REFERENCES messages (message_id)'
                   ');'
                   'CREATE TABLE IF NOT EXISTS stories ('
                   '    message_id INT NOT NULL UNIQUE,'
                   '    can_see INT NOT NULL,'
                   '    story_date_gmt TIMESTAMP NOT NULL,'
                   '    expires_at_gmt TIMESTAMP NOT NULL,'
                   '    is_one_time BOOLEAN,'
                   '    FOREIGN KEY (message_id) REFERENCES messages (message_id)'
                   ');')
    connect.commit()


connect, cursor = connect_to_postgres()
create_tables_if_not_exists(connect, cursor)
