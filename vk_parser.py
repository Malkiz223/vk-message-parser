import time

from vk import Vk


class VkParser(Vk):
    """
    Сканирует сообщения с указанным пользователем.
    """

    def __init__(self, friend_id, messages_api=Vk.messages_api):
        self.friend_id = friend_id
        self.all_json_messages = []
        self.SCAN_MESSAGES_PER_CALL = 200
        self.offset_scanned_messages = 0
        self.now_scanned = self.SCAN_MESSAGES_PER_CALL + self.offset_scanned_messages
        self.total_messages = messages_api.method('messages.getHistory', user_id=self.friend_id)['count']

    def parse_messages(self):
        """
        Обращается к API VK и вытягивает 200 сообщений.
        При каждом вызове offset смещается, позволяя запарсить следующие 200 сообщений.
        :return: None
        """
        try:
            json_messages = self.messages_api.method('messages.getHistory', user_id=self.friend_id,
                                                     count=self.SCAN_MESSAGES_PER_CALL,
                                                     rev=-1, offset=self.offset_scanned_messages)
            for message in json_messages['items']:
                self.all_json_messages.append(message)
            self.offset_scanned_messages += self.SCAN_MESSAGES_PER_CALL
        except AttributeError as err:
            print(f'Поймал {err}, продолжаю работу. Сообщения не потеряны, всё стабильно!')
        except BaseException as err:
            print(f'Поймали {err}')

    def print_progress_to_console(self):
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
            self.parse_messages()
            self.print_progress_to_console()
            time.sleep(0.1)  # Без задержки работает стабильно, но страшно