from datetime import datetime
from vk_messages import MessagesAPI
import settings
import time
import os


# TODO: записывать сообщения и подобную информацию в базу

class VkUser:
    """
    Создаёт инстанс класса пользователя, который принимает ID отправителя сообщения
    """

    def __init__(self, user_id):
        self.user_id = user_id
        self.FOLDER_NAME = f'Сообщения от {self.user_id}'

        self.statistics = {
            'messages': [],
            'stickers': [],
            'links': [],
            'gifs': [],
            'docs': [],
            'photos': [],
            'videos_counter': 0,
            'audio_messages': [],
            'walls_counter': 0,
            'audios': [],
            'gifts': [],
            'calls_counter': 0,
            'graffiti': [],
            'stories_counter': 0
        }

    def parse_message(self, message):
        if message['text']:
            text = message['text'].replace('\n', ' ')
            self.statistics['messages'].append(text)
        if message['attachments']:
            for attachment in message['attachments']:
                if attachment['type'] == 'sticker':
                    self.statistics['stickers'].append(attachment['sticker']['sticker_id'])
                elif attachment['type'] == 'link':
                    self.statistics['links'].append(attachment['link']['url'])
                elif attachment['type'] == 'doc':
                    if attachment['doc']['ext'] == 'gif':
                        self.statistics['gifs'].append(attachment['doc']['url'])
                    else:
                        self.statistics['docs'].append(attachment['doc']['title'] + ' ' + attachment['doc']['url'])
                elif attachment['type'] == 'photo':
                    self.statistics['photos'].append(attachment['photo']['sizes'][-1]['url'])
                elif attachment['type'] == 'video':
                    self.statistics['videos_counter'] += 1
                elif attachment['type'] == 'audio_message':
                    audio_date_in_seconds = message['date']
                    date_time = datetime.fromtimestamp(audio_date_in_seconds)
                    date_time = date_time.strftime("%d.%m.%Y ")
                    self.statistics['audio_messages'].append(
                        date_time + ' ' + str(attachment['audio_message']['duration']))
                elif attachment['type'] == 'wall':
                    self.statistics['walls_counter'] += 1
                elif attachment['type'] == 'audio':
                    self.statistics['audios'].append(attachment['audio']['title'])
                elif attachment['type'] == 'gift':
                    self.statistics['gifts'].append(attachment['gift']['thumb_256'])
                elif attachment['type'] == 'call':
                    self.statistics['calls_counter'] += 1
                elif attachment['type'] == 'graffiti':
                    self.statistics['graffiti'].append(attachment['graffiti']['url'])
                elif attachment['type'] == 'story':
                    self.statistics['stories_counter'] += 1
                else:
                    print(attachment)

    def print_statistics(self):
        print(f'Статистика от пользователя id{self.user_id}:\n{len(self.statistics["messages"])}')

    def write_statistics_to_files(self):
        if not os.path.exists(self.FOLDER_NAME):
            os.mkdir(self.FOLDER_NAME)
        for filename in self.statistics.keys():
            if self.statistics[filename]:
                with open(f'{self.FOLDER_NAME}\\{filename}.txt', 'a', encoding='UTF-8') as f:
                    try:
                        f.write('\n'.join([str(message) for message in self.statistics[f'{filename}']]))
                    except TypeError:
                        f.write(str(self.statistics[f'{filename}']))


class VkParser:
    """
    Авторизируется в VK по указанным логину и паролю, есть поддержка двухфакторной авторизации.
    Сканирует сообщения с указанным пользователем, создаёт инстансы класса VkUser
    """

    def __init__(self, dialogue_id, login=settings.login, password=settings.password, two_factor=True):
        self.dialogue_id = dialogue_id
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

        self.TOTAL_MESSAGES = self.messages_api.method('messages.getHistory', user_id=self.dialogue_id)['count']

    def run(self):
        number_of_scan_cycles = self.TOTAL_MESSAGES // self.SCAN_MESSAGES_PER_CALL + 1
        for _ in range(number_of_scan_cycles):
            json_messages = self.messages_api.method('messages.getHistory', user_id=self.dialogue_id,
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
    my_id = 123
    friend_id = 123
    my_vk = VkUser(my_id)
    vk_friend = VkUser(friend_id)

    vk_parse = VkParser(dialogue_id=friend_id)
    vk_parse.run()
