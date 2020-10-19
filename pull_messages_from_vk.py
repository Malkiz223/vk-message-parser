from datetime import datetime
from vk_messages import MessagesAPI
import settings
import time
import os

# TODO: записывать сообщения и подобную информацию в базу
# TODO: запись контекстным менеджером? (актуально с базой?)
# TODO: можно добавлять статистику в словари
'''
При инициализации класса нужно создавать два экземпляра (свой и чужой).
Инстанс должен иметь имя папки, создавать их при инициализации.
'''


class VkUser:
    """
    Создаёт инстанс класса пользователя, который принимает ID отправителя сообщения
    """

    def __init__(self, user_id):
        self.user_id = user_id

        self.statistics = {
            'message_counter': 0,
            'sticker_counter': 0,
            'link_counter': 0,
        }

        self.FOLDER_NAME = f'Сообщения от {self.user_id}'

        if not os.path.exists(self.FOLDER_NAME):
            os.mkdir(self.FOLDER_NAME)

    def parse_message(self, message):

        if message['text']:
            text = message['text'].replace('\n', ' ')
            f = open(fr'{self.FOLDER_NAME}\Сообщения.txt', 'a', encoding='UTF-8')
            f.write(text + '\n')

        if message['attachments']:
            for attachment in message['attachments']:
                if attachment['type'] == 'sticker':
                    f = open(fr'{self.FOLDER_NAME}\Стикеры.txt', 'a', encoding='UTF-8')
                    f.write(str(attachment['sticker']['sticker_id']) + '\n')
                    f.close()

                elif attachment['type'] == 'link':
                    f = open(fr'{self.FOLDER_NAME}\Ссылки.txt', 'a', encoding='UTF-8')
                    f.write(attachment['link']['url'] + '\n')
                    f.close()
                elif attachment['type'] == 'doc':
                    if attachment['doc']['ext'] == 'gif':
                        f = open(fr'{self.FOLDER_NAME}\Гифки.txt', 'a', encoding='UTF-8')
                        f.write(attachment['doc']['url'] + '\n')
                        f.close()
                    else:
                        f = open(fr'{self.FOLDER_NAME}\Документы.txt', 'a', encoding='UTF-8')
                        f.write(attachment['doc']['title'] + ' ' + attachment['doc']['url'] + '\n')
                        f.close()
                elif attachment['type'] == 'photo':
                    f = open(fr'{self.FOLDER_NAME}\Фото.txt', 'a', encoding='UTF-8')
                    f.write(attachment['photo']['sizes'][-1]['url'] + '\n')
                    f.close()
                elif attachment['type'] == 'video':
                    f = open(fr'{self.FOLDER_NAME}\Видео.txt', 'a', encoding='UTF-8')
                    f.write(attachment['video']['title'] + '\n')
                    f.close()
                elif attachment['type'] == 'audio_message':
                    audio_date_in_seconds = message['date']
                    date_time = datetime.fromtimestamp(audio_date_in_seconds)
                    date_time = date_time.strftime("%d.%m.%Y ")
                    f = open(fr'{self.FOLDER_NAME}\Аудиосообщения.txt', 'a', encoding='UTF-8')
                    f.write(date_time + str(attachment['audio_message']['duration']) + '\n')
                    f.close()
                elif attachment['type'] == 'wall':
                    f = open(fr'{self.FOLDER_NAME}\Записи на стене.txt', 'a', encoding='UTF-8')
                    f.write('1\n')
                    f.close()
                elif attachment['type'] == 'audio':
                    f = open(fr'{self.FOLDER_NAME}\Аудиозаписи.txt', 'a', encoding='UTF-8')
                    f.write(attachment['audio']['title'] + '\n')
                    f.close()
                elif attachment['type'] == 'gift':
                    f = open(fr'{self.FOLDER_NAME}\Подарки.txt', 'a', encoding='UTF-8')
                    f.write(attachment['gift']['thumb_256'] + '\n')
                    f.close()
                elif attachment['type'] == 'call':
                    f = open(fr'{self.FOLDER_NAME}\Звонки.txt', 'a', encoding='UTF-8')
                    f.write(attachment['call']['state'] + '\n')
                    f.close()
                elif attachment['type'] == 'graffiti':
                    f = open(fr'{self.FOLDER_NAME}\Граффити.txt', 'a', encoding='UTF-8')
                    f.write(attachment['graffiti']['url'] + '\n')
                    f.close()
                elif attachment['type'] == 'story':
                    f = open(fr'{self.FOLDER_NAME}\Сториз.txt', 'a', encoding='UTF-8')
                    f.write('1\n')
                    f.close()
                else:
                    print(attachment)


class VkParser:
    """
    Авторизируется в VK по указанным логину и паролю, есть поддержка двухфакторной авторизации.
    Сканирует сообщения с указанным пользователем, создаёт инстансы класса VkUser
    """

    def __init__(self, dialogue_id, login=settings.login, password=settings.password, two_factor=True):
        self.user_id = dialogue_id
        self.login = login
        self.password = password
        self.two_factor = two_factor
        self.SCAN_MESSAGES_PER_CALL = 200
        self.offset_scanned_messages = 0
        self.now_scanned = self.SCAN_MESSAGES_PER_CALL + self.offset_scanned_messages

        if not os.path.exists('sessions/'):
            os.mkdir('sessions/')

        # Start session
        self.messages_api = MessagesAPI(login=self.login, password=self.password, two_factor=self.two_factor,
                                        cookies_save_path='sessions/')

        self.TOTAL_MESSAGES = self.messages_api.method('messages.getHistory', user_id=self.user_id)['count']

    def run(self):
        number_of_scan_cycles = self.TOTAL_MESSAGES // self.SCAN_MESSAGES_PER_CALL + 1
        for _ in range(number_of_scan_cycles):
            json_messages = self.messages_api.method('messages.getHistory', user_id=self.user_id,
                                                     count=self.SCAN_MESSAGES_PER_CALL,
                                                     rev=-1, offset=self.offset_scanned_messages)
            for message in json_messages['items']:
                if message['from_id'] == my_id:
                    my_vk.parse_message(message)
                if message['from_id'] == friend_id:
                    vk_friend.parse_message(message)

            print(f'Просканировано {self.now_scanned} из {self.TOTAL_MESSAGES} сообщений')

            self.offset_scanned_messages += self.SCAN_MESSAGES_PER_CALL
            self.now_scanned = self.SCAN_MESSAGES_PER_CALL + self.offset_scanned_messages
            if self.now_scanned > self.TOTAL_MESSAGES:
                self.now_scanned = self.TOTAL_MESSAGES
            time.sleep(0.2)


if __name__ == '__main__':
    my_id = 22491953
    friend_id = 183145350
    my_vk = VkUser(my_id)
    vk_friend = VkUser(friend_id)

    vk_parse = VkParser(dialogue_id=friend_id)
    vk_parse.run()
