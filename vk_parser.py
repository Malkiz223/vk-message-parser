import os
import time
from datetime import datetime

import psycopg2
from psycopg2._psycopg import connection
from requests.exceptions import ConnectionError

from vk_messages import MessagesAPI

import settings

"""
# TODO 
Перевести проект на Фласк, фронтенд - ввод логина и пароля в форму, нажатие кнопки отправки, если есть двухфакторка - 
возвращать поле с вводом кода двухфакторки, вводить и снова отправлять на сервер
Возвращать на фронт ответ вида "залогинились", и писать прогресс сканирования.
"""


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
        self.total_messages = self.vk_api.method('messages.getHistory', user_id=self.FRIEND_ID)['count']

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
        except (BaseException, AttributeError):
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

            message_id = message['id']
            if message.get('attachments'):
                for attachment in message.get('attachments'):
                    self.save_to_db_methods[attachment['type']](message_id, attachment)
        del self.messages[:]
        return True

    @staticmethod
    def _save_photo_to_db(message_id, attachment):
        pass

    @staticmethod
    def _save_sticker_to_db(message_id, attachment):
        pass

    @staticmethod
    def _save_link_to_db(message_id, attachment):
        pass

    @staticmethod
    def _save_video_to_db(message_id, attachment):
        pass

    @staticmethod
    def _save_doc_to_db(message_id, attachment):
        pass

    @staticmethod
    def _save_audio_to_db(message_id, attachment):
        pass

    @staticmethod
    def _save_audio_message_to_db(message_id, attachment):
        pass

    @staticmethod
    def _save_call_to_db(message_id, attachment):
        pass

    @staticmethod
    def _save_gift_to_db(message_id, attachment):
        pass

    @staticmethod
    def _save_wall_to_db(message_id, attachment):
        pass

    @staticmethod
    def _save_graffiti_to_db(message_id, attachment):
        pass

    @staticmethod
    def _save_story_to_db(message_id, attachment):
        pass

    def _get_users_name_and_id_data(self, input_id: int or str):
        """
        friend_user_data при input_id=1 имеет следующий вид:
                    [{"first_name": "Павел",
                     "id": 1,
                     "last_name": "Дуров",
                     "can_access_closed": true,
                     "is_closed": false,
                     "screen_name": "durov"}]
        """
        while True:
            try:
                friend_user_data = self.vk_api.method('users.get', user_ids=input_id, fields='screen_name')[0]
                self.friend_id = friend_user_data['id']
                self.friend_url_nickname = friend_user_data['screen_name']
                self.friend_first_name = friend_user_data['first_name']
                self.friend_last_name = friend_user_data['last_name']
                break
            except ConnectionError:
                time.sleep(0.1)
        while True:
            try:
                my_user_data = self.vk_api.method('users.get', fields='screen_name')[0]
                self.my_id = my_user_data['id']
                self.my_url_nickname = my_user_data['screen_name']
                self.my_first_name = my_user_data['first_name']
                self.my_last_name = my_user_data['last_name']
                break
            except ConnectionError:
                time.sleep(0.1)

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
    friend_id = 123
    parser = VkParser(friend_id=friend_id)
    parser.run()
