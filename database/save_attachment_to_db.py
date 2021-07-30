from datetime import datetime


def save_photo_to_db(cursor, message_id: int, attachment: dict) -> None:
    image_url: str = attachment['sizes'][-1]['url']
    cursor.execute('INSERT INTO photos (message_id, image_url) VALUES (%s, %s)',
                   (message_id, image_url,))


def save_sticker_to_db(cursor, message_id: int, attachment: dict) -> None:
    product_id: int = attachment['product_id']
    sticker_id: int = attachment['sticker_id']
    image_url: str = f'https://vk.com/sticker/1-{sticker_id}-512'  # 512 ширина/высота стикера, есть 64/128/256/512
    cursor.execute('INSERT INTO stickers (message_id, product_id, sticker_id, image_url) '
                   'VALUES (%s, %s, %s, %s)', (message_id, product_id, sticker_id, image_url,))


def save_link_to_db(cursor, message_id: int, attachment: dict) -> None:
    title: str = attachment['title']
    url: str = attachment['url']
    cursor.execute('INSERT INTO links (message_id, title, url) VALUES (%s, %s, %s)',
                   (message_id, title, url))


def save_video_to_db(cursor, message_id: int, attachment: dict) -> None:
    """
    У видео нет ссылки, даже если оно ведёт на YouTube. Через API его достать нельзя.
    """
    description: str = attachment.get('description')
    duration: int = attachment['duration']
    image_url: str = attachment['image'][-1]['url']
    cursor.execute(
        'INSERT INTO videos (message_id, description, duration, image_url) VALUES (%s, %s, %s, %s)',
        (message_id, description, duration, image_url,))


def save_doc_to_db(cursor, message_id: int, attachment: dict) -> None:
    title: str = attachment['title']
    extension: str = attachment['ext']
    url: str = attachment['url']
    cursor.execute('INSERT INTO docs (message_id, title, extension, url) VALUES (%s, %s, %s, %s)',
                   (message_id, title, extension, url,))


def save_audio_to_db(cursor, message_id: int, attachment: dict) -> None:
    artist: str = attachment['artist']
    title: str = attachment['title']
    duration: int = attachment['duration']
    url: str = attachment['url']  # url аудио позволяет скачать какую-то непонятную фигню формата .m3u8
    cursor.execute(
        'INSERT INTO audios (message_id, artist, title, duration, url) VALUES (%s, %s, %s, %s, %s)',
        (message_id, artist, title, duration, url,))


def save_audio_message_to_db(cursor, message_id: int, attachment: dict) -> None:
    duration: str = attachment['duration']
    link_ogg: str = attachment['link_ogg']
    link_mp3: str = attachment['link_mp3']
    transcript: str = attachment.get('transcript')  # транскрипт отсутствует у старых сообщений, положится null
    cursor.execute(
        'INSERT INTO audio_messages (message_id, duration, link_ogg, link_mp3, transcript) VALUES ('
        '%s, %s, %s, %s, %s)', (message_id, duration, link_ogg, link_mp3, transcript,))


def save_call_to_db(cursor, message_id: int, attachment: dict) -> None:
    initiator_id: int = attachment['initiator_id']
    state: str = attachment['state']
    video: bool = attachment['video']
    cursor.execute('INSERT INTO calls (message_id, initiator_id, state, video) VALUES (%s, %s, %s, %s)',
                   (message_id, initiator_id, state, video,))


def save_gift_to_db(cursor, message_id: int, attachment: dict) -> None:
    gift_id: int = attachment['id']
    image_url: str = attachment['thumb_256']
    stickers_product_id: int = attachment.get('stickers_product_id')
    cursor.execute('INSERT INTO gifts (message_id, gift_id, image_url, stickers_product_id) VALUES ('
                   '%s, %s, %s, %s)', (message_id, gift_id, image_url, stickers_product_id,))


def save_wall_to_db(cursor, message_id: int, attachment: dict) -> None:
    from_id: int = attachment['from_id']
    post_date_gmt: datetime = datetime.fromtimestamp(attachment['date'])
    post_type: str = attachment['post_type']
    text: str = attachment['text']
    cursor.execute('INSERT INTO walls (message_id, from_id, post_date_gmt, post_type, text) VALUES ('
                   '%s, %s, %s, %s, %s)', (message_id, from_id, post_date_gmt, post_type, text,))


def save_graffiti_to_db(cursor, message_id: int, attachment: dict) -> None:
    image_url: str = attachment['url']
    cursor.execute('INSERT INTO graffiti (message_id, image_url) VALUES (%s, %s)',
                   (message_id, image_url,))


def save_story_to_db(cursor, message_id: int, attachment: dict) -> None:
    can_see: int = attachment['can_see']
    story_date_gmt: datetime = datetime.fromtimestamp(attachment['date'])
    expires_at_gmt: datetime = datetime.fromtimestamp(attachment['expires_at'])
    is_one_time: bool = attachment['is_one_time']  # на моей практике здесь всегда лежит False
    cursor.execute(
        'INSERT INTO stories (message_id, can_see, story_date_gmt, expires_at_gmt, is_one_time) '
        'VALUES (%s, %s, %s, %s, %s)',
        (message_id, can_see, story_date_gmt, expires_at_gmt, is_one_time,))
