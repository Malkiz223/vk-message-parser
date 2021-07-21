import os
import time

from vk_messages import MessagesAPI

import settings

"""
Бот сканирует сообщения с указанным пользователем, хранит данные в памяти. Как досканировал - распарсить данные и 
закинуть их в базу. В базе сделать таблицу чата с названием (from my_id to friend_id)
Создать базу, таблицы будут создаваться автоматически

1) понять, что хочу написать (ввод и вывод данных на фласк?)
Сущность юзеров - ФИО, айдишник, ссылка на профиль? 
Сущность чата - все данные с месседжа

Таблица юзеров (users):
user_id (serial inside database), vk_id, vk_url_nickname (id1 / durov), first_name, last_name

Таблица сообщений (messages):
id - Primary_key (нет автоинкремента, парсить из message)
date (timestamp - int?) - время сообщения в секундах с начала эпохи
from_ID (int) - от кого пришло сообщение
text (text?) - текст сообщения, может быть пустым


Таблица фото
message_id foreign_key, url (sizes: [list[-1][dict]['url']]?)
photo {'date': 1537807124, 'from_id': 22491953, 'id': 579914, 'out': 1, 'peer_id': 183145350, 'text': '', 'conversation_message_id': 32, 'fwd_messages': [], 'important': False, 'random_id': 691669513, 'attachments': [{'type': 'photo', 'photo': {'album_id': -3, 'date': 1537807124, 'id': 456245348, 'owner_id': 22491953, 'has_tags': False, 'access_key': '6a4cf2208ecae08c15', 'sizes': [{'height': 130, 'url': 'https://sun9-18.userapi.com/impf/c845121/v845121029/fb752/TXH2d-ivKPw.jpg?size=102x130&quality=96&sign=a0439642c74c0189af00ffad54687d78&c_uniq_tag=C56nWy8sRX601mY0fERWcDXulL7mziPDKhUhngx06sM&type=album', 'type': 'm', 'width': 102}, {'height': 165, 'url': 'https://sun9-18.userapi.com/impf/c845121/v845121029/fb752/TXH2d-ivKPw.jpg?size=130x165&quality=96&sign=84ea0be9d40dde5ee197ca33d96049b4&c_uniq_tag=H_zztl_ilzPuh4tiTOwzryS5U_uUjF4UCEEwxANbFT8&type=album', 'type': 'o', 'width': 130}, {'height': 254, 'url': 'https://sun9-18.userapi.com/impf/c845121/v845121029/fb752/TXH2d-ivKPw.jpg?size=200x254&quality=96&sign=775749cea9cd56cac5bf4bf3453666ea&c_uniq_tag=0RGaizbqFkEaSbDfy9S_FsBiHit7fTJCx6nmB_aZ_OM&type=album', 'type': 'p', 'width': 200}, {'height': 406, 'url': 'https://sun9-18.userapi.com/impf/c845121/v845121029/fb752/TXH2d-ivKPw.jpg?size=320x406&quality=96&sign=aa2490f96bff59c9ca5d83fbf9c5d61a&c_uniq_tag=Lb3arvDt35xaJdyndBAN-KeK_Z0brhuvbAjvgAW9BnQ&type=album', 'type': 'q', 'width': 320}, {'height': 468, 'url': 'https://sun9-18.userapi.com/impf/c845121/v845121029/fb752/TXH2d-ivKPw.jpg?size=369x468&quality=96&sign=7c3474a0f46a17bfcfd1c8edf90710f8&c_uniq_tag=kGqmJbaxFP2fZZ5-GkOwgRQGDqXiFXAxLpjzaPtky6o&type=album', 'type': 'r', 'width': 369}, {'height': 75, 'url': 'https://sun9-18.userapi.com/impf/c845121/v845121029/fb752/TXH2d-ivKPw.jpg?size=59x75&quality=96&sign=4ca78b332c8c82def3eaf2019fe35af0&c_uniq_tag=oWgZPvkMUhJEnGiAmj5SM7eMW0M2Ig7WcSTZwzqM6HY&type=album', 'type': 's', 'width': 59}, {'height': 468, 'url': 'https://sun9-18.userapi.com/impf/c845121/v845121029/fb752/TXH2d-ivKPw.jpg?size=369x468&quality=96&sign=7c3474a0f46a17bfcfd1c8edf90710f8&c_uniq_tag=kGqmJbaxFP2fZZ5-GkOwgRQGDqXiFXAxLpjzaPtky6o&type=album', 'type': 'x', 'width': 369}], 'text': ''}}], 'is_hidden': False}

Таблица стикеров
message_id foreign_key, product_id, sticker_id, url_image (https://vk.com/sticker/1-{sticker_id}-512)?
sticker {'date': 1537809108, 'from_id': 183145350, 'id': 580186, 'out': 0, 'peer_id': 183145350, 'text': '', 'conversation_message_id': 267, 'fwd_messages': [], 'important': False, 'random_id': 0, 'attachments': [{'type': 'sticker', 'sticker': {'product_id': 185, 'sticker_id': 5973, 'images': [{'url': 'https://vk.com/sticker/1-5973-64', 'width': 64, 'height': 64}, {'url': 'https://vk.com/sticker/1-5973-128', 'width': 128, 'height': 128}, {'url': 'https://vk.com/sticker/1-5973-256', 'width': 256, 'height': 256}, {'url': 'https://vk.com/sticker/1-5973-352', 'width': 352, 'height': 352}, {'url': 'https://vk.com/sticker/1-5973-512', 'width': 512, 'height': 512}], 'images_with_background': [{'url': 'https://vk.com/sticker/1-5973-64b', 'width': 64, 'height': 64}, {'url': 'https://vk.com/sticker/1-5973-128b', 'width': 128, 'height': 128}, {'url': 'https://vk.com/sticker/1-5973-256b', 'width': 256, 'height': 256}, {'url': 'https://vk.com/sticker/1-5973-352b', 'width': 352, 'height': 352}, {'url': 'https://vk.com/sticker/1-5973-512b', 'width': 512, 'height': 512}]}}], 'is_hidden': False}

Таблица ссылок
message_id foreign_key, title (link: title), url (link: url)
link {'date': 1537834460, 'from_id': 183145350, 'id': 581224, 'out': 0, 'peer_id': 183145350, 'text': 'Там не прям до дома, а в ближайшей аптеки забирать можно всё что купил https://м.монастырёв.рф', 'conversation_message_id': 810, 'fwd_messages': [], 'important': False, 'random_id': 0, 'attachments': [{'type': 'link', 'link': {'url': 'https://?1?.?4??4??4??4??4??4??5??4??1?.?4??6?', 'title': 'Главная страница', 'caption': '', 'description': '', 'photo': {'album_id': -26, 'date': 1537834468, 'id': 456259963, 'owner_id': 2000057260, 'has_tags': False, 'sizes': [{'height': 480, 'url': 'https://sun9-10.userapi.com/impf/c846520/v846520488/f5ea2/y1LPTpC3peQ.jpg?size=1024x480&quality=96&sign=b951efa81eae12ddf986127e6c49038d&c_uniq_tag=6JP3SQL-60J27BP7BWkIFHnlZdLANEZaN-UQGfWNXmY&type=share', 'type': 'k', 'width': 1024}, {'height': 240, 'url': 'https://sun9-10.userapi.com/impf/c846520/v846520488/f5ea2/y1LPTpC3peQ.jpg?size=537x240&quality=96&crop=0,0,1024,458&sign=53bb7b9b6a130ade2a623f7c794d2b4c&c_uniq_tag=jTU_EuKxeSa9O_uiso-s2_AZNllQcN5_7CRZHetikQs&type=share', 'type': 'l', 'width': 537}, {'height': 130, 'url': 'https://sun9-10.userapi.com/impf/c846520/v846520488/f5ea2/y1LPTpC3peQ.jpg?size=130x80&quality=96&crop=122,0,780,480&sign=fa4a540518267b403b9b4afbcdce1af6&c_uniq_tag=60BBp7paJgmpgPlhYn6kSYDWkDb3AWVEPbijYU727nM&type=share', 'type': 'm', 'width': 130}, {'height': 130, 'url': 'https://sun9-69.userapi.com/c846520/v846520488/f5e9d/fAh0ibONYps.jpg', 'type': 'o', 'width': 130}, {'height': 200, 'url': 'https://sun9-10.userapi.com/impf/c846520/v846520488/f5ea2/y1LPTpC3peQ.jpg?size=260x140&quality=96&crop=66,0,891,480&sign=2cd6ecf6c635c9587f7ff476170dd5db&c_uniq_tag=DglKaR6Eh1WYId1z6r4Rdxbl05HqAWsSk-NOC4jOTqM&type=share', 'type': 'p', 'width': 200}, {'height': 320, 'url': 'https://sun9-22.userapi.com/c846520/v846520488/f5e9f/fk9taZfxvBA.jpg', 'type': 'q', 'width': 320}, {'height': 510, 'url': 'https://sun9-11.userapi.com/c846520/v846520488/f5ea0/xQ7-oRgyBjQ.jpg', 'type': 'r', 'width': 510}, {'height': 75, 'url': 'https://sun9-10.userapi.com/impf/c846520/v846520488/f5ea2/y1LPTpC3peQ.jpg?size=75x35&quality=96&sign=50c0cbd3fc5b5beb5051b45f148618b4&c_uniq_tag=Q8QZbdh4MeTnrjE9nc6NwWH0WH5aLAmEGZ955wHLk_4&type=share', 'type': 's', 'width': 75}, {'height': 604, 'url': 'https://sun9-10.userapi.com/impf/c846520/v846520488/f5ea2/y1LPTpC3peQ.jpg?size=150x80&quality=96&crop=62,0,900,480&sign=15ee9b88e9e3ad7a3c7ad0ec4c95c3d5&c_uniq_tag=bppsdQjE9J_jO9VyO14H0t6EXgZRP1KooxJF89svClA&type=share', 'type': 'x', 'width': 604}, {'height': 807, 'url': 'https://sun9-72.userapi.com/c846520/v846520488/f5e9b/USAuCpUP71k.jpg', 'type': 'y', 'width': 807}, {'height': 1024, 'url': 'https://sun9-5.userapi.com/c846520/v846520488/f5e9c/ftKl1XQ4U5E.jpg', 'type': 'z', 'width': 1024}], 'text': '', 'user_id': 100}}}], 'is_hidden': False}

Таблица видео
message_id foreign_key, description (video: description), duration (video: duration), image_url (video: image [list[-1][url]
video {'date': 1537894114, 'from_id': 183145350, 'id': 582083, 'out': 0, 'peer_id': 183145350, 'text': 'Кстати, там в клан чате тема была про плацкарт и пердеж. Не знаю как ты относишься ко всяким стендаперам, но посмотри, если будет время ) https://youtu.be/1K_x_Ut90Ks', 'conversation_message_id': 974, 'fwd_messages': [], 'important': False, 'random_id': 0, 'attachments': [{'type': 'video', 'video': {'access_key': '305de86c923ad8e833', 'can_add': 0, 'date': 1537894115, 'description': 'Саша делится мыслями о кошке, внезапном стояке и пердеже в спальне.\n\nВыкладываем отдельные выступления из второго выпуска проекта "Стендап Комики", как и обещали. \nВторой выпуск целиком тут:\nhttps://youtu.be/pw0E50amV-g\n\nПервый выпуск: https://youtu.be/thMYU7lTgxY\n\nСаша в инсте - https://www.instagram.com/sashamaloj\nСаша ВК - https://vk.com/id916772\n\nМы в соц сетях:\nhttps://vk.com/standupclubru\nhttps://instagram.com/standupclubru\nhttps://facebook.com/standupclubru\nhttps://twitter.com/standupclubru\nhttps://y', 'duration': 877, 'image': [{'height': 96, 'url': 'https://sun9-12.userapi.com/c851020/v851020864/f822/-9OBx-KIcms.jpg', 'width': 130, 'with_padding': 1}, {'height': 120, 'url': 'https://sun9-27.userapi.com/c851020/v851020864/f823/fAzyk_z6XLU.jpg', 'width': 160, 'with_padding': 1}, {'height': 240, 'url': 'https://sun9-83.userapi.com/c851020/v851020864/f824/6kn4VrzIBDs.jpg', 'width': 320, 'with_padding': 1}, {'height': 450, 'url': 'https://sun9-24.userapi.com/c851020/v851020864/f825/ErZEZwplVC0.jpg', 'width': 800, 'with_padding': 1}], 'id': 456239387, 'owner_id': 183145350, 'title': 'Саша Малой - Кошка/ старики/ пердёж', 'is_favorite': False, 'track_code': 'video_cc861b17RAQytzA9HmayMbAEMhrW31fyaPmSEVOSyQwBKsbCa-xGFwOPAwwqU4EEgFsG', 'type': 'video', 'views': 2, 'platform': 'YouTube'}}], 'is_hidden': False}

Таблица документов
message_id foreign_key, title (doc: title), ext - расширение (doc: ext), url (doc: url)
doc {'date': 1537997849, 'from_id': 22491953, 'id': 583790, 'out': 1, 'peer_id': 183145350, 'text': '', 'conversation_message_id': 1152, 'fwd_messages': [], 'important': False, 'random_id': 0, 'attachments': [{'type': 'doc', 'doc': {'id': 476545603, 'owner_id': 22491953, 'title': 'file.gif', 'size': 17983028, 'ext': 'gif', 'date': 1537997849, 'type': 3, 'url': 'https://vk.com/doc22491953_476545603?hash=fa4751b2e9ff16fee8&dl=GIZDIOJRHE2TG:1626646633:d3b587af049e790cde&api=1&no_preview=1', 'preview': {'photo': {'sizes': [{'src': 'https://sun9-12.userapi.com/c848132/u141844997/d4/-3/m_f24b83e7c4.jpg', 'width': 130, 'height': 100, 'type': 'm'}, {'src': 'https://sun9-19.userapi.com/c848132/u141844997/d4/-3/s_f24b83e7c4.jpg', 'width': 100, 'height': 75, 'type': 's'}, {'src': 'https://sun9-41.userapi.com/c848132/u141844997/d4/-3/x_f24b83e7c4.jpg', 'width': 604, 'height': 755, 'type': 'x'}, {'src': 'https://sun9-8.userapi.com/c848132/u141844997/d4/-3/o_f24b83e7c4.jpg', 'width': 520, 'height': 650, 'type': 'o'}, {'src': 'https://sun9-41.userapi.com/impf/c848132/u141844997/d4/-3/x_f24b83e7c4.jpg?size=230x288&quality=90&sign=a3d3c5fc9c7cbfe112093ad3966e81d2&c_uniq_tag=3tGIrKdxX7F_wTbNzEXCIKFUoEwF5vBkkoiV14cjpLE', 'width': 230, 'height': 288, 'type': 'i'}, {'src': 'https://sun9-41.userapi.com/impf/c848132/u141844997/d4/-3/x_f24b83e7c4.jpg?size=154x192&quality=90&sign=14856e729dd18c3ab341abc944711ad0&c_uniq_tag=D8Rbx1-lD_m_LvY0XsdZYYiDZmCrnvjqo55b5hK66Qg', 'width': 154, 'height': 192, 'type': 'd'}]}, 'video': {'src': 'https://vk.com/doc22491953_476545603?hash=fa4751b2e9ff16fee8&dl=GIZDIOJRHE2TG:1626646633:d3b587af049e790cde&api=1&mp4=1', 'width': 520, 'height': 650, 'file_size': 383595}}, 'access_key': '277175f01263a8f46d'}}], 'is_hidden': False}

Таблица аудио
message_id foreign_key, artist (audio: artist), title (audio: title), duration (audio: duration), url (audio: url для скачивания ЧЕГО? чепуха качается) 
audio {'date': 1538361131, 'from_id': 183145350, 'id': 589880, 'out': 0, 'peer_id': 183145350, 'text': 'Вот тебе колыбельная', 'conversation_message_id': 3340, 'fwd_messages': [], 'important': False, 'random_id': 0, 'attachments': [{'type': 'audio', 'audio': {'artist': 'Крики птиц', 'id': 456240506, 'owner_id': 2000142035, 'title': 'Выпь (неясыть)', 'duration': 23, 'is_explicit': False, 'is_focus_track': False, 'track_code': 'a83bc02dC2ipgVj1QkTYQc-KyysZI6blo02hUMOT', 'url': '', 'date': 1481104751, 'genre_id': 18, 'no_search': 1, 'content_restricted': 1, 'short_videos_allowed': False, 'stories_allowed': False, 'stories_cover_allowed': False}}], 'is_hidden': False}

Таблица звонков
message_id foreign_key, initiator_id (call: initiator_id), state (call: state), video (call: video)
call {'date': 1538668724, 'from_id': 22491953, 'id': 595054, 'out': 1, 'peer_id': 183145350, 'text': '', 'conversation_message_id': 5055, 'fwd_messages': [], 'important': False, 'random_id': 0, 'attachments': [{'type': 'call', 'call': {'initiator_id': 22491953, 'receiver_id': 183145350, 'state': 'canceled_by_initiator', 'time': 1538668724, 'video': False}}], 'is_hidden': False}

Таблица аудиосообщений
message_id foreign_key, duration (audio_message: duration), link_ogg (audio_message: link_ogg), link_mp3 (audio_message: link_mp3), transcription (перевод)
audio_message {'date': 1538992321, 'from_id': 183145350, 'id': 598885, 'out': 0, 'peer_id': 183145350, 'text': '', 'conversation_message_id': 5899, 'fwd_messages': [], 'important': False, 'random_id': 0, 'attachments': [{'type': 'audio_message', 'audio_message': {'id': 478133569, 'owner_id': 183145350, 'duration': 28, 'waveform': [0, 5, 5, 2, 6, 4, 5, 1, 3, 5, 8, 2, 4, 4, 1, 1, 1, 0, 1, 6, 8, 12, 5, 8, 6, 5, 6, 7, 5, 5, 3, 9, 23, 12, 12, 6, 9, 10, 8, 4, 4, 9, 5, 5, 1, 5, 3, 5, 1, 0, 1, 6, 7, 2, 5, 10, 6, 5, 5, 5, 7, 6, 4, 8, 8, 7, 8, 6, 7, 14, 7, 4, 4, 5, 10, 4, 1, 1, 1, 0, 6, 12, 9, 5, 6, 8, 24, 25, 21, 10, 9, 27, 31, 9, 3, 6, 9, 5, 4, 5, 10, 4, 8, 4, 5, 2, 3, 2, 1, 5, 7, 7, 3, 1, 5, 7, 1, 1, 1, 1, 7, 3, 4, 4, 4, 3, 2, 1], 'link_ogg': 'https://psv4.userapi.com/c852632//u183145350/audiomsg/d7/ff0a1ce144.ogg', 'link_mp3': 'https://psv4.userapi.com/c852632//u183145350/audiomsg/d7/ff0a1ce144.mp3', 'access_key': '04bc45b3fe39e60d40'}}], 'is_hidden': False, 'was_listened': True}

Таблица подарков
message_id foreign_key, gift_id (gift: id), gift_image (gift: thumb_256) (у стикеров ещё stickers_product_id: 127)
gift [{'type': 'gift', 'gift': {'id': 975, 'thumb_256': 'https://vk.com/images/gift/975/256.jpg', 'thumb_48': 'https://vk.com/images/gift/975/48.png', 'thumb_96': 'https://vk.com/images/gift/975/96.png'}}]
gift [{'type': 'gift', 'gift': {'id': -127, 'thumb_256': 'https://vk.com/sticker/4-127-256w', 'thumb_48': 'https://vk.com/sticker/4-127-48', 'thumb_96': 'https://vk.com/sticker/4-127-96', 'stickers_product_id': 127}}]

Таблица записей со стены
message_id foreign_key, from_id (wall: from_id), post_date (wall: date), post_type (wall: post_type), text (wall: text)
wall {'date': 1539279415, 'from_id': 183145350, 'id': 606878, 'out': 0, 'peer_id': 183145350, 'text': '', 'conversation_message_id': 7930, 'fwd_messages': [], 'important': False, 'random_id': 0, 'attachments': [{'type': 'wall', 'wall': {'id': 382623, 'from_id': -31480508, 'to_id': -31480508, 'date': 1539279300, 'post_type': 'post', 'text': 'Не пакет, а лучший друг\n\nКомментарии: pikabu.ru/story/_6208512', 'marked_as_ads': 0, 'attachments': [{'type': 'photo', 'photo': {'album_id': -7, 'date': 1539270942, 'id': 456275708, 'owner_id': -31480508, 'has_tags': False, 'access_key': '7a186708fb85ef9979', 'sizes': [{'height': 130, 'url': 'https://sun2-9.userapi.com/impf/c850328/v850328163/47c79/Mp2U58uAKpk.jpg?size=85x130&quality=96&sign=26e37a0b10dc9a030efdf78fd242fa88&c_uniq_tag=6WDQ9Tz1IUS6RKhOZli3h91_TfrcrySWtrJ3Xphpm8E&type=album', 'type': 'm', 'width': 85}, {'height': 199, 'url': 'https://sun2-9.userapi.com/impf/c850328/v850328163/47c79/Mp2U58uAKpk.jpg?size=130x199&quality=96&sign=294dc91b9fafa2c47fa2b168a895a9e3&c_uniq_tag=I6HDXnIVQoP--R-DzewOeF4LpiPFqzHPPrCQiWAVi2I&type=album', 'type': 'o', 'width': 130}, {'height': 306, 'url': 'https://sun2-9.userapi.com/impf/c850328/v850328163/47c79/Mp2U58uAKpk.jpg?size=200x306&quality=96&sign=65cc57392f5c182d6ce90f4e4bf0a355&c_uniq_tag=iwXoLPjmNp6-GceUmp-AInd2WrnmzlzNZeXkXmP7Zto&type=album', 'type': 'p', 'width': 200}, {'height': 489, 'url': 'https://sun2-9.userapi.com/impf/c850328/v850328163/47c79/Mp2U58uAKpk.jpg?size=320x489&quality=96&sign=6c1f436bbb41a24fae036cd6fe4e34e1&c_uniq_tag=Ug2AXLAGaF2CPbJzfx3HR1mMpTzbIEN04G4VD-dy9zY&type=album', 'type': 'q', 'width': 320}, {'height': 780, 'url': 'https://sun2-9.userapi.com/impf/c850328/v850328163/47c79/Mp2U58uAKpk.jpg?size=510x780&quality=96&sign=bb6f2923e975866fd2d05ba98f34863e&c_uniq_tag=MbTc0WUcSTNTiADYd8gQ3ZJ79K8JAR8rfpIVOrp1AXU&type=album', 'type': 'r', 'width': 510}, {'height': 75, 'url': 'https://sun2-9.userapi.com/impf/c850328/v850328163/47c79/Mp2U58uAKpk.jpg?size=49x75&quality=96&sign=06f749f631bf93dc594abe6edc81f22d&c_uniq_tag=aFuwqu3gJHWHWVQhzPilb4xjNOM8YCIusZBiypMhugk&type=album', 'type': 's', 'width': 49}, {'height': 604, 'url': 'https://sun2-9.userapi.com/impf/c850328/v850328163/47c79/Mp2U58uAKpk.jpg?size=395x604&quality=96&sign=0c3233497d3aba2ef5bccc3e381f32e5&c_uniq_tag=6bNbIwXaHeFL59VxPtEFx8BGOHqkQCHHvM7v7TmUKNo&type=album', 'type': 'x', 'width': 395}, {'height': 807, 'url': 'https://sun2-9.userapi.com/impf/c850328/v850328163/47c79/Mp2U58uAKpk.jpg?size=528x807&quality=96&sign=0a0aeb72fe21ae87956c8ba42275bd32&c_uniq_tag=CBINqYft38AmZ83qz2kxnqqNBfvxX7bB_fN0qvnzEZU&type=album', 'type': 'y', 'width': 528}, {'height': 1070, 'url': 'https://sun2-9.userapi.com/impf/c850328/v850328163/47c79/Mp2U58uAKpk.jpg?size=700x1070&quality=96&sign=078eddd4da92235a137285d0bc0c6ed7&c_uniq_tag=eiII4LTB1uvm98Lg77W71_jK1dRWtXqCkQRLPtrQwG0&type=album', 'type': 'z', 'width': 700}], 'text': '', 'user_id': 100}}, {'type': 'photo', 'photo': {'album_id': -7, 'date': 1539270942, 'id': 456275709, 'owner_id': -31480508, 'has_tags': False, 'access_key': '7a77345857dce740fd', 'sizes': [{'height': 130, 'url': 'https://sun2-9.userapi.com/impf/c845523/v845523163/10afb0/hf6PN0eFMNs.jpg?size=86x130&quality=96&sign=c8afb7adc81021d73d8dae763c40750d&c_uniq_tag=6Y5lgMChnR3vfkLN8bDK9aPrs24DX9HZAoyZE8f9E7A&type=album', 'type': 'm', 'width': 86}, {'height': 196, 'url': 'https://sun2-9.userapi.com/impf/c845523/v845523163/10afb0/hf6PN0eFMNs.jpg?size=130x196&quality=96&sign=1c8660b0cae7964d8adfdc9f5c989aca&c_uniq_tag=P8_ALji1j9mw-B3KIG-pLOMocT3XdQXmSfTRAw66zPg&type=album', 'type': 'o', 'width': 130}, {'height': 301, 'url': 'https://sun2-9.userapi.com/impf/c845523/v845523163/10afb0/hf6PN0eFMNs.jpg?size=200x301&quality=96&sign=fe569d922faf96e228f2336d0f83400f&c_uniq_tag=JrhDdvmOS2FWdl12BotvRLaZm1apf5RzVOCQ-PbZ_3U&type=album', 'type': 'p', 'width': 200}, {'height': 482, 'url': 'https://sun2-9.userapi.com/impf/c845523/v845523163/10afb0/hf6PN0eFMNs.jpg?size=320x482&quality=96&sign=6f06f0b68b2505aa51bd0cac8adeaf1f&c_uniq_tag=7wo9pw2E_W1l1qGkdtGeL23dOunbETNXp8nESC8aJ48&type=album', 'type': 'q', 'width': 320}, {'height': 768, 'url': 'https://sun2-9.userapi.com/impf/c845523/v845523163/10afb0/hf6PN0eFMNs.jpg?size=510x768&quality=96&sign=37f9ead693d0759708f816c76991e737&c_uniq_tag=FkmKNBLkcP5YKjcAb752OJa_YKLDCelOy_870Z3yKWw&type=album', 'type': 'r', 'width': 510}, {'height': 75, 'url': 'https://sun2-9.userapi.com/impf/c845523/v845523163/10afb0/hf6PN0eFMNs.jpg?size=50x75&quality=96&sign=dabf3ca2ae2edac0b9204766f7fef149&c_uniq_tag=NK-45xU0Wm-L0_VSEEUYLOrSqHjP1OP7h376OQBu2DY&type=album', 'type': 's', 'width': 50}, {'height': 604, 'url': 'https://sun2-9.userapi.com/impf/c845523/v845523163/10afb0/hf6PN0eFMNs.jpg?size=401x604&quality=96&sign=d15205bf889c067e9ded0ee57e76fdf3&c_uniq_tag=RdP7H6rOFwdAfkx8CR0uNKps4XcHuMiCkwct7QrkKGc&type=album', 'type': 'x', 'width': 401}, {'height': 807, 'url': 'https://sun2-9.userapi.com/impf/c845523/v845523163/10afb0/hf6PN0eFMNs.jpg?size=536x807&quality=96&sign=b067418b556e758c8e799c07718dcc15&c_uniq_tag=z9Ny9YYLpN6p05VuiGBcyoKnulF9F-XrZLroi_aO6_Y&type=album', 'type': 'y', 'width': 536}, {'height': 1054, 'url': 'https://sun2-9.userapi.com/impf/c845523/v845523163/10afb0/hf6PN0eFMNs.jpg?size=700x1054&quality=96&sign=1a202861b967656dfe18642d06e49f64&c_uniq_tag=EMpWHTO4UrZCATFvj7xIlTCN_GrWr7J5wkiLjU4FBHw&type=album', 'type': 'z', 'width': 700}], 'text': '', 'user_id': 100}}, {'type': 'link', 'link': {'url': 'https://pikabu.ru/story/otzyivyi_6208512', 'title': 'Отзывы...', 'description': 'Отзывы...', 'target': 'internal', 'photo': {'album_id': -2, 'date': 1539242434, 'id': 456241719, 'owner_id': 100, 'has_tags': False, 'sizes': [{'height': 480, 'url': 'https://sun9-13.userapi.com/c848616/v848616733/93da9/YJHYuOHYxuU.jpg', 'type': 'k', 'width': 1074}, {'height': 240, 'url': 'https://sun9-6.userapi.com/c848616/v848616733/93da8/tN_0RCuTtKM.jpg', 'type': 'l', 'width': 537}, {'height': 70, 'url': 'https://sun9-16.userapi.com/c848616/v848616733/93da5/fEYjw75lSng.jpg', 'type': 'm', 'width': 130}, {'height': 140, 'url': 'https://sun9-41.userapi.com/c848616/v848616733/93da7/wy-lnYOk-Yk.jpg', 'type': 'p', 'width': 260}, {'height': 39, 'url': 'https://sun9-59.userapi.com/c848616/v848616733/93da4/CY08yj6F_XE.jpg', 'type': 's', 'width': 75}, {'height': 80, 'url': 'https://sun9-50.userapi.com/c848616/v848616733/93da6/ZuUEs8imgUg.jpg', 'type': 'x', 'width': 150}], 'text': '', 'user_id': 100}, 'is_favorite': False}}], 'post_source': {'type': 'vk'}, 'comments': {'count': 0, 'can_post': 0, 'groups_can_post': True}, 'likes': {'count': 10059, 'user_likes': 0, 'can_like': 1, 'can_publish': 1}, 'reposts': {'count': 186, 'user_reposted': 0}, 'views': {'count': 348054}, 'is_favorite': False, 'access_key': 'ec6ad69299000fc7aa'}}], 'is_hidden': False}

Таблица граффити
message_id foreign_key, owner_id (graffiti: owner_id), url (graffiti: url), 
graffiti {'date': 1546827178, 'from_id': 183145350, 'id': 685265, 'out': 0, 'peer_id': 183145350, 'text': '', 'conversation_message_id': 47129, 'fwd_messages': [], 'important': False, 'random_id': 0, 'attachments': [{'type': 'graffiti', 'graffiti': {'id': 488419242, 'owner_id': 183145350, 'url': 'https://vk.com/doc183145350_488419242?hash=74b1917bf75e297cf4&dl=GIZDIOJRHE2TG:1626646772:2161100a79f5d70f3b&api=1&no_preview=1', 'width': 641, 'height': 720, 'access_key': '55e9a98c34bb11275d'}}], 'is_hidden': False}

Таблица сториз
message_id foreign_key, owner_id (story: owned_id), date (story: date), expires_at (story: expires_at), is_one_time (story: is_one_time -> True or False)  
story {'date': 1598458195, 'from_id': 183145350, 'id': 1084635, 'out': 0, 'peer_id': 183145350, 'text': '', 'conversation_message_id': 245133, 'fwd_messages': [], 'important': False, 'random_id': 0, 'attachments': [{'type': 'story', 'story': {'id': 456239081, 'owner_id': 183145350, 'can_see': 0, 'date': 1598458195, 'expires_at': 1598544595, 'is_one_time': False}}], 'is_hidden': False}


Опционально:
# FRONTEND 
Проект на Фласк, фронтенд - ввод логина и пароля в форму, нажатие кнопки отправки, если есть двухфакторка - 
возвращать поле с вводом кода двухфакторки, вводить и снова отправлять на сервер
Возвращать на фронт ответ вида "залогинились", и писать прогресс сканирования


# TODO программа ест 900 мегабайт оперативки за 300к+ сообщений. Смертельно? (можно грузить сразу всё в базу) 
"""


