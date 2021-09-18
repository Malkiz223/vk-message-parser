import os
import sys

# Авторизация происходит либо по паролю, либо по access token
# Не обязателен, если будет введён логин и пароль. Токен можно получить здесь: https://vkhost.github.io/
VK_ACCESS_TOKEN: str = os.getenv('VK_ACCESS_TOKEN')  # '4e224ec586965787f254c01873933312d941e919b1c399f33168208a96ac9c0'

# Логин с паролем не требуются, если введён access token. Он имеет высший приоритет в работе программы
VK_LOGIN: str = os.getenv('VK_LOGIN')  # 'admin@gmail.com'
VK_PASSWORD: str = os.getenv('VK_PASSWORD')  # 'qwerty123'
# Сохранять ли сессию в файл, чтобы при повторном запуске не стучаться на сервер аутентификации
SAVE_SESSION: bool = True  # True / False

if not (all([VK_LOGIN, VK_PASSWORD])) and not VK_ACCESS_TOKEN:
    sys.exit('Не получили связку логин+пароль и нет токена')

# Настройки PostgreSQL
POSTGRES_USER: str = 'postgres'  # пользователь по умолчанию
POSTGRES_PASSWORD: str = os.getenv('POSTGRESQL_PASSWORD')  # пароль для подключения к пользователю
POSTGRES_DBNAME: str = os.getenv('POSTGRES_VK_DBNAME', 'vk_messages')  # название созданной вами базы
POSTGRES_HOST: str = '127.0.0.1'  # localhost, ip по умолчанию
POSTGRES_PORT: int = 5432  # порт по умолчанию
