import os

from vk_messages import MessagesAPI

import settings


class Vk:
    """
    Суперкласс, имеющий доступ к API VK, хранящий сессию в отдельной папочке
    """
    if not os.path.exists('sessions/'):
        os.mkdir('sessions/')

    messages_api = MessagesAPI(login=settings.login, password=settings.password, two_factor=True,
                               cookies_save_path='sessions/')
