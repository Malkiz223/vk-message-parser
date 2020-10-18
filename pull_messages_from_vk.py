from datetime import datetime
from vk_messages import MessagesAPI
import settings
import time
import os

# TODO: сделать два экземпляра класса - для меня и для собеседника.
# TODO: записывать сообщения и подобную информацию в базу
# TODO: создавать папки циклом? (актуально с базой?)
# TODO: запись контекстным менеджером? (актуально с базой?)
# TODO: можно добавлять статистику в словари
'''
При инициализации класса нужно создавать два экземпляра (свой и чужой).
Инстанс должен иметь имя папки, создавать их при инициализации.
'''


# 1 - как называть репозиторий на гитхабе? (куда кликать, чтобы адекватно там залогиниться и создать репозиторий?:D)
# 2 - нормальный ли вариант - выносить инициализирующие параметры в абстрактный класс?

class Vk:
    try:
        os.mkdir('sessions/')
    except FileExistsError:
        pass

    def __init__(self, user_id, login, password, two_factor=True):
        self.user_id = user_id
        self.login = login
        self.password = password
        self.two_factor = two_factor
        self.SCAN_MESSAGES_PER_CALL = 200
        self.offset_scanned_messages = 0
        self.now_scanned = self.SCAN_MESSAGES_PER_CALL + self.offset_scanned_messages

        self.messages = MessagesAPI(login=self.login, password=self.password, two_factor=self.two_factor,
                                    cookies_save_path='sessions/')
        self.TOTAL_MESSAGES = self.messages.method('messages.getHistory', user_id=self.user_id)['count']
        self.MY_FOLDER_NAME = f'{self.user_id} - исходящие'
        self.HIS_FOLDER_NAME = f'{self.user_id} - входящие'

        self.my_messages = 0

        try:
            os.mkdir(self.MY_FOLDER_NAME)
        except FileExistsError:
            pass
        try:
            os.mkdir(self.HIS_FOLDER_NAME)
        except FileExistsError:
            pass

    def parse_message(self, message):
        if message['from_id'] == self.user_id:  # если сообщение не от меня
            folder_name = self.HIS_FOLDER_NAME
        else:
            folder_name = self.MY_FOLDER_NAME

        if message['text']:
            text = message['text'].replace('\n', ' ')
            f = open(fr'{folder_name}\Сообщения.txt', 'a', encoding='UTF-8')
            f.write(text + '\n')
            self.my_messages += 1

        if message['attachments']:
            for attachment in message['attachments']:
                if attachment['type'] == 'sticker':
                    f = open(fr'{folder_name}\Стикеры.txt', 'a', encoding='UTF-8')
                    f.write(str(attachment['sticker']['sticker_id']) + '\n')
                    f.close()

                elif attachment['type'] == 'link':
                    f = open(fr'{folder_name}\Ссылки.txt', 'a', encoding='UTF-8')
                    f.write(attachment['link']['url'] + '\n')
                    f.close()
                elif attachment['type'] == 'doc':
                    if attachment['doc']['ext'] == 'gif':
                        f = open(fr'{folder_name}\Гифки.txt', 'a', encoding='UTF-8')
                        f.write(attachment['doc']['url'] + '\n')
                        f.close()
                    else:
                        f = open(fr'{folder_name}\Документы.txt', 'a', encoding='UTF-8')
                        f.write(attachment['doc']['title'] + ' ' + attachment['doc']['url'] + '\n')
                        f.close()
                elif attachment['type'] == 'photo':
                    f = open(fr'{folder_name}\Фото.txt', 'a', encoding='UTF-8')
                    f.write(attachment['photo']['sizes'][-1]['url'] + '\n')
                    f.close()
                elif attachment['type'] == 'video':
                    f = open(fr'{folder_name}\Видео.txt', 'a', encoding='UTF-8')
                    f.write(attachment['video']['title'] + '\n')
                    f.close()
                elif attachment['type'] == 'audio_message':
                    audio_date_in_seconds = message['date']
                    date_time = datetime.fromtimestamp(audio_date_in_seconds)
                    date_time = date_time.strftime("%d.%m.%Y ")
                    f = open(fr'{folder_name}\Аудиосообщения.txt', 'a', encoding='UTF-8')
                    f.write(date_time + str(attachment['audio_message']['duration']) + '\n')
                    f.close()
                elif attachment['type'] == 'wall':
                    f = open(fr'{folder_name}\Записи на стене.txt', 'a', encoding='UTF-8')
                    f.write('1\n')
                    f.close()
                elif attachment['type'] == 'audio':
                    f = open(fr'{folder_name}\Аудиозаписи.txt', 'a', encoding='UTF-8')
                    f.write(attachment['audio']['title'] + '\n')
                    f.close()
                elif attachment['type'] == 'gift':
                    f = open(fr'{folder_name}\Подарки.txt', 'a', encoding='UTF-8')
                    f.write(attachment['gift']['thumb_256'] + '\n')
                    f.close()
                elif attachment['type'] == 'call':
                    f = open(fr'{folder_name}\Звонки.txt', 'a', encoding='UTF-8')
                    f.write(attachment['call']['state'] + '\n')
                    f.close()
                elif attachment['type'] == 'graffiti':
                    f = open(fr'{folder_name}\Граффити.txt', 'a', encoding='UTF-8')
                    f.write(attachment['graffiti']['url'] + '\n')
                    f.close()
                elif attachment['type'] == 'story':
                    f = open(fr'{folder_name}\Сториз.txt', 'a', encoding='UTF-8')
                    f.write('1\n')
                    f.close()
                else:
                    print(attachment)

    def run(self):
        scan_cycles = self.TOTAL_MESSAGES // self.SCAN_MESSAGES_PER_CALL + 1
        for _ in range(scan_cycles):

            history = self.messages.method('messages.getHistory', user_id=self.user_id,
                                           count=self.SCAN_MESSAGES_PER_CALL,
                                           rev=-1, offset=self.offset_scanned_messages)
            print(f'Просканировано {self.now_scanned} из {self.TOTAL_MESSAGES} сообщений')
            for message in history['items']:
                self.parse_message(message)

            self.offset_scanned_messages += self.SCAN_MESSAGES_PER_CALL
            self.now_scanned = self.SCAN_MESSAGES_PER_CALL + self.offset_scanned_messages
            if self.now_scanned > self.TOTAL_MESSAGES:
                self.now_scanned = self.TOTAL_MESSAGES
            time.sleep(0.2)


if __name__ == '__main__':
    vk = Vk(user_id=183145350, login=settings.login, password=settings.password)
    vk.run()
