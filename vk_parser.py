import time
from datetime import datetime

from requests.exceptions import ConnectionError

from database import db_connection as db, save_attachment_to_db
from vk_api import vk_api


class VkParser:
    """
    Сканирует сообщения с указанным пользователем и сохраняет их в заранее созданную PostgreSQL базу.
    Таблицы создаются автоматически в database/db_connection.py
    Может сканировать пользователей как по числовому, так и по буквенному ID.
    """

    def __init__(self, friend_id: int or str):
        self.messages = []
        self.SCAN_MESSAGES_PER_CALL = 200  # максимум, что позволяет API VK
        self.offset_scanned_messages = -200  # отрицательный offset в силу особенностей API VK

        self.my_user_data = self._get_user_data()
        self.friend_user_data = self._get_user_data(friend_id)

        self.my_id, self.my_url_nickname, self.my_first_name, self.my_last_name = self.my_user_data
        self.friend_id, self.friend_url_nickname, self.friend_first_name, self.friend_last_name = self.friend_user_data
        self._save_users_to_db()

        self.total_messages = self._get_number_of_messages()
        self.messages_scanned_before, self.last_scanned_id = self._get_saved_messages_statistics()
        self.messages_was_scanned = self.messages_scanned_before  # количество ранее сканированных сообщений
        self.count_messages_was_printed = self.messages_scanned_before  # для печати статистики в консоль

        # реализовано для удобного вызова функций по типу вложения вместо if/elif
        self.save_to_db_methods = {
            'photo': save_attachment_to_db.save_photo_to_db,
            'sticker': save_attachment_to_db.save_sticker_to_db,
            'link': save_attachment_to_db.save_link_to_db,
            'video': save_attachment_to_db.save_video_to_db,
            'doc': save_attachment_to_db.save_doc_to_db,
            'audio': save_attachment_to_db.save_audio_to_db,
            'audio_message': save_attachment_to_db.save_audio_message_to_db,
            'call': save_attachment_to_db.save_call_to_db,
            'gift': save_attachment_to_db.save_gift_to_db,
            'wall': save_attachment_to_db.save_wall_to_db,
            'graffiti': save_attachment_to_db.save_graffiti_to_db,
            'story': save_attachment_to_db.save_story_to_db,
        }

    def get_messages_from_vk(self) -> None:
        """
        Обращается к API VK и вытягивает 200 сообщений. Если сообщений с этим пользователем не было в базе (проверяется
        в self.last_scanned_id), то парсит с самого начала. Если сообщения были - начинает парсить с N + 1.
        Если ошибок не было - offset смещается, позволяя получить следующие 200 сообщений. self.offset отрицательный
        из-за особенностей получения сообщений через API, т.к. start_message_id и rev (reverse) не работают вместе.
        """
        while True:  # иногда VK API банит запрос и приходится спрашивать заново
            try:
                json_messages = vk_api.method('messages.getHistory', user_id=self.friend_id,
                                              count=self.SCAN_MESSAGES_PER_CALL,
                                              offset=self.offset_scanned_messages,
                                              start_message_id=self.last_scanned_id)
                json_messages['items'] = json_messages['items'][::-1]  # теперь сообщения идут в хронологическом порядке
                for message in json_messages['items']:
                    self.messages.append(message)
                self.offset_scanned_messages -= self.SCAN_MESSAGES_PER_CALL
                break
            except (ConnectionError, AttributeError):  # скрипт всегда падает без этой обработки исключений
                time.sleep(0.2)

    def print_parsing_progress_to_console(self) -> None:
        """
        Печатает в консоль прогресс сканирования сообщений.
        """
        self.messages_was_scanned += len(self.messages)
        if self.messages_was_scanned > self.total_messages:  # чтобы не превышало общее количество сообщений
            self.messages_was_scanned = self.total_messages
        print(f'{self.messages_was_scanned} из {self.total_messages} сообщений сохранены в базе')

    def _save_messages_to_db(self) -> None:
        """
        Берёт сообщения из self.messages, сканированные ранее, и кладёт их в базу. Если в сообщении было вложение -
        кладёт вложение в таблицу этого типа вложений. Пропускает market в виду малого смысла его использования.
        """
        for message in self.messages:
            message_id: int = message['id']
            date_gmt: datetime = datetime.fromtimestamp(message['date'])
            from_id: int = message['from_id']
            chat_id: int = message['peer_id']
            conversation_message_id: int = message.get('conversation_message_id')
            text: str = message['text']
            db.cursor.execute(
                'INSERT INTO messages (message_id, date_gmt, from_id, chat_id, conversation_message_id, text) '
                'VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (message_id) DO NOTHING',
                (message_id, date_gmt, from_id, chat_id, conversation_message_id, text,))

            if db.cursor.statusmessage == 'INSERT 0 1':  # если значение вставлено успешно, защита от дубликатов
                for attachment in message.get('attachments'):
                    attachment_type: str = attachment['type']
                    if attachment_type == 'market':  # можно класть и маркет в базу, но смысла мало
                        continue
                    try:
                        # в зависимости от типа вложения запускается нужный метод, см. __init__.self.save_to_db_methods
                        self.save_to_db_methods[attachment_type](db.cursor, message['id'],
                                                                 attachment[attachment_type])
                    except TypeError:  # если в будущих версиях VK появятся новые типы вложений
                        print(f'[ERR] Не вставили значение в базу, пропускаем: {attachment}')
        db.connect.commit()

    def _save_users_to_db(self) -> None:
        """
        Можно сохранять имена пользователей в разных падежах, их можно вытянуть через API VK.
        """
        users = [self.my_user_data, self.friend_user_data]
        # users = ', '.join([self.sql_field_char] * len(users))
        sql_insert_into_users = 'INSERT INTO users (vk_id, vk_url_nickname, vk_first_name, vk_last_name) ' \
                                'VALUES (%s, %s, %s, %s) ON CONFLICT (vk_url_nickname) DO NOTHING'

        db.cursor.executemany(sql_insert_into_users, users)
        db.connect.commit()

    @staticmethod
    def _get_user_data(input_id: int or str = '') -> tuple[int, str, str, str]:
        """
        В случае input_id="" (не None) достаются данные своего аккаунта.
        fields='screen_name' - псевдоним страницы, идущий после https://vk.com/.
        """
        while True:
            try:
                user_data: dict = vk_api.method('users.get', user_ids=input_id, fields='screen_name')[0]
                user_id: int = user_data['id']
                user_url_nickname: str = user_data['screen_name']
                user_first_name: str = user_data['first_name']
                user_last_name: str = user_data['last_name']
                return user_id, user_url_nickname, user_first_name, user_last_name
            except (ConnectionError, AttributeError):
                time.sleep(0.2)

    def _get_number_of_messages(self) -> int:
        """
        total_messages - количество всех сообщений с пользователем.
        """
        while True:
            try:
                total_messages: int = vk_api.method('messages.getHistory', user_id=self.friend_id)['count']
                return total_messages
            except (ConnectionError, AttributeError):
                time.sleep(0.2)

    def _get_saved_messages_statistics(self) -> tuple[int, int]:
        """
        messages_scanned_before - количество сообщений, уже сохранённых в базе (чтобы не сканировать сначала).
        last_scanned_id - последний ID сообщения в базе (меняется на 1 при отсутствии сообщений в базе).
        """
        db.cursor.execute('SELECT COUNT(*) FROM messages WHERE chat_id = %s', (self.friend_id,))
        messages_scanned_before: int = db.cursor.fetchone()[0]
        db.cursor.execute('SELECT MAX(message_id) FROM messages WHERE chat_id = %s', (self.friend_id,))
        last_scanned_id: int = db.cursor.fetchone()[0]
        last_scanned_id = 1 if last_scanned_id is None else last_scanned_id
        return messages_scanned_before, last_scanned_id

    def run(self) -> None:
        """
        Основная функция, запускает парсинг сообщений, сохраняет сообщения в базу, печатая прогресс сканирования.
        """
        while self.messages_was_scanned < self.total_messages:
            self.get_messages_from_vk()
            self._save_messages_to_db()
            self.print_parsing_progress_to_console()
            del self.messages[:]  # чистит оперативку, влияет на вывод статистики и отправку сообщений в базу
        else:
            print(f'Сообщения с пользователем {self.friend_first_name} {self.friend_last_name} сохранены в базе')

    def __del__(self) -> None:
        try:
            if db.connect:
                db.cursor.close()
                db.connect.close()
        except AttributeError:
            pass
