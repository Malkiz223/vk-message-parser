import os
import time
from datetime import datetime

import psycopg2
from psycopg2._psycopg import connection
from requests.exceptions import ConnectionError
from vk_messages import MessagesAPI

import settings

# TODO добавить докстринги
# TODO добавить сканирование с места прерывания
# TODO добавить возможность сканирования сразу однопоточно сразу нескольких пользователей
#  или сканирование всех чатов без добавления вручную
# TODO перевести проект на Flask
# TODO добавить поддержку другой базы с автосозданием? сканировать наличие базы PostgreSQL

# TODO в прогресс добавлять не оффсет, а длинну self.messages
# TODO зайти под сессией на сайт вк и распарсить всех собеседников?


class VkParser:
    """
    Сканирует сообщения с указанным пользователем.
    """

    def __init__(self, friend_id: int or str):
        if not os.path.exists('sessions/'):
            os.mkdir('sessions/')
        self.vk_api = MessagesAPI(login=settings.VK_LOGIN, password=settings.VK_PASSWORD,
                                  two_factor=True, cookies_save_path='sessions/')
        self.connection: connection = psycopg2.connect(user='postgres', password=os.getenv('POSTGRESQL_PASSWORD'),
                                                       database='vk_messages', host='127.0.0.1', port=5432)
        self.cursor = self.connection.cursor()
        self.messages = []
        self.SCAN_MESSAGES_PER_CALL = 200
        self.offset_scanned_messages = 0
        self.count_messages_was_printed = 0
        self.now_scanned = self.SCAN_MESSAGES_PER_CALL + self.offset_scanned_messages
        self.save_to_db_methods = {
            'photo': self._save_photo_to_db,
            'sticker': self._save_sticker_to_db,
            'link': self._save_link_to_db,
            'video': self._save_video_to_db,
            'doc': self._save_doc_to_db,
            'audio': self._save_audio_to_db,
            'audio_message': self._save_audio_message_to_db,
            'call': self._save_call_to_db,
            'gift': self._save_gift_to_db,
            'wall': self._save_wall_to_db,
            'graffiti': self._save_graffiti_to_db,
            'story': self._save_story_to_db,
        }

        # получаем self.(friend_id, friend_url_nickname, friend_first_name, friend_last_name) и аналогично с self.my_...
        self._get_users_name_and_id_data(friend_id)
        self._save_users_to_db()
        while True:
            try:
                self.total_messages = self.vk_api.method('messages.getHistory', user_id=self.friend_id)['count']
                break
            except ConnectionError:  # иногда сервер ВК банит частые запросы и скрипт падает
                time.sleep(0.2)

    def get_messages_from_vk(self) -> None:
        """
        Обращается к API VK и вытягивает 200 сообщений, начиная с self.offset_scanned_messages (нулевое сообщение).
        Если ошибок не было - offset смещается, позволяя запарсить следующие 200 сообщений.
        """
        try:
            json_messages = self.vk_api.method('messages.getHistory', user_id=self.friend_id,
                                               count=self.SCAN_MESSAGES_PER_CALL,
                                               rev=-1, offset=self.offset_scanned_messages)
            for message in json_messages['items']:
                self.messages.append(message)
            self.offset_scanned_messages += self.SCAN_MESSAGES_PER_CALL
        except (ConnectionError, AttributeError):  # раньше вместо ConnectionError был BaseException
            pass

    def print_parsing_progress_to_console(self) -> None:
        """
        Печатает в консоль прогресс сканирования сообщений. При дублировании значения пропускает печать.
        """
        if self.now_scanned > self.total_messages:
            self.now_scanned = self.total_messages  # чтобы не превышало верхний предел сообщений
        if self.count_messages_was_printed < self.now_scanned:  # если уже печатало данное количество - скипаем
            print(f'Просканировано {self.now_scanned} из {self.total_messages} сообщений')
            self.count_messages_was_printed = self.now_scanned
        self.now_scanned = self.SCAN_MESSAGES_PER_CALL + self.offset_scanned_messages

    def save_messages_to_db(self) -> None:
        for message in self.messages:
            message_id: int = message['id']
            date_gmt: datetime = datetime.fromtimestamp(message['date'])
            from_id: int = message['from_id']
            chat_id: int = message['peer_id']
            conversation_message_id: int = message.get('conversation_message_id')
            text: str = message['text']
            self.cursor.execute(
                'INSERT INTO messages (message_id, date_gmt, from_id, chat_id, conversation_message_id, text) '
                'VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (message_id) DO NOTHING',
                (message_id, date_gmt, from_id, chat_id, conversation_message_id, text,))
            if self.cursor.statusmessage == 'INSERT 0 1':  # если значение вставлено успешно
                for attachment in message.get('attachments'):
                    attachment_type: str = attachment['type']
                    if attachment_type == 'market':
                        continue
                    try:
                        # в зависимости от типа вложения запускается нужный метод, см. __init__.self.save_to_db_methods
                        self.save_to_db_methods[attachment_type](message['id'], attachment[attachment_type])
                    except TypeError:
                        print(f'[ERR] Не вставили значение в базу, пропускаем: {attachment}')
        self.connection.commit()
        del self.messages[:]

    def _save_photo_to_db(self, message_id: int, attachment: dict) -> None:
        photo_url: str = attachment['sizes'][-1]['url']
        self.cursor.execute('INSERT INTO photos (message_id, image_url) VALUES (%s, %s)', (message_id, photo_url,))

    def _save_sticker_to_db(self, message_id: int, attachment: dict) -> None:
        product_id: int = attachment['product_id']
        sticker_id: int = attachment['sticker_id']
        image_url: str = f'https://vk.com/sticker/1-{sticker_id}-512'
        self.cursor.execute('INSERT INTO stickers (message_id, product_id, sticker_id, image_url) '
                            'VALUES (%s, %s, %s, %s)', (message_id, product_id, sticker_id, image_url,))

    def _save_link_to_db(self, message_id: int, attachment: dict) -> None:
        title: str = attachment['title']
        url: str = attachment['url']
        self.cursor.execute('INSERT INTO links (message_id, title, url) VALUES (%s, %s, %s)', (message_id, title, url))

    def _save_video_to_db(self, message_id: int, attachment: dict) -> None:
        description: str = attachment.get('description')
        duration: int = attachment['duration']
        image_url: str = attachment['image'][-1]['url']
        self.cursor.execute('INSERT INTO videos (message_id, description, duration, image_url) VALUES (%s, %s, %s, %s)',
                            (message_id, description, duration, image_url,))

    def _save_doc_to_db(self, message_id: int, attachment: dict) -> None:
        title: str = attachment['title']
        extension: str = attachment['ext']
        url: str = attachment['url']
        self.cursor.execute('INSERT INTO docs (message_id, title, extension, url) VALUES (%s, %s, %s, %s)',
                            (message_id, title, extension, url,))

    def _save_audio_to_db(self, message_id: int, attachment: dict) -> None:
        artist: str = attachment['artist']
        title: str = attachment['title']
        duration: int = attachment['duration']
        url: str = attachment['url']
        self.cursor.execute('INSERT INTO audios (message_id, artist, title, duration, url) VALUES (%s, %s, %s, %s, %s)',
                            (message_id, artist, title, duration, url,))

    def _save_audio_message_to_db(self, message_id: int, attachment: dict) -> None:
        duration: str = attachment['duration']
        link_ogg: str = attachment['link_ogg']
        link_mp3: str = attachment['link_mp3']
        transcript: str = attachment.get('transcript')
        self.cursor.execute('INSERT INTO audio_messages (message_id, duration, link_ogg, link_mp3, transcript) VALUES ('
                            '%s, %s, %s, %s, %s)', (message_id, duration, link_ogg, link_mp3, transcript,))

    def _save_call_to_db(self, message_id: int, attachment: dict) -> None:
        initiator_id: int = attachment['initiator_id']
        state: str = attachment['state']
        video: bool = attachment['video']
        self.cursor.execute('INSERT INTO calls (message_id, initiator_id, state, video) VALUES (%s, %s, %s, %s)',
                            (message_id, initiator_id, state, video,))

    def _save_gift_to_db(self, message_id: int, attachment: dict) -> None:
        gift_id: int = attachment['id']
        image_url: str = attachment['thumb_256']
        stickers_product_id: int = attachment.get('stickers_product_id')
        self.cursor.execute('INSERT INTO gifts (message_id, gift_id, image_url, stickers_product_id) VALUES ('
                            '%s, %s, %s, %s)', (message_id, gift_id, image_url, stickers_product_id,))

    def _save_wall_to_db(self, message_id: int, attachment: dict) -> None:
        from_id: int = attachment['from_id']
        post_date_gmt: datetime = datetime.fromtimestamp(attachment['date'])
        post_type: str = attachment['post_type']
        text: str = attachment['text']
        self.cursor.execute('INSERT INTO walls (message_id, from_id, post_date_gmt, post_type, text) VALUES ('
                            '%s, %s, %s, %s, %s)', (message_id, from_id, post_date_gmt, post_type, text,))

    def _save_graffiti_to_db(self, message_id: int, attachment: dict) -> None:
        image_url: str = attachment['url']
        self.cursor.execute('INSERT INTO graffiti (message_id, image_url) VALUES (%s, %s)', (message_id, image_url,))

    def _save_story_to_db(self, message_id: int, attachment: dict) -> None:
        can_see: int = attachment['can_see']
        story_date_gmt: datetime = datetime.fromtimestamp(attachment['date'])
        expires_at_gmt: datetime = datetime.fromtimestamp(attachment['expires_at'])
        is_one_time: bool = attachment['is_one_time']
        self.cursor.execute('INSERT INTO stories (message_id, can_see, story_date_gmt, expires_at_gmt, is_one_time) '
                            'VALUES (%s, %s, %s, %s, %s)',
                            (message_id, can_see, story_date_gmt, expires_at_gmt, is_one_time,))

    def _save_users_to_db(self) -> None:
        sql_insert_into_users = ('INSERT INTO users (vk_id, vk_url_nickname, vk_first_name, vk_last_name) '
                                 'VALUES (%s, %s, %s, %s) ON CONFLICT (vk_url_nickname) DO NOTHING')
        users = [(self.my_id, self.my_url_nickname, self.my_first_name, self.my_last_name),
                 (self.friend_id, self.friend_url_nickname, self.friend_first_name, self.friend_last_name)]
        self.cursor.executemany(sql_insert_into_users, users)
        self.connection.commit()

    def _get_users_name_and_id_data(self, input_id: int or str):
        while True:
            try:
                my_user_data = self.vk_api.method('users.get', fields='screen_name')[0]
                self.my_id = my_user_data['id']
                self.my_url_nickname = my_user_data['screen_name']
                self.my_first_name = my_user_data['first_name']
                self.my_last_name = my_user_data['last_name']
                break
            except (ConnectionError, AttributeError):
                time.sleep(0.2)
        while True:
            try:
                friend_user_data = self.vk_api.method('users.get', user_ids=input_id, fields='screen_name')[0]
                self.friend_id = friend_user_data['id']
                self.friend_url_nickname = friend_user_data['screen_name']
                self.friend_first_name = friend_user_data['first_name']
                self.friend_last_name = friend_user_data['last_name']
                break
            except (ConnectionError, AttributeError):
                time.sleep(0.2)

    def run(self) -> None:
        """
        Основная функция, запускает парсинг сообщений, выжидая между парсингом определённое время и печатая статистику.
        """
        while self.offset_scanned_messages <= self.total_messages:
            self.get_messages_from_vk()
            self.save_messages_to_db()
            self.print_parsing_progress_to_console()
            time.sleep(0.1)  # Без задержки работает стабильно, но вдруг начнут блокировать запросы

    def __del__(self) -> None:
        if self.connection:
            self.cursor.close()
            self.connection.close()


if __name__ == '__main__':
    friend_id = 1  # int or str (1 or 'durov')
    parser = VkParser(friend_id=friend_id)
    parser.run()
