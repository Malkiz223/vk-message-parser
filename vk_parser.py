import os
import time

from vk_messages import MessagesAPI

import settings


class VkParser:
    """
    Сканирует сообщения с указанным пользователем.
    :arg friend_id (int): ID собеседника в VK
    :arg messages_api (class): API VK
    """

    def __init__(self, friend_id):
        if not os.path.exists('sessions/'):
            os.mkdir('sessions/')
        self.messages_api = MessagesAPI(login=settings.VK_LOGIN, password=settings.VK_PASSWORD, two_factor=True,
                                        cookies_save_path='sessions/')
        self.FRIEND_ID = friend_id
        self.all_json_messages = []
        self.SCAN_MESSAGES_PER_CALL = 200
        self.offset_scanned_messages = 0
        self.now_scanned = self.SCAN_MESSAGES_PER_CALL + self.offset_scanned_messages
        self.total_messages = self.messages_api.method('messages.getHistory', user_id=self.FRIEND_ID)['count']

    def get_messages_from_vk(self):
        """
        Обращается к API VK и вытягивает 200 сообщений.
        При каждом вызове offset смещается, позволяя запарсить следующие 200 сообщений.
        :return: None
        """
        try:
            json_messages = self.messages_api.method('messages.getHistory', user_id=self.FRIEND_ID,
                                                     count=self.SCAN_MESSAGES_PER_CALL,
                                                     rev=-1, offset=self.offset_scanned_messages)
            for message in json_messages['items']:
                self.all_json_messages.append(message)
            self.offset_scanned_messages += self.SCAN_MESSAGES_PER_CALL
        except AttributeError:
            pass
        except BaseException:
            pass

    def print_parsing_progress_to_console(self):
        """
        Печатает в консоль прогресс сканирования сообщений.
        :return: None
        """
        if self.now_scanned > self.total_messages:
            self.now_scanned = self.total_messages
        print(f'Просканировано {self.now_scanned} из {self.total_messages} сообщений')
        self.now_scanned = self.SCAN_MESSAGES_PER_CALL + self.offset_scanned_messages

    def run(self):
        """
        Основная функция, запускает парсинг сообщений, выжидая между парсингом определённое время и печатая статистику.
        :return: None
        """
        while self.offset_scanned_messages <= self.total_messages:
            self.get_messages_from_vk()
            self.print_parsing_progress_to_console()
            time.sleep(0.1)  # Без задержки работает стабильно, но вдруг начнут блокировать запросы
