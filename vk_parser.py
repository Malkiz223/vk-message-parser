import os
import time
from datetime import datetime

import psycopg2
from psycopg2._psycopg import connection
from requests.exceptions import ConnectionError
from vk_messages import MessagesAPI

import settings


class VkParser:
    """
    Сканирует сообщения с указанным пользователем и сохраняет их в заранее созданную PostgreSQL базу.
    Скрипт создания таблиц лежит в database/create_db.py.
    Может сканировать пользователей как по числовому, так и по буквенному ID.
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
        self.SCAN_MESSAGES_PER_CALL = 200  # максимум, что позволяет API VK
        self.offset_scanned_messages = -200  # отрицательный offset в силу особенностей API VK
        # реализовано для удобного вызова функций по типу вложения - вместо if/elif
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

        self.my_id, self.my_url_nickname, self.my_first_name, self.my_last_name = self._get_user_data()
        self.friend_id, self.friend_url_nickname, self.friend_first_name, self.friend_last_name = self._get_user_data(
            friend_id)
        self._save_users_to_db()

        self.total_messages, self.messages_scanned_before, self.last_scanned_id = self._get_chat_statistic()
        self.messages_was_scanned = self.messages_scanned_before
        self.count_messages_was_printed = self.messages_scanned_before

    def get_messages_from_vk(self) -> None:
        """
        Обращается к API VK и вытягивает 200 сообщений. Если сообщений с этим пользователем не было в базе (проверяется
        в self.last_scanned_id), то парсит с самого начала. Если сообщения были - начинает парсить с N + 1.
        Если ошибок не было - offset смещается, позволяя получить следующие 200 сообщений. self.offset отрицательный
        из-за особенностей получения сообщений через API , т.к. start_message_id и rev (reverse) не работают вместе.
        """
        try:
            json_messages = self.vk_api.method('messages.getHistory', user_id=self.friend_id,
                                               count=self.SCAN_MESSAGES_PER_CALL,
                                               offset=self.offset_scanned_messages,
                                               start_message_id=self.last_scanned_id)
            json_messages['items'] = json_messages['items'][::-1]
            for message in json_messages['items']:
                self.messages.append(message)
            self.offset_scanned_messages -= self.SCAN_MESSAGES_PER_CALL
        except (ConnectionError, AttributeError):  # скрипт всегда падает без этой обработки исключений
            time.sleep(0.1)

    def print_parsing_progress_to_console(self) -> None:
        """
        Печатает в консоль прогресс сканирования сообщений. При дублировании значения пропускает печать.
        """
        self.messages_was_scanned += len(self.messages)
        if self.messages_was_scanned > self.total_messages:  # чтобы не превышало верхний предел сообщений
            self.messages_was_scanned = self.total_messages
        if self.count_messages_was_printed < self.messages_was_scanned:  # если уже печатало данное количество - скипаем
            print(f'Просканировано {self.messages_was_scanned} из {self.total_messages} сообщений')
            self.count_messages_was_printed = self.messages_was_scanned  # иначе дублирует печать

    def save_messages_to_db(self) -> None:
        """
        Берёт сообщения из self.messages, просканированные ранее, и кладёт их в базу. Если в сообщении было вложение -
        кладёт вложение в таблицу этого типа вложений. Пропускает market в виду малого смысла его использования.
        """
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
                    if attachment_type == 'market':  # можно класть и маркет в базу, но смысла мало
                        continue
                    try:
                        # в зависимости от типа вложения запускается нужный метод, см. __init__.self.save_to_db_methods
                        self.save_to_db_methods[attachment_type](message['id'], attachment[attachment_type])
                    except TypeError:  # если в будущих версиях VK появятся новые типы вложений
                        print(f'[ERR] Не вставили значение в базу, пропускаем: {attachment}')
        self.connection.commit()

    def _save_photo_to_db(self, message_id: int, attachment: dict) -> None:
        photo_url: str = attachment['sizes'][-1]['url']
        self.cursor.execute('INSERT INTO photos (message_id, image_url) VALUES (%s, %s)', (message_id, photo_url,))

    def _save_sticker_to_db(self, message_id: int, attachment: dict) -> None:
        product_id: int = attachment['product_id']
        sticker_id: int = attachment['sticker_id']
        image_url: str = f'https://vk.com/sticker/1-{sticker_id}-512'  # 512 ширина/высота стикера, есть 64/128/256/512
        self.cursor.execute('INSERT INTO stickers (message_id, product_id, sticker_id, image_url) '
                            'VALUES (%s, %s, %s, %s)', (message_id, product_id, sticker_id, image_url,))

    def _save_link_to_db(self, message_id: int, attachment: dict) -> None:
        title: str = attachment['title']
        url: str = attachment['url']
        self.cursor.execute('INSERT INTO links (message_id, title, url) VALUES (%s, %s, %s)', (message_id, title, url))

    def _save_video_to_db(self, message_id: int, attachment: dict) -> None:
        """
        У видео нет ссылки, даже если оно ведёт на YouTube. Через API его достать нельзя.
        """
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
        url: str = attachment['url']  # url аудио позволяет скачать какую-то непонятную фигню формата .m3u8
        self.cursor.execute('INSERT INTO audios (message_id, artist, title, duration, url) VALUES (%s, %s, %s, %s, %s)',
                            (message_id, artist, title, duration, url,))

    def _save_audio_message_to_db(self, message_id: int, attachment: dict) -> None:
        duration: str = attachment['duration']
        link_ogg: str = attachment['link_ogg']
        link_mp3: str = attachment['link_mp3']
        transcript: str = attachment.get('transcript')  # транскрипт отсутствует у старых сообщений, положится null
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
        is_one_time: bool = attachment['is_one_time']  # на моей практике здесь всегда лежит False
        self.cursor.execute('INSERT INTO stories (message_id, can_see, story_date_gmt, expires_at_gmt, is_one_time) '
                            'VALUES (%s, %s, %s, %s, %s)',
                            (message_id, can_see, story_date_gmt, expires_at_gmt, is_one_time,))

    def _save_users_to_db(self) -> None:
        """
        Можно класть имена в разных падежах, их можно вытянуть через API VK.
        """
        sql_insert_into_users = ('INSERT INTO users (vk_id, vk_url_nickname, vk_first_name, vk_last_name) '
                                 'VALUES (%s, %s, %s, %s) ON CONFLICT (vk_url_nickname) DO NOTHING')
        users = [(self.my_id, self.my_url_nickname, self.my_first_name, self.my_last_name),
                 (self.friend_id, self.friend_url_nickname, self.friend_first_name, self.friend_last_name)]
        self.cursor.executemany(sql_insert_into_users, users)
        self.connection.commit()

    def _get_user_data(self, input_id: int or str = ''):
        """
        В случае input_id="" (не None) достаются данные своего аккаунта. fields='screen_name' - псевдоним страницы,
        идущий после https://vk.com/. Замена id12345 либо сама строка id12345 при отсутствии псевдонима.
        """
        while True:
            try:
                user_data = self.vk_api.method('users.get', user_ids=input_id, fields='screen_name')[0]
                user_id = user_data['id']
                user_url_nickname = user_data['screen_name']
                user_first_name = user_data['first_name']
                user_last_name = user_data['last_name']
                return user_id, user_url_nickname, user_first_name, user_last_name
            except (ConnectionError, AttributeError):
                time.sleep(0.2)

    def _get_chat_statistic(self):
        """
        total_messages - всего сообщений с пользователем
        messages_scanned_before - количество сообщений, просканированных ранее (чтобы не начинать сначала).
        last_scanned_id - последний айдишник сообщения в базе (меняется на 1 при отсутствии сообщений в базе).
        """
        while True:
            try:
                total_messages = self.vk_api.method('messages.getHistory', user_id=self.friend_id)['count']
                break
            except (ConnectionError, AttributeError):
                time.sleep(0.2)
        self.cursor.execute('SELECT COUNT(*) FROM messages WHERE chat_id = %s', (self.friend_id,))
        messages_scanned_before = self.cursor.fetchone()[0]
        self.cursor.execute('SELECT MAX(message_id) FROM messages WHERE chat_id = %s', (self.friend_id,))
        last_scanned_id = self.cursor.fetchone()[0]
        last_scanned_id = 1 if last_scanned_id is None else last_scanned_id
        return total_messages, messages_scanned_before, last_scanned_id

    def run(self) -> None:
        """
        Основная функция, запускает парсинг сообщений, сохраняет сообщения в базу, печатая прогресс сканирования.
        """
        while self.messages_was_scanned < self.total_messages:
            self.get_messages_from_vk()
            self.save_messages_to_db()
            self.print_parsing_progress_to_console()
            del self.messages[:]  #
        else:
            print(f'Сообщения с пользователем {self.friend_first_name} {self.friend_last_name} просканированы')

    def __del__(self) -> None:
        if self.connection:
            self.cursor.close()
            self.connection.close()


if __name__ == '__main__':
    friend_id = 1  # int or str (1 or 'durov')
    parser = VkParser(friend_id=friend_id)
    parser.run()
