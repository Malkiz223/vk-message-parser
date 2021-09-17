import os
import sys

import vk_api

from settings import VK_LOGIN, VK_PASSWORD, VK_ACCESS_TOKEN

sessions_folder_name = 'sessions'


def two_factor_auth_handler():
    """
    При двухфакторной аутентификации вызывается эта функция. Требуется ввести код для входа. Обычно его отправляет
    личным сообщением Администрация ВКонтакте, либо ввести код из Google Authenticator, если он подключен.
    """
    key = input("Enter authentication code: ")  # Код двухфакторной аутентификации
    remember_device = True  # Сохранять сессию в файл?
    if remember_device:
        if not os.path.exists(sessions_folder_name):
            os.mkdir(sessions_folder_name)
    return key, remember_device


def get_vk_session_by_password() -> vk_api.VkApi:
    """
    Для авторизации в ВК требуются логин и пароль, получаемые из settings.py.
    app_id требуется для работы API. Лишь некоторым "приложениям" разрешены многие методы API. VK Admin - одно из них.
    Смена версии API может привести к изменениям получаемых данных, что приведёт к проблемам.
    config_filename - необязательный параметр. Если убрать, файл сессии будет иметь имя "vk_config.v2.json" и лежать
    в корневой папке проекта.
    """

    vk_session = vk_api.VkApi(
        login=VK_LOGIN,
        password=VK_PASSWORD,
        auth_handler=two_factor_auth_handler,  # функция для обработки двухфакторной аутентификации
        config_filename=f'{sessions_folder_name}/session_{VK_LOGIN}.json',
        app_id=6121396,  # 6121396 - ID VK Admin. 2685278 - ID Kate Mobile
        api_version='5.131'
    )
    try:
        vk_session.auth()
        return vk_session
    except vk_api.AuthError as error:
        sys.exit(error)


def get_vk_session_by_token() -> vk_api.VkApi:
    vk_session = vk_api.VkApi(
        token=VK_ACCESS_TOKEN,
        app_id=6121396,  # 6121396 - ID VK Admin. 2685278 - ID Kate Mobile
        api_version='5.131'
    )
    return vk_session


if VK_ACCESS_TOKEN:
    vk_session = get_vk_session_by_token()
elif VK_LOGIN and VK_PASSWORD:
    vk_session = get_vk_session_by_password()
else:
    sys.exit('Не смогли получить сессию ни через логин с паролем, ни через токен')
