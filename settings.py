import os
import sys

# авторизация происходит либо по паролю, либо по токену
VK_LOGIN: str = os.getenv('VK_LOGIN')  # 'admin@gmail.com'
VK_PASSWORD: str = os.getenv('VK_PASSWORD')  # 'qwerty123'
# опционально, если получили логин и пароль
VK_ACCESS_TOKEN: str = os.getenv('VK_ACCESS_TOKEN')  # токен можно получить здесь: https://vkhost.github.io/

if not (all([VK_LOGIN, VK_PASSWORD])) and not VK_ACCESS_TOKEN:
    sys.exit('Не получили связку логин+пароль и нет токена')

# Настройки PostgreSQL
POSTGRES_USER: str = 'postgres'  # пользователь по умолчанию
POSTGRES_PASSWORD: str = os.getenv('POSTGRESQL_PASSWORD')  # пароль для подключения к пользователю
POSTGRES_DBNAME: str = os.getenv('POSTGRES_VK_DBNAME', 'vk_messages')  # название созданной вами базы
POSTGRES_HOST: str = '127.0.0.1'  # localhost, ip по умолчанию
POSTGRES_PORT: int = 5432  # порт по умолчанию
