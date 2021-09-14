import os

VK_LOGIN: str = os.getenv('VK_LOGIN')  # 'admin@gmail.com'
VK_PASSWORD: str = os.getenv('VK_PASSWORD')  # 'qwerty123'

# Настройки PostgreSQL
POSTGRES_USER: str = 'postgres'  # пользователь по умолчанию
POSTGRES_PASSWORD: str = os.getenv('POSTGRESQL_PASSWORD')  # пароль для подключения к пользователю
POSTGRES_DBNAME: str = os.getenv('POSTGRES_VK_DBNAME', 'vk_messages')  # название созданной вами базы
POSTGRES_HOST: str = '127.0.0.1'  # localhost, ip по умолчанию
POSTGRES_PORT: int = 5432  # порт по умолчанию
