import os
import sys

from vk_messages import MessagesAPI
from vk_messages.vk_messages import Exception_MessagesAPI

import settings

if not os.path.exists('sessions/'):
    os.mkdir('sessions/')
try:
    vk_api = MessagesAPI(login=settings.VK_LOGIN, password=settings.VK_PASSWORD,
                         two_factor=settings.TWO_FACTOR, cookies_save_path='sessions/')
except Exception_MessagesAPI as e:
    print(f'Неверный пароль или {"имеется" if settings.TWO_FACTOR else "отсутствует"} двухфакторная аутентификация.', e)
    print('Передайте верные аргументы в экземпляр класса VkParser')
    sys.exit()
