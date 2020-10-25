import os
from collections import Counter
from datetime import datetime

from vk import Vk


class VkUser(Vk):
    """Пользователь ВК, участвующий в переписке. Может печатать статистику в консоль и в отдельные файлы.
    :arg user_id (int): ID пользователя
    :arg messages_api (class): API VK
    """

    def __init__(self, user_id, messages_api=Vk.messages_api):
        self.user_id = user_id
        while True:
            try:
                self.first_name = messages_api.method('users.get', user_ids=self.user_id, name_case='gen')[0]['first_name']
                self.last_name = messages_api.method('users.get', user_ids=self.user_id, name_case='gen')[0]['last_name']
                break
            except AttributeError:
                print(f'Ошибка при входе в сеть. Но всё в порядке, работаем дальше')
        self.FOLDER_NAME = f'Сообщения от {self.first_name} {self.last_name}'

        self.statistics = {
            'messages': [],
            'stickers': [],
            'stickers_counter': Counter(),
            'links': [],
            'gifs': [],
            'docs': [],
            'photos': [],
            'videos_counter': 0,
            'audio_messages': [],
            'duration_of_audio_messages': [],
            'walls_counter': 0,
            'audios': [],
            'gifts': [],
            'gifted_stickers': 0,
            'calls_counter': 0,
            'graffiti': [],
            'stories_counter': 0
        }

    def collect_statistics(self, message):
        """
        Принимает JSON на 200 сообщений, разбивает сообщение на части и кладёт эти части в определённые словари
        Собирает статистику по различным метрикам - текст, стикеры, ссылки, ссылки на фото, на видео и так далее
        :param message: Строка формата JSON
        :return: None
        """
        if message['text']:
            text = message['text'].replace('\n', ' ')
            self.statistics['messages'].append(text)
        if message['attachments']:
            for attachment in message['attachments']:
                if attachment['type'] == 'sticker':
                    self.statistics['stickers'].append(attachment['sticker']['sticker_id'])
                    self.statistics['stickers_counter'][attachment['sticker']['sticker_id']] += 1
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
                    self.statistics['duration_of_audio_messages'].append(attachment['audio_message']['duration'])
                elif attachment['type'] == 'wall':
                    self.statistics['walls_counter'] += 1
                elif attachment['type'] == 'audio':
                    self.statistics['audios'].append(attachment['audio']['title'])
                elif attachment['type'] == 'gift':
                    self.statistics['gifts'].append(attachment['gift']['thumb_256'])
                    if 'sticker' in attachment['gift']['thumb_256'] or '10001' in attachment['gift']['thumb_256'] \
                            or '10002' in attachment['gift']['thumb_256']:
                        self.statistics['gifted_stickers'] += 1
                elif attachment['type'] == 'call':
                    self.statistics['calls_counter'] += 1
                elif attachment['type'] == 'graffiti':
                    self.statistics['graffiti'].append(attachment['graffiti']['url'])
                elif attachment['type'] == 'story':
                    self.statistics['stories_counter'] += 1
                else:
                    print(attachment)

    def print_statistics_to_console(self):
        """
        Печатает в консоль отформатированную статистику, собранную в self.statistics
        :return: None
        """
        print('@' * 34)
        print(f'Статистика от {self.first_name} {self.last_name}:')
        if self.statistics['messages']:
            print(f'Отправлено сообщений: {len(self.statistics["messages"])}')
        if self.statistics['stickers']:
            print(f'Отправлено стикеров: {len(self.statistics["stickers"])}')
            print(f'Самые популярные стикеры:')
            for sticker_id, count in self.statistics["stickers_counter"].most_common(3):
                print(f'https://vk.com/sticker/1-{sticker_id}-512b использовался {count} раз')
        if self.statistics['links']:
            print(f'Отправлено ссылок: {len(self.statistics["links"])}')
        if self.statistics['gifs']:
            print(f'Отправлено гифок: {len(self.statistics["gifs"])}')
        if self.statistics['docs']:
            print(f'Отправлено документов: {len(self.statistics["docs"])}')
        if self.statistics['photos']:
            print(f'Отправлено изображений: {len(self.statistics["photos"])}')
        if self.statistics['videos_counter']:
            print(f'Отправлено видео: {self.statistics["videos_counter"]}')
        if self.statistics['audio_messages']:
            print(f'Отправлено аудиосообщений: {len(self.statistics["audio_messages"])}')
            print(f'Продолжительность аудиосообщений: {sum(self.statistics["duration_of_audio_messages"])} сек.')
            if len(self.statistics['audio_messages']) > 1:
                print(f'Самое долгое аудиосообщение длилось {max(self.statistics["duration_of_audio_messages"])} сек.')
        if self.statistics['walls_counter']:
            print(f'Отправлено записей со стен: {self.statistics["walls_counter"]}')
        if self.statistics['audios']:
            print(f'Отправлено песен: {len(self.statistics["audios"])}')
        if self.statistics['gifts']:
            print(f'Отправлено подарков: {len(self.statistics["gifts"])}', end='')
            if self.statistics['gifted_stickers']:
                print(f', из которых стикеров - {self.statistics["gifted_stickers"]}')
            else:
                print()
        if self.statistics['calls_counter']:
            print(f'Звонков совершено: {self.statistics["calls_counter"]}')
        if self.statistics['graffiti']:
            print(f'Отправлено граффити: {len(self.statistics["graffiti"])}')
        if self.statistics['stories_counter']:
            print(f'Отправлено историй: {self.statistics["stories_counter"]}')
        print()

    def write_statistics_to_files(self):
        """
        Пишет все значения self.statistics в отдельные файлы по категориям
        :return: None
        """
        if not os.path.exists(self.FOLDER_NAME):
            os.mkdir(self.FOLDER_NAME)
        for filename in self.statistics.keys():
            if self.statistics[filename]:
                with open(f'{self.FOLDER_NAME}\\{filename}.txt', 'a', encoding='UTF-8') as f:
                    try:
                        f.write('\n'.join([str(message) for message in self.statistics[f'{filename}']]))
                    except TypeError:
                        f.write(str(self.statistics[f'{filename}']))