class VkParser:
    """
    Сканирует сообщения с указанным пользователем.
    """

    def __init__(self, friend_id):
        if not os.path.exists('sessions/'):
            os.mkdir('sessions/')
        self.vk_api = MessagesAPI(login=settings.VK_LOGIN, password=settings.VK_PASSWORD, two_factor=True,
                                  cookies_save_path='sessions/')

        self.messages = []
        self.SCAN_MESSAGES_PER_CALL = 200
        self.offset_scanned_messages = 0
        self.count_messages_was_printed = 0
        self.now_scanned = self.SCAN_MESSAGES_PER_CALL + self.offset_scanned_messages
        self.total_messages = self.vk_api.method('messages.getHistory', user_id=self.FRIEND_ID)['count']

    def get_messages_from_vk(self) -> None:
        """
        Обращается к API VK и вытягивает 200 сообщений, начиная с self.offset_scanned_messages (нулевое сообщение)
        При каждом вызове offset смещается, позволяя запарсить следующие 200 сообщений.
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
        Печатает в консоль прогресс сканирования сообщений. При дублировании значения пропускает печать
        """
        if self.now_scanned > self.total_messages:
            self.now_scanned = self.total_messages  # чтобы не превышало верхний предел сообщений
        if self.count_messages_was_printed < self.now_scanned:  # если уже печатало данное количество - скипаем
            print(f'Просканировано {self.now_scanned} из {self.total_messages} сообщений')
            self.count_messages_was_printed = self.now_scanned
        self.now_scanned = self.SCAN_MESSAGES_PER_CALL + self.offset_scanned_messages

    def save_messages_to_db(self) -> bool:
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

    def run(self) -> None:
        """
        Основная функция, запускает парсинг сообщений, выжидая между парсингом определённое время и печатая статистику.
        """
        while self.offset_scanned_messages <= self.total_messages:
            self.get_messages_from_vk()
            self.save_messages_to_db()
            self.print_parsing_progress_to_console()
            time.sleep(0.1)  # Без задержки работает стабильно, но вдруг начнут блокировать запросы


if __name__ == '__main__':
    friend_id = 123
    parser = VkParser(friend_id=friend_id)
    parser.run()
    # with open(f'messages_with_{friend_id}.txt', 'w') as file:
    #     for message2 in parser.all_json_messages:
    #         file.write(json.dumps(message2) + '\n')
